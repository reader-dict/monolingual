from __future__ import annotations

import gzip
import json
import logging
from datetime import timedelta
from pathlib import Path
from time import monotonic
from typing import Any

from wikidict import utils
from wikidict.converters import BaseFormat
from wikidict.stubs import Definition, Definitions, Word

log = logging.getLogger(__name__)


class JSONVolumeFormat(BaseFormat):
    """Save the data into JSON volumes with range-based splitting."""

    output_file = "jsonvolume-{lang_src}-{lang_dst}{etym_suffix}"
    max_volume_size_kb = 1024  # Target volume size in KB
    max_volume_bytes = max_volume_size_kb * 1024

    KEY_DEFINITION = "d"
    KEY_ETYMOLOGY = "e"
    KEY_PRONUNCIATION = "p"
    KEY_REDIRECT = "r"
    KEY_VARIANT = "v"

    def process(self) -> None:
        """Generate the JSON volumes."""
        if not self.include_etymology:
            return

        output_base = self.dictionary_file(self.output_file)
        output_base.mkdir(exist_ok=True, parents=True)

        # Get all words sorted alphabetically
        all_words = sorted(
            (word, details)
            for word, details in self.words.items()
            # Skip variant-only words without definitions
            if not details.is_variant or details.definitions
        )

        log.info(
            "[%s] Processing %s words into volumes (max %dKB each)",
            self.id(),
            f"{len(all_words):,}",
            self.max_volume_size_kb,
        )

        # Split into volumes
        volumes = self._create_volumes(all_words, output_base)

        # Generate and save manifest
        self._save_manifest(volumes, output_base)

        # Summary
        log.info(
            "[%s] Generated %s volumes with %s total words (max size: %dKB)",
            self.id(),
            f"{len(volumes):,}",
            f"{len(all_words):,}",
            self.max_volume_size_kb,
        )

    def _format_word_data(self, word: str, details: Word) -> dict[str, Any]:
        """Format a single word's data for JSON output."""
        if not details.definitions:
            if details.reverse_variants:
                return {self.KEY_REDIRECT: details.reverse_variants[0]}
            return {self.KEY_REDIRECT: details.variants[0]}

        word_data: dict[str, Any] = {}
        if defs := self._format_definitions(details.definitions):
            word_data[self.KEY_DEFINITION] = defs
        if etyms := self._format_etymology(details.etymology):
            word_data[self.KEY_ETYMOLOGY] = etyms
        if prons := utils.convert_pronunciation(details.pronunciations):
            word_data[self.KEY_PRONUNCIATION] = prons
        if variants := self.variants.get(word):
            word_data[self.KEY_VARIANT] = sorted(variants)

        return word_data

    def _format_definitions(self, definitions: Definitions) -> dict[str, list[Any]]:
        """Format definitions preserving nested structure."""
        return {
            pos: [self._format_definition_item(definition) for definition in pos_definitions]
            for pos, pos_definitions in definitions.items()
        }

    def _format_definition_item(self, definition: Definition) -> str | list[Any]:
        """Recursively format a definition item, preserving nesting."""
        if isinstance(definition, str):
            return definition
        return [self._format_definition_item(sub_def) for sub_def in definition]

    def _format_etymology(self, etymology: list[Definition]) -> str | list[Any]:
        """Format etymology preserving nested structure."""
        if not etymology:
            return ""

        if len(etymology) == 1 and isinstance(etymology[0], str):
            return etymology[0]

        result: list[str | list[Any]] = []
        for etym in etymology:
            if isinstance(etym, str):
                result.append(etym)
            else:
                result.append([self._format_definition_item(sub_etym) for sub_etym in etym])

        return result

    def _estimate_json_size(self, data: dict[str, dict[str, Any]]) -> int:
        """Estimate the size of JSON data in bytes."""
        json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return len(json_str.encode("utf-8"))

    def _create_volumes(self, all_words: list[tuple[str, Word]], output_dir: Path) -> list[dict[str, Any]]:
        """Split words into volumes based on size."""
        volumes = []
        current_volume_words: dict[str, dict[str, Any]] = {}
        current_volume_size = 0
        volume_num = 0
        first_word = ""

        for word, details in all_words:
            word_data = self._format_word_data(word, details)

            # Estimate size of adding this word
            test_entry = {word: word_data}
            word_size = self._estimate_json_size(test_entry)

            # If this is the first word in the volume, track it
            if not current_volume_words:
                first_word = word

            # Check if adding this word would exceed the limit
            if current_volume_size + word_size > self.max_volume_bytes and current_volume_words:
                # Save current volume
                last_word = list(current_volume_words.keys())[-1]
                volume_info = self._save_volume(volume_num, current_volume_words, first_word, last_word, output_dir)
                volumes.append(volume_info)

                # Start new volume
                volume_num += 1
                current_volume_words = {}
                current_volume_size = 0
                first_word = word

            # Add word to current volume
            current_volume_words[word] = word_data
            current_volume_size += word_size
            self.words_count += 1

        # Save the last volume
        if current_volume_words:
            last_word = list(current_volume_words.keys())[-1]
            volume_info = self._save_volume(volume_num, current_volume_words, first_word, last_word, output_dir)
            volumes.append(volume_info)

        return volumes

    def _save_volume(
        self,
        volume_num: int,
        words: dict[str, Any],
        first_word: str,
        last_word: str,
        output_dir: Path,
    ) -> dict[str, Any]:
        """Save a single volume and return its metadata."""
        volume_data = {"words": words}

        filename = f"vol-{volume_num:08d}.json.gz"
        filepath = output_dir / filename

        # Write gzipped JSON
        json_content = json.dumps(volume_data, ensure_ascii=False, separators=(",", ":"))
        with gzip.open(filepath, "wt", encoding="utf-8") as f:
            f.write(json_content)

        file_size = filepath.stat().st_size  # Get actual compressed file size

        log.info(
            "[%s] Volume %s: %s → %s (%s words, %sKB)",
            self.id(),
            f"{volume_num:08d}",
            first_word,
            last_word,
            f"{len(words):,}",
            f"{file_size / 1024:.1f}",
        )

        return {
            "filename": filename,
            "volumeNum": volume_num,
            "firstWord": first_word,
            "lastWord": last_word,
            "wordCount": len(words),
            "sizeBytes": file_size,
        }

    def _save_manifest(self, volumes: list[dict[str, Any]], output_dir: Path) -> None:
        """Generate and save the manifest.json file."""
        manifest = {
            "version": "3.0",
            "totalVolumes": len(volumes),
            "totalWords": self.words_count,
            "maxVolumeSizeKB": self.max_volume_size_kb,
            "volumes": [
                {
                    "file": vol["filename"],
                    "volumeNum": vol["volumeNum"],
                    "firstWord": vol["firstWord"],
                    "lastWord": vol["lastWord"],
                    "wordCount": vol["wordCount"],
                    "sizeBytes": vol["sizeBytes"],
                }
                for vol in volumes
            ],
        }

        manifest_path = output_dir / "manifest.json"
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        log.info("[%s] Generated manifest.json with %d volumes", self.id(), len(volumes))
        self.compute_checksum(manifest_path)

    def summary(self, file: Path) -> None:
        """Override summary to handle directory output."""
        log.info(
            "[%s] Generated JSON volumes with %s words in %s",
            self.id(),
            f"{self.words_count:,}",
            timedelta(seconds=monotonic() - self.start),
        )
        log.info(
            "[%s] Finished the conversion with %s words, and %s variants, as expected.",
            self.id(),
            f"{len(self.words):,}",
            f"{len(self.variants):,}",
        )
