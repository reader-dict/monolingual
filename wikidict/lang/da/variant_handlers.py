import re
from collections import defaultdict

import wikitextparser as wtp

from ... import context, utils


def cleanup(form: str) -> str:
    """
    >>> cleanup("(den) studerende")
    'studerende'
    """
    return utils.cleanup_rev_variant(
        form,
        skip={"akkusativ", "bestemt", "dativ", "genitiv", "nominativ", "ubestemt"},
        rpl=["(de) ", "(den) "],
    )


RE_FORM1 = re.compile(r"<b>\[\[([^\]#]++)")
RE_FORM2 = re.compile(r"\[\[([^\]#]++)")


def table_to_forms(word: str, wikitext: str) -> list[str]:
    r"""
    >>> table_to_forms("baskyle", '''{| border=0 \n|-\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nEntal&nbsp;ubestemt<br>\nen&nbsp;<b>[[bakterie]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nEntal&nbsp;bestemt<br>\n<b>[[bakterien#Dansk|bakterien]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nFlertal&nbsp;ubestemt<br>\n<b>[[bakterier#Dansk|bakterier]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nFlertal&nbsp;bestemt<br>\n<b>[[bakterierne#Dansk|bakterierne]]</b>\n|}\n|}''')
    ['bakterie', 'bakterien', 'bakterier', 'bakterierne']
    >>> table_to_forms("hund", '''&nbsp; &nbsp; Bøjning af „hund“\n\n{| class="inflection-table" style="text-align:center;width:100%;"\n|- style="background-color:#eee;"\n! rowspan="2" style="width:25%;" | fælleskøn\n! colspan="2" | \'\'Ental\'\'\n! colspan="2" | \'\'Flertal\'\'\n|- style="font-size:90%;background-color:#eee;"\n! \'\'ubestemt\'\' || \'\'bestemt\'\' || \'\'ubestemt\'\' || \'\'bestemt\'\'\n|-\n! style="background-color:#eee;" | \'\'[[nominativ]]\'\', \'\'[[dativ]]\'\' og \'\'[[akkusativ]]\'\'\n| style="background-color:#f9f9f9;"| [[hund]]\n| style="background-color:#f9f9f9;"| [[hunden]]\n| style="background-color:#f9f9f9;"| [[hunde]]\n| style="background-color:#f9f9f9;"| [[hundene]]\n|-\n! style="background-color:#eee;" | \'\'[[genitiv]]\'\'\n| style="background-color:#f9f9f9;"| [[hunds]]\n| style="background-color:#f9f9f9;"| [[hundens]]\n| style="background-color:#f9f9f9;"| [[hundes]]\n| style="background-color:#f9f9f9;"| [[hundenes]]\n|-\n|}''')
    ['hunde', 'hunden', 'hundene', 'hundenes', 'hundens', 'hundes', 'hunds']
    >>> table_to_forms("kapitel", '''{|  style="background-color:#FFFAFA; color: #8B795E; text-align:center; border: 1px solid #EEE9BF; font-size:11px; line-height:14px; font-stretch:extra-expanded;" cellpadding="3" cellspacing="1"\n|- style="background-color:#EEE9BF; "\n! width=70 | Bøjning af \'\'[[kapitel]] \'\'\n! colspan=2 | Ental\n! colspan=2  | Flertal\n|- style="background-color:#EEE9BF; "\n! \'\'\'intetkøn\'\'\'\n! width=65 | Ubestemt\n! width=65 | Bestemt || width=65 | Ubestemt || width=65 | Bestemt\n|- align=center\n!style="background-color:#EEE9BF; " | Nominativ\n| [[]]\n| [[kapitlet]] || [[]]\n| [[kapitlen]]\n|- align=center\n!style="background-color:#EEE9BF; " | Genitiv\n| [[s]]\n| [[kapitlets]] || [[s]]\n| [[kapitlens]]\n|}''')
    ['kapitels', 'kapitlen', 'kapitlens', 'kapitlet', 'kapitlets']
    >>> table_to_forms("hond", '''{| class="prettytable" style="margin-left: 15px;"\n|- style="text-align:center;"\n|width=30px| \'\'\'Bøjning\'\'\'\n|width=80px colspan="2"| Ental\n|width=80px colspan="2"| Flertal\n|- style="text-align:center;"\n|width=30px|\n|bgcolor="#ffffff"| Ubestemt\n|bgcolor="#efefef"| Bestemt\n|bgcolor="#ffffff"| Ubestemt\n|bgcolor="#efefef"| Bestemt\n|- style="text-align:center;"\n| Nominativ\n|bgcolor="#ffffff"| hond\n|bgcolor="#efefef"| hondin\n|bgcolor="#ffffff"| hendur\n|bgcolor="#efefef"| hendurnar\n|- style="text-align:center;"\n| Akkusativ\n|bgcolor="#ffffff"| hond\n|bgcolor="#efefef"| hondina\n|bgcolor="#ffffff"| hendur\n|bgcolor="#efefef"| hendurnar\n|- style="text-align:center;"\n| Dativ\n|bgcolor="#ffffff"| hond\n|bgcolor="#efefef"| hondini\n|bgcolor="#ffffff"| hondum\n|bgcolor="#efefef"| hondunum\n|- style="text-align:center;"\n| Genitiv\n|bgcolor="#ffffff"| handar\n|bgcolor="#efefef"| handarinnar\n|bgcolor="#ffffff"| handa \n|bgcolor="#efefef"| handanna\n|}''')
    ['handa', 'handanna', 'handar', 'handarinnar', 'hendur', 'hendurnar', 'hondin', 'hondina', 'hondini', 'hondum', 'hondunum']
    >>> table_to_forms("hond", '''{| class="wikitable"\n|-\n! Ental !! Flertal !! Diminutiv ental !!Diminutiv flertal\n|- align="center"\n| hond || honde &nbsp;\n| hondjie || hondjies\n|}''')
    ['honde', 'hondjie', 'hondjies']
    >>> table_to_forms("getuige", '''{| border=0 \n|-\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nBest.  Ental<br>\nde    <b>[[getuige]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nEntal&nbsp;diminutiv<br>\n<b>[[(getuigetje)]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nFlertal<br>\n<b>[[getuigen]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nFlertal&nbsp;diminutiv<br>\n<b>[[(getuigetjes)]]</b>\n|}\n|}''')
    ['getuigen', 'getuigetje', 'getuigetjes']
    >>> table_to_forms("pracovat", '''\'\'\'pracovat\'\'\'&nbsp;''imperfektiv''&nbsp;(''perfektiv''&nbsp;[[-]])''')
    []
    >>> table_to_forms("pracovat", '''Konjugation af \'\'\'pracovat\'\'\'</small>\n\n{| class="wikitable inflection-table" style="text-indent:4px"\n! Person\n! Præsens\n! Præteritum\n! Futurum\n! Konditionalis\n! Imperativ\n|-\n! style="text-align:center;" |\'\'já\'\'\n|pracuju,<br>pracuji (formel) ||pracoval jsem \'\'M\'\'<br>&nbsp;pracovala jsem \'\'F\'\'||budu pracovat ||pracoval bych \'\'M\'\'<br>&nbsp;pracovala bych \'\'F\'\'|| —\n|-\n! style="text-align:center;" |\'\'ty\'\'\n| pracuješ ||pracoval jsi \'\'M\'\'<br>&nbsp;pracovala jsi \'\'F\'\'||budeš pracovat ||pracoval bys \'\'M\'\'<br>&nbsp;pracovala bys \'\'F\'\'||pracuj\n|-\n! style="text-align:center;" |\'\'on\'\'<br>\'\'ona\'\'<br>\'\'ono\'\'\n| pracuje ||pracoval \'\'M\'\'<br>&nbsp;pracovala \'\'F\'\'<br>&nbsp;pracovalo \'\'N\'\' ||bude pracovat || pracoval by \'\'M\'\'<br>&nbsp;pracovala by \'\'F\'\'<br>&nbsp;pracovalo by \'\'N\'\'|| —\n|-\n! style="text-align:center;" |\'\'my\'\'\n| pracujeme ||pracovali jsme \'\'M\'\'<br>&nbsp;pracovaly jsme \'\'F\'\'|| budeme pracovat ||pracovali bychom \'\'M\'\'<br>&nbsp;pracovaly bychom \'\'F\'\'||pracujme\n|-\n! style="text-align:center;" |\'\'vy\'\'\n| pracujete ||pracovali jste \'\'M\'\'<br>&nbsp;pracovaly jste \'\'F\'\'||budete pracovat || pracovali byste \'\'M\'\'<br>&nbsp;pracovaly byste \'\'F\'\'||pracujte\n|-\n! style="text-align:center;" |\'\'oni\'\'<br>\'\'ony\'\'<br>\'\'ony\'\'\n| pracujou,<br>pracují (formel) ||pracovali \'\'M\'\'<br>&nbsp;pracovaly \'\'F\'\'<br>&nbsp;pracovala \'\'N\'\'||budou pracovat ||pracovali by \'\'M levende\'\'<br>&nbsp;pracovaly by \'\'M ikke-levende\'\', \'\'F\'\'<br>&nbsp;pracovala by \'\'N\'\'|| —\n|}''')
    ['bude pracovat', 'budeme pracovat', 'budete pracovat', 'budeš pracovat', 'budou pracovat', 'budu pracovat', 'pracuj', 'pracuje', 'pracujeme', 'pracujete', 'pracuješ', 'pracuji', 'pracujme', 'pracujou', 'pracujte', 'pracuju', 'pracují']
    """
    forms: set[str] = set()
    tables = wtp.parse(wikitext).get_tables(recursive=True)

    # Try 1
    for table in tables:
        line = str(table).splitlines()[2]
        for form in RE_FORM1.findall(line):
            if "<br/>" in form:
                forms.update([cleanup(f) for f in form.split("<br/>")])
            elif "/" in form:
                forms.update([cleanup(f) for f in form.split("/")])
            else:
                forms.add(cleanup(form))

    # Try 2
    if not forms:
        for table in tables:
            data = table.data(span=False)
            for lines in data[1:]:
                for line in lines:
                    if not line or "''" in line:
                        continue
                    if form := RE_FORM2.findall(line):
                        forms.add(cleanup(form[0]))
                    # Try 3
                    elif line.strip("[]()"):
                        if ",<br>" in line:
                            forms.update([cleanup(f) for f in line.split(",<br>")])
                        else:
                            forms.add(cleanup(line))

    forms.discard(word)
    forms.discard("&ndash;")
    forms.discard("-")
    forms.discard("—")
    forms.discard("")

    if "s" in forms:
        forms.discard("s")
        forms.add(f"{word}s")

    return sorted(forms)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["tale"], defaultdict(str), "")
    'tale'

    >>> render_variant("{{form of", ["imperative form", "bjerge"], defaultdict(str, {"lang": "da"}), "")
    'bjerge'
    """
    return parts[-1]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["baskylen"], defaultdict(str), "baskyle")
    'baskylen'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "da")
    if not table.startswith("{|"):
        if (idx := table.find("{|")) == -1:
            return ""
        table = table[idx:]
    return "|".join(table_to_forms(word, table))


handlers = {
    **dict.fromkeys(
        {
            "alternativ stavemåde af",
            "flexion",
            "form of",
            "imperativ af",
            "imperativ form af",
        },
        render_variant,
    ),
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
