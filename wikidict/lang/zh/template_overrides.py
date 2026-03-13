def template_category(args: tuple[str, ...]) -> str:
    """
    >>> template_category(("分類", "和製漢語"))
    ''
    """
    return ""


overrides = {
    "分類": template_category,
}
