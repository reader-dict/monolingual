"""Malagasy language."""

import re

from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://mg.wiktionary.org/wiki/Manokana:Kisendra"

template_trans = "Modèle"

head_sections = ("{{=mg=}}", "{{=mul=}}")
etyl_section = ("etim",)
sections = (
    *etyl_section,
    "ana",  # common noun
    "e-",  # forms (for variants)
    # "eva",  # letter, see #2634
    "isa",  # (number)
    # "marika",  # symbol, see #2634
    "mat",  # verb
    "mpam",  # adjective
    "nom-pr",  # proper noun
    "tamb",  # adverb
    "dika-mitovy",  # synonyms
)

variant_templates = ("{{flexion",)

templates_ignored = (
    "{{...",
    "{{dikantenin'ny dikanteny",
    "{{ébauche",
    "{{vang-",
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "mg")
    []
    >>> find_pronunciations("{{fanononana|t͡situnɖ͡ʐuit͡sikʲạ|mg}}", "mg")
    ['/t͡situnɖ͡ʐuit͡sikʲạ/']
    >>> find_pronunciations("* {{IPA|mul|[ˈkilo]|ref={{cite-book |title=DIN 5009:2022-06 |page=Anhang B: Buchstabiertafel der ICAO („Radiotelephony Spelling Alphabet“) |publisher=Deutsches Institut für Normung |date=June 2022 }}}}", "mg")
    ['/ˈkilo/']
    """
    return [
        f"/{pron}/" for pron in re.findall(rf"\{{\{{fanononana\|([^|]+)\|{locale}\}}\}}", code) if "}" not in pron
    ] or [f"/{pron}/" for pron in re.findall(r"\{\{IPA\|\w+\|\[([^\]]+)\]", code)]


VAR_PATTERNS = [
    # Mpanao faharoa ny ploraly ny endrika efa lasan'ny matoanteny ''[[tsitondroina]]''.
    # Mpanao voalohan'ny endrika ploraly (eksklioziva) ny teny [[tsitondroina]]
    #  ploraly ny ova matoanteny efa lasa ny matoanteny [[tsitondroina]]
    # Mpandray anjara faharoa ny ploraly ny teny ''[[tsitondroina]]''.
    # Mpanao voalohany singiolary ny teny ''[[tsitondroina]]''.
    # Endrika ankehitrin'ny matoantenin'ny atao mampitranga mpifampivoho ny matoanteny mifamoivoho avy amin'ny anarana iombonana ''[[filingitana]]''.
    # Anarana mpanao avy amin'ny matoanteny ''[[miebokeboka]]''.
    # Endrika ho avin'ny ny matoantenin'ny atao mampitranga mampita avy amin'ny anarana iombonana ''[[fandrodahana]]''.
    # Endrika ho avin'ny ny matoantenin'ny atao mifampivoho avy amin'ny anarana iombonana ''[[fanatsembohana]]''.
    re.compile(
        r"^#[ ]*.+ (?:endrika|mampitranga|matoantenin|matoanteny|mpanao|ploraly|singiolary).+ (?:anarana|matoanteny|teny).+\[\[([^\]#]+).*",
        flags=re.MULTILINE,
    ),
    # ''[[famadidirana]]'' mifanao.
    re.compile(r"#[ ']*\[\[([^\]]+)\]\]'* mifanao.", flags=re.MULTILINE),
]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("{{-ana-|mg}}", "mg")
    '===ana==='
    >>> adjust_wikicode("{{-e-ana-|mg}}", "mg")
    '===e-ana==='
    >>> adjust_wikicode("{{-ana-}}", "mg")
    '===ana==='
    >>> adjust_wikicode("{{-anagr-}}", "mg")
    '=====anagr====='

    >>> adjust_wikicode("{{-dika-mitovy-}}\n* [[a]]\n* [[b]]", "mg")
    '===dika-mitovy===\n# [[a]]\n# [[b]]'

    >>> adjust_wikicode("# Mpanao faharoa ny ploraly ny endrika efa lasan'ny matoanteny ''[[foo]]''.", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("# Mpanao voalohan'ny endrika ploraly (eksklioziva) ny teny [[foo]]", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("#  ploraly ny ova matoanteny efa lasa ny matoanteny [[foo]]", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("# Mpandray anjara faharoa ny ploraly ny teny ''[[foo]]''.", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("# Mpanao voalohany singiolary ny teny ''[[foo]]''.", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("# Endrika ankehitrin'ny matoantenin'ny atao mampitranga mpifampivoho ny matoanteny mifamoivoho avy amin'ny anarana iombonana ''[[foo]]''.", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("# Anarana mpanao avy amin'ny matoanteny ''[[foo]]''.", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("# Endrika ho avin'ny ny matoantenin'ny atao mampitranga mampita avy amin'ny anarana iombonana ''[[foo]]''.", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("# Endrika ho avin'ny ny matoantenin'ny atao mifampivoho avy amin'ny anarana iombonana ''[[foo]]''.", "mg")
    '# {{flexion|foo}}'
    >>> adjust_wikicode("# ''[[foo]]'' mifanao.", "mg")
    '# {{flexion|foo}}'
    """
    # {{-ana-|mg}} → ===ana===
    # {{-ana-}} → ===ana===e
    code = re.sub(r"^\{\{-(.+)-(?:\|\w+)?\}\}", r"===\1===", code, flags=re.MULTILINE)

    # We do not want to keep anagrams
    code = code.replace("===anagr===", "=====anagr=====")

    # Change synonyms list type
    lines: list[str] = []
    in_section = False
    for line_ in code.splitlines():
        if not (line := line_.strip()):
            continue
        if line.startswith("==="):
            in_section = "dika-mitovy" in line
        if in_section and line.startswith("*"):
            line = line.replace("*", "#", count=1)
        lines.append(line)
    code = "\n".join(lines)

    #
    # Variants
    #

    lines.clear()
    for line in code.splitlines():
        if line.startswith("#"):
            for pattern in VAR_PATTERNS:
                line, count = pattern.subn(r"# {{flexion|\1}}", line, count=1)
                if count:
                    break
        lines.append(line)
    code = "\n".join(lines)

    return code
