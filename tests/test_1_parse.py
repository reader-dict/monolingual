import bz2
import os
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context, parse


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("fr")


def save(path: Path, content: str) -> Path:
    file = path / "page.xml.bz2"
    with bz2.open(file, "wt", encoding="utf-8") as fh:
        fh.write(content)
    return file


def test_simple(craft_data: Callable[[str], bytes]) -> None:
    output_dir = Path(os.environ["CWD"]) / "data" / "fr"

    # Delete an previously created file to cover the save() part
    for file in output_dir.glob("data_wikicode-*.json"):
        file.unlink()

    # Ensure there is data to process.
    compressed = craft_data("fr")
    (output_dir / "pages-20201217.xml.bz2").write_bytes(compressed)

    assert parse.main("fr") == 0


def test_no_xml_file() -> None:
    with patch.object(parse, "get_latest_file", return_value=None):
        assert parse.main("fr") == 1


def test_parse_restricted_word(tmp_path: Path) -> None:
    """For instance, "cunnilingus" was filtered out. Ensure no regressions."""
    file = save(
        tmp_path,
        """\
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xml:lang="fr">
  <page>
    <title>cunnilingus</title>
    <ns>0</ns>
    <id>27758</id>
    <restrictions>edit=autoconfirmed:move=autoconfirmed</restrictions>
    <revision>
        <id>27636792</id>
        <parentid>27249625</parentid>
        <timestamp>2020-04-05T23:27:40Z</timestamp>
        <contributor>
            <username>Alice</username>
            <id>-42</id>
        </contributor>
        <minor />
        <comment></comment>
        <model>wikitext</model>
        <format>text/x-wiki</format>
        <text bytes="292" xml:space="preserve">{{voir|Cunnilingus}}

== {{langue|fr}} ==
=== {{S|nom|fr}} ===
{{fr-inv|ky.ni.lɛ̃.gys|sp=1}}
[[Fichier:Édouard-Henri Avril (23).jpg|thumb|Un '''cunnilingus''']]
'''cunnilingus''' {{pron|ky.ni.lɛ̃.ɡys|fr}} {{m}}, {{sp}}
# {{sexe|fr}} [[excitation|Excitation]] [[buccal]]e des [[organe]]s [[génitaux]] [[féminins]].</text>
        <sha1>aimljsg0qagdsp5yyz38fgv3rh0ksm1</sha1>
    </revision>
  </page>
</mediawiki>
""",
    )

    assert "cunnilingus" in parse.process(file, "fr")


def test_parse_redirected_word(tmp_path: Path) -> None:
    file = save(
        tmp_path,
        """\
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xml:lang="fr">
  <page>
    <title>abkhaserene</title>
    <ns>0</ns>
    <id>24608</id>
    <redirect title="abkhaserne" />
    <revision>
        <id>123263</id>
        <parentid>123256</parentid>
        <timestamp>2013-12-10T16:41:03Z</timestamp>
        <contributor>
          <username>Alice</username>
          <id>42</id>
        </contributor>
        <model>wikitext</model>
        <format>text/x-wiki</format>
        <text bytes="23" sha1="5azntpng4wtt8cmcqz845vsdh69gk8u" xml:space="preserve">#REDIRECT[[abkhaserne]]</text>
        <sha1>5azntpng4wtt8cmcqz845vsdh69gk8u</sha1>
    </revision>
  </page>
</mediawiki>
""",
    )

    assert parse.process(file, "fr") == {"abkhaserene": "##REDIRECT##abkhaserne"}


def test_parse_word_without_wikicode(tmp_path: Path) -> None:
    file = save(
        tmp_path,
        """\
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xml:lang="fr">
  <page>
    <title>MediaWiki</title>
    <ns>8</ns>
    <id>12</id>
    <revision>
        <id>403956</id>
        <parentid>33016</parentid>
        <timestamp>2006-02-13T09:08:31Z</timestamp>
        <contributor>
        <username>Bob</username>
            <id>-42</id>
            </contributor>
        <comment>changement de titre pour meilleur référencement dans les moteurs de recherche</comment>
        <model>wikitext</model>
        <format>text/x-wiki</format>
        <sha1>40helna9646ffk0utvwm8bkdlzi1eck</sha1>
    </revision>
  </page>
</mediawiki>
""",
    )

    assert not parse.process(file, "fr")


