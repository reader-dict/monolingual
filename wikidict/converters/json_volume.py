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
            log.info("[%s] Skipped etymology-free volumes.", self.id())
            return

        output_base = self.dictionary_file(self.output_file)
        output_base.mkdir(exist_ok=True, parents=True)

        volumes = self._create_volumes(output_base)
        self._save_manifest(volumes, output_base)

        log.info(
            "[%s] Generated %s volumes with %s total words (max size: %dKB) in %s",
            self.id(),
            f"{len(volumes):,}",
            f"{self.words_count:,}",
            self.max_volume_size_kb,
            timedelta(seconds=monotonic() - self.start),
        )

    def _format_word_data(self, word: str, details: Word) -> dict[str, Any]:
        """Format a single word's data for JSON output."""
        if not details.definitions:
            if details.reverse_variants:
                return {self.KEY_REDIRECT: details.reverse_variants[0]}
            if details.variants:
                return {self.KEY_REDIRECT: details.variants[0]}
            return {}

        word_data: dict[str, Any] = {}
        if defs := details.definitions:
            word_data[self.KEY_DEFINITION] = self._format_definitions(defs)
        if etyms := details.etymology:
            word_data[self.KEY_ETYMOLOGY] = self._format_etymology(etyms)
        if prons := details.pronunciations:
            word_data[self.KEY_PRONUNCIATION] = utils.convert_pronunciation(prons).strip()
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

    def _create_volumes(self, output_dir: Path) -> list[dict[str, Any]]:
        """Split words into volumes based on size."""
        volumes = []
        current_volume_words: dict[str, dict[str, Any]] = {}
        current_volume_size = 0
        volume_num = 0
        first_word = ""

        for word, details in sorted(self.words.items()):
            if not (word_data := self._format_word_data(word, details)):
                continue

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
        with gzip.open(filepath, "wt", encoding="utf-8") as f:
            f.write(json.dumps(volume_data, ensure_ascii=False, separators=(",", ":")))

        file_size = filepath.stat().st_size  # Get actual compressed file size

        log.info(
            "[%s] Volume %s: %r → %r (%s words, %sKB)",
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
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
