"""Type annotations."""

import json
from collections import OrderedDict
from dataclasses import dataclass, field

SubDefinition = str | list[str]
Definition = str | list[str] | list[SubDefinition]
Definitions = OrderedDict[str, list[Definition]]
Parts = tuple[str, ...]
Variants = dict[str, set[str]]


@dataclass(slots=True)
class Word:
    pronunciations: list[str] = field(default_factory=list)
    genders: list[str] = field(default_factory=list)
    etymology: list[Definition] = field(default_factory=list)
    definitions: Definitions = field(default_factory=OrderedDict)
    variants: list[str] = field(default_factory=list)
    reverse_variants: list[str] = field(default_factory=list)
    is_variant: bool = False

    def tojson(self) -> str:
        return json.dumps(
            [self.pronunciations, self.etymology, self.definitions, self.variants, self.reverse_variants],
            ensure_ascii=False,
            indent=4,
        )


Words = dict[str, Word]
Groups = dict[str, Words]
