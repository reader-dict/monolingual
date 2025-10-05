def code(kind: str, value: str) -> str:
    """
    >>> code("html", "")
    ''
    >>> code("html", "</span>")
    '<code>&lt;/span&gt;</code>'

    >>> code("js", "(65535).toString(16) === 'ffff'")
    "<code>(65535).toString(16) === 'ffff'</code>"
    >>> code("js", "=(65535).toString(16) === 'ffff'")
    "<code>(65535).toString(16) === 'ffff'</code>"
    >>> code("js", "==(65535).toString(16) === 'ffff'")
    "<code>=(65535).toString(16) === 'ffff'</code>"
    """
    from html import escape

    if not value:
        return ""
    if value[0] == "=":
        value = value[1:]
    if kind == "html":
        value = escape(value)
    return f"<code>{value}</code>"


overrides = {
    "code": lambda args: code(args[1], args[2]),
}
