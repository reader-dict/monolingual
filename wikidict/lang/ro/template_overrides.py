from ... import utils


def template_trad(args: tuple[str, ...]) -> str:
    """
    >>> template_trad(("trad", "el", "παρα"))
    'παρα'
    """
    parts = list(args[1:])
    utils.extract_keywords_from(parts)
    return parts[1]


overrides = {
    "trad": template_trad,
}