def test_parse_word_with_colons(tmp_path: Path) -> None:
    file = save(
        tmp_path,
        """\
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xml:lang="fr">
  <page>
    <title>MediaWiki:Sitetitle</title>
    <ns>8</ns>
    <id>12</id>
    <revision>
        <id>403956</id>
        <parentid>33016</parentid>
        <timestamp>2006-02-13T09:08:31Z</timestamp>
        <contributor>
        <username>Bob</username>
        <id>-42</id>
        </contributor>
        <comment>changement de titre pour meilleur référencement dans les moteurs de recherche</comment>
        <model>wikitext</model>
        <format>text/x-wiki</format>
        <text bytes="46" xml:space="preserve">{{voir|Cunnilingus}}

== {{langue|fr}} ==
=== {{S|nom|fr}} ===
{{fr-inv|ky.ni.lɛ̃.gys|sp=1}}
[[Fichier:Édouard-Henri Avril (23).jpg|thumb|Un '''cunnilingus''']]
'''cunnilingus''' {{pron|ky.ni.lɛ̃.ɡys|fr}} {{m}}, {{sp}}
# {{sexe|fr}} [[excitation|Excitation]] [[buccal]]e des [[organe]]s [[génitaux]] [[féminins]].</text>
        <sha1>40helna9646ffk0utvwm8bkdlzi1eck</sha1>
    </revision>
  </page>
</mediawiki>
""",
    )

    assert not parse.process(file, "fr")


def test_parse_word_with_templates_lowercased(tmp_path: Path) -> None:
    file = save(
        tmp_path,
        """\
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xml:lang="fr">
  <page>
    <title>restaurang</title>
    <ns>0</ns>
    <id>5156</id>
    <revision>
      <id>3874635</id>
      <parentid>3872233</parentid>
      <timestamp>2023-01-04T18:58:03Z</timestamp>
      <contributor>
        <username>Frodlekis</username>
        <id>762</id>
      </contributor>
      <comment>+he: [[מִסְעָדָה]] (assisterat)</comment>
      <origin>3874635</origin>
      <model>wikitext</model>
      <format>text/x-wiki</format>
      <text bytes="2778" sha1="7k86wfuvisuff9jk6ogymzuk5dgtjfq" xml:space="preserve">{{wikipedia}}

==Svenska==
===Substantiv===
{{sv-subst-n-er}}
'''restaurang'''
*{{uttal|sv|enkel=,rest(a)u’rang|ipa=ˌrɛst.(a)ɵˈraŋ}}
#[[inrättning]] där man [[köpa|köper]] [[mat]] som man sedan [[äta|äter]] på plats
#:{{varianter|[[restaurant]] ''(ålderdomlig stavning)''}}
#:{{sammansättningar|[[dansrestaurang]], [[fiskrestaurang]], [[gourmetrestaurang]], [[hamburgerrestaurang]], [[kinarestaurang]], [[lunchrestaurang]], [[personalrestaurang]], [[restaurangbesök]], [[restaurangbesökare]], [[restaurangbransch]], [[restaurangchef]], [[restauranggäst]], [[restaurangkedja]], [[restaurangkök]], [[restaurangnota]], [[restaurangskola]], [[restaurangsorl]], [[restaurangvagn]], [[restaurangägare]], [[snabbmatsrestaurang]], [[sushirestaurang]]}}
#:{{etymologi|Sedan 1865 av {{härledning|sv|fr|restaurant}} med samma betydelse, presensparticip av ''[[restaurer]]'' (”återlagra”), av {{härledning|sv|la|restaurare}}. Stavningen ''restaurang'' är belagd sedan 1889. Stavningen {{?|stavningen?!}} och uttalet ''resturang'' är mycket vanligt sen 1970-talet.}}
</text>
      <sha1>7k86wfuvisuff9jk6ogymzuk5dgtjfq</sha1>
    </revision>
  </page>
</mediawiki>
""",
    )

    assert "restaurang" in parse.process(file, "sv")


@pytest.mark.parametrize(
    "locale, lang_src, lang_dst",
    [
        ("fr", "fr", "fr"),
        ("fro", "fr", "fro"),
        ("fr:fro", "fr", "fro"),
        ("fr:it", "fr", "it"),
        ("it:fr", "it", "fr"),
    ],
)
def test_sublang(locale: str, lang_src: str, lang_dst: str, tmp_path: Path) -> None:
    snapshot = "20250401"
    pages = Path(f"pages-{snapshot}.xml.bz2")
    words: dict[str, str] = {}

    with patch.dict("os.environ", {"CWD": str(tmp_path)}):
        source_dir = parse.get_source_dir(lang_src)
        assert source_dir == tmp_path / "data" / lang_src

        output_file = parse.get_output_file(source_dir, lang_src, lang_dst, snapshot)
        assert output_file == source_dir.parent / lang_dst / lang_src / f"data_wikicode-{snapshot}.json"

        output_file_modules = parse.get_output_file_modules(source_dir, lang_src, lang_dst, snapshot)
        assert output_file_modules == source_dir.parent / lang_dst / lang_src / f"modules-{snapshot}.sqlite"

        with (
            patch.object(parse, "get_source_dir") as mocked_gsd,
            patch.object(parse, "get_latest_file") as mocked_glf,
            patch.object(parse, "process") as mocked_p,
            patch.object(parse, "save") as mocked_s,
        ):
            mocked_glf.return_value = pages
            mocked_gsd.return_value = source_dir
            mocked_p.return_value = words

            parse.main(locale)
            mocked_gsd.assert_called_once_with(lang_src)
            mocked_glf.assert_called_once_with(source_dir)
            mocked_p.assert_called_once_with(pages, locale)
            mocked_s.assert_called_once_with(output_file, words)
