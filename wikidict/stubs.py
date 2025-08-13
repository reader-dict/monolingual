"""Type annotations."""

from dataclasses import dataclass

SubDefinition = str | tuple[str, ...]
Definition = str | tuple[str, ...] | tuple[SubDefinition, ...]
Definitions = dict[str, list[Definition]]
Parts = tuple[str, ...]
Variants = dict[str, list[str]]


@dataclass(slots=True)
class Word:
    pronunciations: list[str]
    genders: list[str]
    etymology: list[Definition]
    definitions: Definitions
    variants: list[str]
    is_variant: bool = False


Words = dict[str, Word]
Groups = dict[str, Words]
