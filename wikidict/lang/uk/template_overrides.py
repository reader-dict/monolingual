def template_quotes(args: tuple[str, ...]) -> str:
    """
    >>> template_quotes(('"', "ау"))
    '„ау“'
    """
    return f"„{args[1]}“"


def template_two(args: tuple[str, ...]) -> str:
    """
    >>> template_two(("2"))
    ''
    >>> template_two(("2", "a"))
    'a'
    >>> template_two(("2", "a", "b"))
    'a b'
    >>> template_two(("2", "a", "b", "c"))
    'a b'
    """
    return " ".join(args[1:3])


overrides = {
    '"': template_quotes,
    "2": template_two,
}
