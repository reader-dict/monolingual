from __future__ import annotations

import bz2
import logging

from jinja2 import Template

from wikidict.converters import BaseFormat, Summary

# DictFile-related dictionaries
# Source: https://pgaskin.net/dictutil/dictgen/#dictfile-format
# Source: https://github.com/hunspell/hunspell/blob/ecc6dbb52025bdf3a766429988e64190d912765f/man/hunspell.1#L93-L139 (for later, in case of issues with other sub-formats)
TEMPLATE = Template(
    """\
@ {{ word }}
{%- if pronunciation %}
:{{ pronunciation }}
{%- endif %}
{%- for variant in variants %}
& {{ variant }}
{%- endfor %}
<html>
{%- for pos, pos_definitions in definitions -%}
    <p>
    {%- if pos.find("|") > -1 -%}
    <b>{{ pos.split("|", 1)[0] }}</b> <i>{{ pos.split("|", 1)[1] }}</i>
    {%- else -%}
    <b>{{ pos }}</b>
    {%- endif -%}
    </p><ol>
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
            {%- if etymology.startswith("<table") -%}
                {{ etymology }}
            {%- else -%}
                <p>{{ etymology }}</p>
            {%- endif -%}
        {%- else -%}
            <ol>
                {%- for sub_etymology in etymology -%}
                    <li>{{ sub_etymology }}</li>
                {%- endfor -%}
            </ol>
        {%- endif -%}
    {%- endfor -%}
    <br/>
{%- endif %}


"""
)

log = logging.getLogger(__name__)


class DictFileFormat(Summary, BaseFormat):
    """Save the data into a bz2-compressed *.df* DictFile."""

    output_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.df.bz2"
    template = TEMPLATE

    def process(self) -> None:
        file = self.dictionary_file(self.output_file)
        words = self.words
        with bz2.open(file, mode="wb") as fh:
            for word in words:
                fh.write("".join(self.handle_word(word, words)).encode(encoding="utf-8"))

        self.summary(file)
