from collections import defaultdict

from .place import get_def


def show(parts: list[str], data: defaultdict) -> str:
    return get_def(parts, data)
