"""Type annotations."""

from dataclasses import dataclass, field

SubDefinition = str | tuple[str, ...]
Definition = str | tuple[str, ...] | tuple[SubDefinition, ...]
Definitions = dict[str, list[Definition]]
Parts = tuple[str, ...]
Variants = dict[str, set[str]]


@dataclass(slots=True)
class Word:
    pronunciations: list[str] = field(default_factory=list)
    genders: list[str] = field(default_factory=list)
    etymology: list[Definition] = field(default_factory=list)
    definitions: Definitions = field(default_factory=dict)
    variants: list[str] = field(default_factory=list)
    reverse_variants: list[str] = field(default_factory=list)
    is_variant: bool = False


Words = dict[str, Word]
Groups = dict[str, Words]
