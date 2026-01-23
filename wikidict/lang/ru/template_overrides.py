def template_quotes(args: tuple[str, ...]) -> str:
    """
    >>> template_quotes(('"', "ау"))
    '„ау“'
    """
    return f"„{args[1]}“"


overrides = {
    '"': template_quotes,
}
