from __future__ import annotations

import gzip
import shutil
from collections import defaultdict
from functools import partial
from logging import getLogger
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from jinja2 import Template
from marisa_trie import Trie

from wikidict import constants, utils
from wikidict.converters import BaseFormat, Summary
from wikidict.stubs import Groups, Words

log = getLogger(__name__)

# Note: we issue a line break (`<br/>`) at the end of etymologies to workaround a visual glitch when there are multiple results for a word:
#       the next word would'nt be properly visually separated from the previous word's etymology.
# Note: We cannot remove the space before the slash in `<a name="{{ word }}" />` because
#       the Kobo lookup regexp for Japanese words is `(<a name="WORD" />.*</w>)`.
WORD_TPL_KOBO = Template(
    """\
<w><p><a name="{{ headword }}" /><b>{{ word }}</b>{{ pronunciation }}<br/><br/>
{%- for pos, pos_definitions in definitions -%}
    {%- if pos.find("|") > -1 -%}
    <b>{{ pos.split("|", 1)[0] }}</b> <i>{{ pos.split("|", 1)[1] }}</i>
    {%- else -%}
    <b>{{ pos }}</b>
    {%- endif -%}
    <ol>
    {%- for definition in pos_definitions -%}
        {%- if definition is string -%}
            <li>{{ definition }}</li>
        {%- else -%}
            <ol style="list-style-type:lower-alpha">
            {%- for sub_def in definition -%}
                {%- if sub_def is string -%}
                    <li>{{ sub_def }}</li>
                {%- else -%}
                    <ol style="list-style-type:lower-roman">
                        {%- for sub_sub_def in sub_def -%}
                            <li>{{ sub_sub_def }}</li>
                        {%- endfor -%}
                    </ol>
                {%- endif -%}
            {%- endfor -%}
            </ol>
        {%- endif -%}
    {%- endfor -%}
    </ol>
{%- endfor -%}
{%- if etymologies -%}
    {%- for etymology in etymologies -%}
        {%- if etymology is string -%}
            <p>{{ etymology }}</p>
        {%- else -%}
            <ol>
            {%- for sub_etymology in etymology -%}
                <li>{{ sub_etymology }}</li>
            {%- endfor -%}
            </ol>
        {%- endif -%}
    {%- endfor -%}
    <br/>
{%- endif -%}
</p>
{%- if variants -%}
    <var>
    {%- for variant in variants -%}
        <variant name="{{ variant }}"/>
    {%- endfor -%}
    </var>
{%- endif -%}
</w>
""",
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


class DictHtmlFormat(Summary, BaseFormat):
    """Save the data into Kobo-specific ZIP file."""

    output_file = "dicthtml-{lang_src}-{lang_dst}{etym_suffix}.zip"
    template = WORD_TPL_KOBO

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.prefix_exceptions: list[str] = []

    def process(self) -> None:
        self.groups = self.make_groups(self.words)
        self.save()

    def craft_index(self, wordlist: list[str], output_dir: Path) -> Path:
        """Generate the special file "words" that is an index of all words."""
        log.info("[%s] Crafting index", self.id())
        output = output_dir / "words"
        trie = Trie(wordlist)
        trie.save(output)
        return output

    def craft_prefix_exceptions(self, output_dir: Path) -> Path:
        r"""Generate the special file "prefix_exceptions" that is a list of group word redirections in the format "INFLECTION\tGROUP_PREFIX."""
        log.info("[%s] prefix_exceptions: %s", self.id(), f"{len(self.prefix_exceptions):,}")
        output = output_dir / "prefix_exceptions"
        trie = Trie(self.prefix_exceptions)
        trie.save(output)
        return output

    def make_groups(self, words: Words) -> Groups:
        """Group word by prefix."""
        log.info("[%s] Making groups", self.id())
        groups: Groups = defaultdict(dict)
        guess_prefix = partial(utils.guess_prefix, locale=self.effective_lang_src())
        for word, details in words.items():
            groups[guess_prefix(word)][word] = details
        return groups

    def save(self) -> None:  # sourcery skip: extract-method
        """
        Format of resulting dicthtml-LOCALE-LOCALE.zip:

            aa.html
            ab.html
            ..
            words

        Each word must be stored into the file {letter1}{letter2}.html (gzip content).
        """

        # Clean-up before we start
        tmp_dir = self.output_dir / "tmp"
        shutil.rmtree(tmp_dir, ignore_errors=True)
        tmp_dir.mkdir()

        # Files to add to the final archive
        to_compress: list[Path] = []

        # First, create individual HTML files
        wordlist: list[str] = []
        for prefix, words in self.groups.items():
            if html := self.save_html(prefix, words, tmp_dir):
                to_compress.append(html)
            wordlist.extend(words.keys())

        # Then create the special "words" file
        to_compress.append(self.craft_index(wordlist, tmp_dir))

        # Also create the special "prefix_exceptions" file
        if self.prefix_exceptions:
            to_compress.append(self.craft_prefix_exceptions(tmp_dir))

        # Finally, create the ZIP
        final_file = self.dictionary_file(self.output_file)
        with ZipFile(final_file, mode="w", compression=ZIP_DEFLATED) as fh:
            # The ZIP's comment will serve as the dictionary signature
            fh.comment = self.description.encode(encoding="utf-8")

            # Unrelated files, just for history
            fh.writestr(constants.ZIP_WORDS_COUNT, str(self.words_count + self.variants_count))
            fh.writestr(constants.ZIP_WORDS_SNAPSHOT, self.snapshot)

            for file in to_compress:
                fh.write(file, arcname=file.name)

            # Check the ZIP validity
            # testzip() returns the name of the first corrupt file, or None
            assert fh.testzip() is None, fh.testzip()

        self.summary(final_file)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def save_html(self, name: str, words: Words, output_dir: Path) -> Path | None:
        """Generate individual HTML files.

        Content of the HTML file:

            <html>
                word 1
                word 2
                ...
            </html>
        """

        # Save to uncompressed HTML
        if not (data := "".join(line for word in words for line in self.handle_word(word, self.words))):
            return None
        raw_output = output_dir / f"{name}.raw.html"
        raw_output.write_text(data, encoding="utf-8")

        # Compress the HTML with gzip
        output = output_dir / f"{name}.html"
        with raw_output.open(mode="rb") as fi, gzip.open(output, mode="wb") as fo:
            fo.write(fi.read())

        return output

    def summary(self, file: Path) -> None:
        log.info("[%s] utils.guess_prefix() %s", self.id(), utils.guess_prefix.cache_info())
        super().summary(file)
