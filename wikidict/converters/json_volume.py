from __future__ import annotations

import gzip
import json
import logging
import shutil
from collections.abc import Sequence
from datetime import timedelta
from time import monotonic
from typing import Any

from jinja2 import Template

from wikidict.converters import BaseFormat
from wikidict.stubs import Definition

log = logging.getLogger(__name__)

MAX_VOLUME_SIZE_KB = 1024  # Target volume size in KB
KEY_DEFINITION = "d"
KEY_ETYMOLOGY = "e"
KEY_PRONUNCIATION = "p"
KEY_REDIRECT = "r"
KEY_VARIANT = "v"


class JSONVolumeFormat(BaseFormat):
    """Save the data into JSON volumes with range-based splitting."""

    target_format = "jsonvolume"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.max_volume_bytes = MAX_VOLUME_SIZE_KB * 1024
        self.volumes: list[dict[str, Any]] = []
        self.current_volume_words: dict[str, dict[str, Any]] = {}
        self.current_volume_size = 0
        self.volume_num = 0
        self.first_word = ""
        self.tmp_dir = self.output_dir / self.target_format
        self.rendered_entries: list[tuple[str, dict[str, Any]]] = []

    def render_word(self, template: Template, **kwargs: Any) -> str:
        data: dict[str, Any] = {KEY_DEFINITION: self._format_definitions(kwargs["definitions"])}
        if etyms := kwargs["etymologies"]:
            data[KEY_ETYMOLOGY] = self._format_etymology(etyms)
        if prons := kwargs["pronunciation"]:
            data[KEY_PRONUNCIATION] = prons.strip()

        self.rendered_entries.append((kwargs["word"], data))
        self.rendered_entries.extend((variant, {KEY_REDIRECT: kwargs["word"]}) for variant in kwargs["variants"])

        self.words_count += 1
        self.variants_count += len(kwargs["variants"])

        return ""

    def process(self) -> None:
        """Generate the JSON volumes."""
        if not self.include_etymology:
            log.info("[%s] Skipped etymology-free volumes.", self.id())
            return

        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir()

        words = self.words
        for word in words:
            # Exhaust the generator
            for _ in self.handle_word(word, words):
                pass

        for word, data in sorted(self.rendered_entries, key=lambda kv: kv[0]):
            # Estimate size of adding this word
            size = self._estimate_json_size({word: data})

            # If this is the first word in the volume, track it
            if not self.current_volume_words:
                self.first_word = word

            # Check if adding this word would exceed the limit
            elif self.current_volume_size + size > self.max_volume_bytes:
                self._save_volume()
                self.first_word = word

            # Add word to current volume
            self.current_volume_words[word] = data
            self.current_volume_size += size

        # Save the last volume
        if self.current_volume_words:
            self._save_volume()

        self._save_manifest()

        log.info(
            "[%s] Generated %s volumes with %s words + %s variants = %s entries (max size: %dKB) in %s",
            self.id(),
            f"{len(self.volumes):,}",
            f"{self.words_count:,}",
            f"{self.variants_count:,}",
            f"{self.words_count + self.variants_count:,}",
            MAX_VOLUME_SIZE_KB,
            timedelta(seconds=monotonic() - self.start),
        )

    def _format_definitions(self, definitions: Sequence[Any]) -> dict[str, list[Any]]:
        """Format definitions preserving nested structure."""
        return {
            pos: [self._format_definition_item(definition) for definition in pos_definitions]
            for pos, pos_definitions in definitions
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

    def _save_volume(self) -> None:
        """Save a single volume and return its metadata."""
        words = self.current_volume_words
        last_word = list(words.keys())[-1]
        volume_data = {"words": words}
        file = self.tmp_dir / f"vol-{self.volume_num:08d}.json.gz"

        # Write gzipped JSON
        with gzip.open(file, "wt", encoding="utf-8") as f:
            f.write(json.dumps(volume_data, ensure_ascii=False, separators=(",", ":")))

        file_size = file.stat().st_size  # Get actual compressed file size

        log.info(
            "[%s] Volume %s: %r → %r (%s words, %sKB)",
            self.id(),
            f"{self.volume_num:08d}",
            self.first_word,
            last_word,
            f"{len(words):,}",
            f"{file_size / 1024:.1f}",
        )

        self.volumes.append(
            {
                "filename": file.name,
                "volumeNum": self.volume_num,
                "firstWord": self.first_word,
                "lastWord": last_word,
                "wordCount": len(words),
                "sizeBytes": file_size,
            }
        )

        # Start new volume
        self.volume_num += 1
        self.current_volume_words.clear()
        self.current_volume_size = 0

    def _save_manifest(self) -> None:
        """Generate and save the manifest.json file."""
        manifest = {
            "version": "3.0",
            "totalVolumes": len(self.volumes),
            "totalWords": self.words_count + self.variants_count,
            "maxVolumeSizeKB": MAX_VOLUME_SIZE_KB,
            "volumes": [
                {
                    "file": vol["filename"],
                    "volumeNum": vol["volumeNum"],
                    "firstWord": vol["firstWord"],
                    "lastWord": vol["lastWord"],
                    "wordCount": vol["wordCount"],
                    "sizeBytes": vol["sizeBytes"],
                }
                for vol in self.volumes
            ],
        }

        manifest_path = self.tmp_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
