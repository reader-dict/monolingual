from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("en-archaic third-person singular of", ["verb"], defaultdict(str), "")
    'verb'

    >>> render_variant("infl of", ["en", "human", "", "s-verb-form"], defaultdict(str), "humans")
    'human'
    >>> render_variant("infl of", ["en", "human", "", "s-verb-form"], defaultdict(str, {"1": "en", "2": "human", "3": "", "4": "s-verb-form"}), "humans")
    'human'
    >>> render_variant("infl of", ["en", "foo (“bar)"], defaultdict(str), "")
    'foo'

    >>> render_variant("plural of", ["en", "woman"], defaultdict(str), "women")
    'woman'
    >>> render_variant("plural of", ["en", "hop<id:ultimately-from-PIE-kewb->"], defaultdict(str, {"gloss": "jump"}), "hops")
    'hop'

    >>> render_variant("form of", ["en", "Alternative (anglicized) spelling", "Wrocław"], defaultdict(str), "Wroclaw")
    'Wrocław'
    >>> render_variant("adj form of", ["en", "Alternative (anglicized) spelling", "Wrocław"], defaultdict(str), "Wroclaw")
    'Alternative (anglicized) spelling'
    """
    if "en-archaic" in tpl:
        return parts[0]

    if tpl == "form of":
        return parts[-1]

    base = data["2"] or parts[1]

    if "infl" in tpl and ("(") in base:
        base = base.split("(", 1)[0].strip()

    if "<" in base:
        base = base.split("<", 1)[0]

    return base


handlers = {
    **dict.fromkeys(
        {
            "active participle of",
            "adj form of",
            "agent noun of",
            "an of",
            "alternative plural of",
            "female equivalent of",
            "feminine equivalent of",
            "femeq",
            "feminine of",
            "feminine plural of",
            "feminine plural past participle of",
            "feminine singular of",
            "feminine singular past participle of",
            "form of",
            "gerund of",
            "imperfective form of",
            "inflection of",
            "infl of",
            "masculine plural of",
            "masculine plural past participle of",
            "neuter plural of",
            "neuter singular past participle of",
            "noun form of",
            "participle of",
            "passive of",
            "passive participle of",
            "past participle form of",
            "past participle of",
            "perfective form of",
            "plural of",
            "plural",
            "present participle of",
            "reflexive of",
            "verbal noun of",
            "verb form of",
        },
        render_variant,
    ),
}
