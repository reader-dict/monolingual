from __future__ import annotations

import shutil
import subprocess
import uuid
import zipfile
from collections import deque
from logging import getLogger
from typing import Any

from jinja2 import Template

from wikidict import constants
from wikidict.converters import BaseFormat, Summary
from wikidict.converters.stardict import TEMPLATE

GROUP_XHTML_TEMPLATE = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"
      xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" />
</head>
<body>
<mbp:frameset>
{group_contents}
</mbp:frameset>
</body>
</html>
"""

ENTRY_TEMPLATE = """
<idx:entry scriptable="yes" spell="yes">
<idx:orth>{headword}{variants}
</idx:orth>
<br/>{definition}
</idx:entry>
<hr/>
""".strip()

INFL_TEMPLATE = """
<idx:infl>
{variants}
</idx:infl>
""".strip()

IFORM_TEMPLATE = """<idx:iform value="{variant}" exact="yes" />"""

OPF_TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<package unique-identifier="uid">
<metadata>
<dc-metadata xmlns:dc="http://purl.org/metadata/dublin_core">
<dc:Title>{title}</dc:Title>
<dc:Language>{source_lang}</dc:Language>
<dc:Identifier id="uid">{identifier}</dc:Identifier>
<dc:Creator>{creator}</dc:Creator>
<dc:Rights>{copyright}</dc:Rights>
<dc:description>{description}</dc:description>
<dc:Subject BASICCode="REF008000">Dictionaries</dc:Subject>
</dc-metadata>
<x-metadata>
<output encoding="utf-8"></output>
<DictionaryInLanguage>{source_lang}</DictionaryInLanguage>
<DictionaryOutLanguage>{target_lang}</DictionaryOutLanguage>
</x-metadata>
</metadata>
<manifest>
{manifest}
</manifest>
<spine>
{spine}
</spine>
</package>
""".strip()


log = getLogger(__name__)


class MobiFormat(Summary, BaseFormat):
    """Save the data into a MobiPocket file."""

    target_format = "mobi"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.mobi.zip"
    template = TEMPLATE

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.tmp_dir = self.output_dir / self.target_format
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.oebps_dir = self.tmp_dir / "OEBPS"
        self.oebps_dir.mkdir(exist_ok=True)

        self.max_file_size = 2**18
        self.uuid = str(uuid.uuid4()).replace("-", "")
        self.current_size = 0
        self.group_contents: list[str] = []
        self.manifest_items: list[str] = []
        self.spine_items: list[str] = []
        self.file_index = 0

    def render_word(self, template: Template, **kwargs: Any) -> str:
        rendered = super().render_word(template, **kwargs)
        formatted = self.format_entry(kwargs["word"], rendered, kwargs["variants"])
        size = len(formatted.encode("utf-8"))

        if self.current_size + size > self.max_file_size and self.group_contents:
            self.save_xhtml_group()

        self.group_contents.append(formatted)
        self.current_size += size
        return formatted

    def save_xhtml_group(self) -> None:
        name = f"group_{self.file_index}.xhtml"
        file = self.oebps_dir / name
        html_body = "\n".join(self.group_contents)
        file.write_text(GROUP_XHTML_TEMPLATE.format(group_contents=html_body), encoding="utf-8")
        item_id = f"item_{self.file_index}"
        self.manifest_items.append(f'<item id="{item_id}" href="{name}" media-type="application/xhtml+xml"/>')
        self.spine_items.append(f'<itemref idref="{item_id}"/>')

        self.file_index += 1
        self.group_contents.clear()
        self.current_size = 0

    def format_entry(self, word: str, definition: str, variants_list: list[str]) -> str:
        if variants_list:
            variants = "\n" + INFL_TEMPLATE.format(
                variants="\n".join(IFORM_TEMPLATE.format(variant=var) for var in variants_list)
            )
        else:
            variants = ""

        return ENTRY_TEMPLATE.format(headword=word, definition=definition, variants=variants)

    def process(self) -> None:
        words = self.words
        for word in sorted(words):
            deque(self.handle_word(word, words), maxlen=0)  # Exhaust the generator

        if self.group_contents:
            self.save_xhtml_group()

        description = "\n".join(
            [
                "Clean, optimized dictionary generated from Wiktionary data.",
                f"Contains {self.words_count + self.variants_count:,} entries with{'' if self.include_etymology else 'out'} etymologies.\n",
                self.description,
            ]
        )
        opf_content = OPF_TEMPLATE.format(
            title=self.title(),
            source_lang=self.effective_lang_src(),
            target_lang=self.effective_lang_dst(),
            identifier=self.uuid,
            manifest="\n".join(self.manifest_items),
            spine="\n".join(self.spine_items),
            description=description,
            creator=constants.PROJECT,
            copyright=self.description,
        )

        stem = self.title().lower().replace(" ", "-")
        if not self.include_etymology:
            stem += "-noetym"
        opf_path = self.oebps_dir / f"{stem}.opf"
        opf_path.write_text(opf_content, encoding="utf-8")

        mobi_file = opf_path.with_suffix(".mobi")
        process = subprocess.Popen(
            [
                constants.MOBIPOCKET_TOOL,
                opf_path.name,
                "-gen_ff_mobi7",
                "-dont_append_source",
                # "-c2",
                "-o",
                mobi_file.name,
            ],
            cwd=self.oebps_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = process.communicate()
        id_ = self.id()
        for line in output.decode(encoding="utf-8").splitlines():
            log.info("[%s] %s", id_, line)
        for line in error.decode(encoding="utf-8").splitlines():
            log.info("[%s] %s", id_, line)

        assert mobi_file.is_file()

        file = self.dictionary_file(self.final_file)
        with zipfile.ZipFile(file, mode="w", compression=zipfile.ZIP_DEFLATED) as fh:
            fh.write(mobi_file, arcname=mobi_file.name)
            assert fh.testzip() is None, fh.testzip()

        self.summary(file)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
