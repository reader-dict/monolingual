"""
Source: https://en.wiktionary.org/w/index.php?title=Module:place/placetypes&oldid=85730296
"""

import re
from collections.abc import Callable, Sequence
from typing import Any

from ..utilities import pluralize, singularize
from .locations import iterate_matching_location, key_to_placename

PLACETYPE_DATA: dict[str, dict[str, Any]] = {
    "*": {
        "link": False,
    },
    "administrative atoll": {
        "link": "+w:administrative divisions of the Maldives",
        "preposition": "of",
        "class": "subpolity",
    },
    "administrative capital": {
        "link": "w",
        "fallback": "capital city",
    },
    "administrative center": {
        "link": "w",
        "fallback": "non-city capital",
    },
    "administrative centre": {
        "link": "w",
        "fallback": "administrative center",
    },
    "administrative county": {
        "link": "w",
        "fallback": "county",
    },
    "administrative district": {
        "link": "w",
        "fallback": "district",
    },
    "administrative headquarters": {
        "link": "separately",
        "fallback": "administrative centre",
    },
    "administrative region": {
        "link": True,
        "preposition": "of",
        "suffix": "region",
        "fallback": "region",
        "class": "subpolity",
    },
    "administrative seat": {
        "link": "w",
        "fallback": "administrative centre",
    },
    "administrative territory": {
        "link": "separately",
        "preposition": "of",
        "suffix": "territory",
        "fallback": "territory",
        "class": "subpolity",
    },
    "administrative unit": {
        "link": "w",
        "class": "subpolity",
    },
    "administrative village": {
        "link": "w",
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "settlement",
    },
    "aimag": {
        "link": "w",
        "fallback": "prefecture",
    },
    "airport": {
        "link": True,
        "class": "man-made structure",
        "default": [True],
    },
    "alliance": {
        "link": True,
        "fallback": "confederation",
    },
    "archipelago": {
        "link": True,
        "fallback": "island",
    },
    "area": {
        "link": True,
        "preposition": "of",
        "fallback": "geographic and cultural area",
        "class": "subpolity",
        "former_type": "geographic region",
    },
    "arm": {
        "link": True,
        "preposition": "of",
        "class": "natural feature",
        "default": ["Seas"],
    },
    "arrondissement": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
        "has_neighborhoods": True,
    },
    "associated province": {
        "link": "separately",
        "fallback": "province",
    },
    "atoll": {
        "link": True,
        "class": "natural feature",
        "bare_category_parent": "islands",
        "default": [True],
    },
    "autonomous city": {
        "link": "w",
        "preposition": "of",
        "fallback": "city",
        "has_neighborhoods": True,
    },
    "autonomous community": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "autonomous island": {
        "link": "+w:autonomous islands of Comoros",
        "preposition": "of",
        "class": "subpolity",
    },
    "autonomous oblast": {
        "link": True,
        "preposition": "of",
        "affix_type": "Suf",
        "no_affix_strings": "oblast",
        "class": "subpolity",
    },
    "autonomous okrug": {
        "link": True,
        "preposition": "of",
        "affix_type": "Suf",
        "no_affix_strings": "okrug",
        "class": "subpolity",
    },
    "autonomous prefecture": {
        "link": True,
        "fallback": "prefecture",
    },
    "autonomous province": {
        "link": "w",
        "fallback": "province",
    },
    "autonomous region": {
        "link": "w",
        "preposition": "of",
        "fallback": "administrative region",
        "affix": "autonomous region",
    },
    "autonomous republic": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "autonomous territorial unit": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "autonomous territory": {
        "link": "w",
        "fallback": "dependent territory",
    },
    "bailiwick": {
        "link": True,
        "fallback": "polity",
    },
    "barangay": {
        "link": True,
        "class": "settlement",
        "fallback": "neighborhood",
    },
    "barrio": {
        "link": True,
        "fallback": "neighborhood",
    },
    "basin": {
        "link": True,
        "fallback": "lake",
    },
    "bay": {
        "link": True,
        "preposition": "of",
        "class": "natural feature",
        "addl_bare_category_parents": ["bodies of water"],
        "default": [True],
    },
    "beach": {
        "link": True,
        "class": "natural feature",
        "addl_bare_category_parents": ["water"],
        "default": [True],
    },
    "beach resort": {
        "link": "w",
        "fallback": "resort town",
    },
    "bishopric": {
        "link": True,
        "fallback": "polity",
    },
    "bodies of water!": {
        "category_link": "[[body of water|bodies of water]]",
        "class": "natural feature",
        "addl_bare_category_parents": ["landforms", "ecosystems", "water"],
    },
    "borough": {
        "link": True,
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "subpolity",
    },
    "borough seat": {
        "link": True,
        "entry_placetype_use_the": True,
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "capital",
    },
    "branch": {
        "link": True,
        "preposition": "of",
        "fallback": "river",
    },
    "bridge": {
        "link": True,
        "class": "man-made structure",
        "default": ["Named bridges"],
    },
    "building": {
        "link": True,
        "class": "man-made structure",
        "default": ["Named buildings"],
    },
    "built-up area": {
        "link": "w",
        "fallback": "area",
    },
    "burgh": {
        "link": True,
        "fallback": "borough",
    },
    "caliphate": {
        "link": True,
        "fallback": "polity",
    },
    "canton": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "cape": {
        "link": True,
        "fallback": "headland",
    },
    "capital": {
        "link": True,
        "fallback": "capital city",
    },
    "capital city": {
        "link": True,
        "category_link": "[[capital city|capital cities]]: the [[seat of government|seats of government]] for a country or [[political]] [[division]] of a country",
        "entry_placetype_use_the": True,
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "capital",
        "bare_category_parent": "cities",
        "default": [True],
        "fallback": "city",
    },
    "caplc": {
        "link": "[[capital]] and [[large]]st [[city]]",
        "plural_link": False,
        "fallback": "capital city",
    },
    "captaincy": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
        "inherently_former": ["FORMER"],
    },
    "caravan city": {
        "link": "w",
        "fallback": "city",
        "class": "settlement",
        "inherently_former": ["ANCIENT", "FORMER"],
    },
    "castle": {
        "link": True,
        "fallback": "building",
    },
    "cathedral city": {
        "link": True,
        "fallback": "city",
    },
    "cattle station": {
        "link": True,
        "fallback": "farm",
    },
    "census area": {
        "link": True,
        "affix_type": "Suf",
        "has_neighborhoods": True,
        "class": "non-admin settlement",
    },
    "census-designated place": {
        "link": True,
        "class": "non-admin settlement",
    },
    "census division": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "census town": {
        "link": "w",
        "fallback": "town",
    },
    "central business district": {
        "link": True,
        "fallback": "neighborhood",
    },
    "cercle": {
        "link": "+w:cercles of Mali",
        "preposition": "of",
        "class": "subpolity",
    },
    "ceremonial county": {
        "link": True,
        "fallback": "county",
    },
    "chain of islands": {
        "link": "[[chain]] of [[island]]s",
        "plural": "chains of islands",
        "plural_link": "[[chain]]s of [[island]]s",
        "fallback": "island",
    },
    "channel": {
        "link": True,
        "fallback": "strait",
    },
    "charter community": {
        "link": "w",
        "fallback": "village",
    },
    "city": {
        "link": True,
        "generic_before_non_cities": "in",
        "has_neighborhoods": True,
        "class": "settlement",
        "default": [True],
    },
    "city-state": {
        "link": True,
        "category_link": "[[sovereign]] [[microstate]]s consisting of a single [[city]] and [[w:dependent territory|dependent territories]]",
        "has_neighborhoods": True,
        "class": "settlement",
        "default": ["City-states", "Cities", "Countries", "National capitals"],
    },
    "civil parish": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "has_neighborhoods": True,
        "class": "subpolity",
    },
    "claimed political division": {
        "link": "[[claim]]ed [[political]] [[division]]",
        "class": "subpolity",
        "default": [True],
    },
    "co-capital": {
        "link": "[[co-]][[capital]]",
        "fallback": "capital city",
    },
    "coal city": {
        "link": "+w:coal town",
        "fallback": "city",
    },
    "coal town": {
        "link": "w",
        "fallback": "town",
    },
    "collectivity": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "colony": {
        "link": True,
        "fallback": "dependent territory",
    },
    "comarca": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "commandery": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
        "inherently_former": ["ANCIENT", "FORMER"],
    },
    "commonwealth": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "commune": {
        "link": True,
        "fallback": "municipality",
    },
    "community": {
        "link": True,
        "fallback": "village",
    },
    "community development block": {
        "link": "w",
        "affix_type": "suf",
        "no_affix_strings": "block",
        "class": "subpolity",
    },
    "comune": {
        "link": True,
        "fallback": "municipality",
    },
    "condominium": {
        "link": True,
        "fallback": "polity",
    },
    "confederacy": {
        "link": True,
        "fallback": "confederation",
    },
    "confederation": {
        "link": True,
        "fallback": "polity",
    },
    "constituency": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "constituent country": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "constituent part": {
        "link": "separately",
        "preposition": "of",
        "class": "subpolity",
    },
    "constituent republic": {
        "link": "separately",
        "preposition": "of",
        "class": "subpolity",
    },
    "counties and county-level cities!": {
        "category_link": "[[county|counties]] and [[county-level city|county-level cities]]",
        "class": "subpolity",
    },
    "continent": {
        "link": True,
        "class": "natural feature",
        "default": ["Continents and continental regions"],
    },
    "continental region": {
        "link": "separately",
        "class": "geographic region",
        "fallback": "continent",
    },
    "continents and continental regions!": {
        "class": "geographic region",
    },
    "council area": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "country": {
        "link": True,
        "class": "polity",
        "default": [True],
    },
    "country-like entities!": {
        "class": "polity",
    },
    "county": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "county borough": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "fallback": "borough",
        "class": "subpolity",
    },
    "county seat": {
        "link": True,
        "entry_placetype_use_the": True,
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "capital",
    },
    "county town": {
        "link": True,
        "entry_placetype_use_the": True,
        "preposition": "of",
        "fallback": "town",
        "has_neighborhoods": True,
        "class": "capital",
    },
    "county-administered city": {
        "link": "w",
        "fallback": "city",
        "has_neighborhoods": True,
        "class": "settlement",
    },
    "county-controlled city": {
        "link": "w",
        "fallback": "county-administered city",
    },
    "county-level city": {
        "link": "w",
        "fallback": "prefecture-level city",
    },
    "crater lake": {
        "link": True,
        "fallback": "lake",
    },
    "creek": {
        "link": True,
        "fallback": "stream",
    },
    "Crown colony": {
        "link": "+crown colony",
        "fallback": "crown colony",
    },
    "crown colony": {
        "link": True,
        "fallback": "colony",
    },
    "Crown dependency": {
        "link": True,
        "fallback": "dependent territory",
    },
    "crown dependency": {
        "link": True,
        "fallback": "dependent territory",
    },
    "cultural area": {
        "link": "w",
        "fallback": "geographic and cultural area",
    },
    "cultural region": {
        "link": "w",
        "fallback": "geographic and cultural area",
    },
    "delegation": {
        "link": "+w:delegations of Tunisia",
        "preposition": "of",
        "class": "subpolity",
    },
    "department": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "departmental capital": {
        "link": "separately",
        "fallback": "capital city",
    },
    "dependency": {
        "link": True,
        "fallback": "dependent territory",
    },
    "dependent territory": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
        "former_type": "dependent territory",
        "default": [True],
    },
    "desert": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "deserted mediaeval village": {
        "link": "w",
        "fallback": "deserted medieval village",
    },
    "deserted medieval village": {
        "link": "w",
        "fallback": "ANCIENT settlement",
    },
    "direct-administered municipality": {
        "link": "+w:direct-administered municipalities of China",
        "fallback": "municipality",
    },
    "direct-controlled municipality": {
        "link": "w",
        "fallback": "municipality",
    },
    "distributary": {
        "link": True,
        "preposition": "of",
        "fallback": "river",
    },
    "district": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "districts and autonomous regions!": {
        "class": "subpolity",
    },
    "districts and autonomous territorial units!": {
        "class": "subpolity",
    },
    "district capital": {
        "link": "separately",
        "fallback": "capital city",
    },
    "district headquarters": {
        "link": "separately",
        "fallback": "administrative centre",
    },
    "district municipality": {
        "link": "w",
        "preposition": "of",
        "affix_type": "suf",
        "no_affix_strings": ["district", "municipality"],
        "fallback": "municipality",
        "class": "subpolity",
    },
    "division": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "division capital": {
        "link": "separately",
        "fallback": "capital city",
    },
    "dome": {
        "link": True,
        "fallback": "mountain",
    },
    "dormant volcano": {
        "link": True,
        "fallback": "volcano",
    },
    "duchy": {
        "link": True,
        "fallback": "polity",
    },
    "emirate": {
        "link": True,
        "preposition": "of",
        "fallback": "polity",
    },
    "empire": {
        "link": True,
        "fallback": "polity",
    },
    "enclave": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "entity": {
        "link": "+w:entities of Bosnia and Herzegovina",
        "preposition": "of",
        "class": "subpolity",
    },
    "escarpment": {
        "link": True,
        "fallback": "mountain",
    },
    "ethnographic region": {
        "link": "+w:ethnographic regions of Lithuania",
        "fallback": "geographic and cultural area",
    },
    "exclave": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "external territory": {
        "link": "separately",
        "fallback": "dependent territory",
    },
    "farm": {
        "link": True,
        "class": "non-admin settlement",
        "default": ["Farms and ranches"],
    },
    "farms and ranches!": {
        "class": "non-admin settlement",
    },
    "federal city": {
        "link": "w",
        "preposition": "of",
        "fallback": "city",
    },
    "federal district": {
        "link": True,
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "settlement",
    },
    "federal subject": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "federal territory": {
        "link": "w",
        "fallback": "territory",
    },
    "fictional location": {
        "link": "separately",
        "former_type": "!",
        "class": "hypothetical location",
        "default": [True],
    },
    "First Nations reserve": {
        "link": "[[First Nations]] [[w:Indian reserve|reserve]]",
        "fallback": "Indian reserve",
        "class": "subpolity",
    },
    "fjord": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "footpath": {
        "link": True,
        "fallback": "road",
    },
    "forest": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "fort": {
        "link": True,
        "fallback": "building",
    },
    "fortress": {
        "link": True,
        "plural": "fortresses",
        "fallback": "building",
    },
    "frazione": {
        "link": "w",
        "fallback": "hamlet",
    },
    "freeway": {
        "link": True,
        "fallback": "road",
    },
    "French prefecture": {
        "link": "[[w:prefectures in France|prefecture]]",
        "entry_placetype_use_the": True,
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "capital",
    },
    "geographic and cultural area": {
        "link": "+w:cultural area",
        "generic_before_non_cities": "of",
        "preposition": "of",
        "class": "geographic region",
        "default": [True],
    },
    "geographic area": {
        "link": "+w:geographic region",
        "fallback": "geographic and cultural area",
    },
    "geographic region": {
        "link": "w",
        "fallback": "geographic and cultural area",
    },
    "geographical area": {
        "link": "w",
        "fallback": "geographic and cultural area",
    },
    "geographical region": {
        "link": "w",
        "fallback": "geographic and cultural area",
    },
    "geopolitical zone": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "gewog": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "ghost town": {
        "link": True,
        "generic_before_non_cities": "in",
        "class": "non-admin settlement",
        "default": [True],
    },
    "glen": {
        "link": True,
        "fallback": "valley",
    },
    "governorate": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "greater administrative region": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "gromada": {
        "link": "w",
        "preposition": "of",
        "affix_type": "Pref",
        "class": "subpolity",
    },
    "group of islands": {
        "link": "[[group]] of [[island]]s",
        "plural": "groups of islands",
        "plural_link": "[[group]]s of [[island]]s",
        "fallback": "island group",
    },
    "gulf": {
        "link": True,
        "preposition": "of",
        "holonym_use_the": True,
        "class": "natural feature",
        "default": [True],
    },
    "hamlet": {
        "link": True,
        "fallback": "village",
    },
    "harbor city": {
        "link": "separately",
        "fallback": "city",
    },
    "harbor town": {
        "link": "separately",
        "fallback": "town",
    },
    "harbour city": {
        "link": "separately",
        "fallback": "city",
    },
    "harbour town": {
        "link": "separately",
        "fallback": "town",
    },
    "headland": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "headquarters": {
        "link": "w",
        "fallback": "administrative centre",
    },
    "heath": {
        "link": True,
        "fallback": "moor",
    },
    "hemisphere": {
        "link": True,
        "entry_placetype_use_the": True,
        "fallback": "continental region",
    },
    "highway": {
        "link": True,
        "fallback": "road",
    },
    "hill": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "hill station": {
        "link": "w",
        "fallback": "town",
    },
    "hill town": {
        "link": "w",
        "fallback": "town",
    },
    "historic region": {
        "link": "+w:historical region",
        "fallback": "FORMER geographic region",
    },
    "historical county": {
        "link": "+w:historic county",
        "fallback": "FORMER subpolity",
    },
    "historical region": {
        "link": "w",
        "fallback": "FORMER geographic region",
    },
    "home rule city": {
        "link": "w",
        "fallback": "city",
    },
    "home rule municipality": {
        "link": "w",
        "fallback": "municipality",
    },
    "hot spring": {
        "link": True,
        "fallback": "spring",
    },
    "house": {
        "link": True,
        "fallback": "building",
    },
    "housing estate": {
        "link": True,
        "fallback": "neighborhood",
    },
    "hromada": {
        "link": "w",
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "inactive volcano": {
        "link": "w",
        "fallback": "dormant volcano",
    },
    "independent city": {
        "link": True,
        "fallback": "city",
    },
    "independent town": {
        "link": "+independent city",
        "fallback": "town",
    },
    "Indian reservation": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
        "default": [True],
    },
    "Indian reserve": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
        "default": [True],
    },
    "inland sea": {
        "link": True,
        "fallback": "sea",
    },
    "inner city area": {
        "link": "[[inner city]] [[area]]",
        "fallback": "neighborhood",
    },
    "island": {
        "link": True,
        "preposition": "of",
        "class": "natural feature",
        "default": [True],
    },
    "island country": {
        "link": "w",
        "fallback": "country",
    },
    "island group": {
        "link": "separately",
        "fallback": "island",
    },
    "island municipality": {
        "link": "w",
        "fallback": "municipality",
    },
    "islet": {
        "link": "w",
        "fallback": "island",
    },
    "Israeli settlement": {
        "link": "w",
        "class": "settlement",
        "default": [True],
    },
    "judicial capital": {
        "link": "w",
        "fallback": "capital city",
    },
    "khanate": {
        "link": True,
        "fallback": "polity",
    },
    "kibbutz": {
        "link": True,
        "plural": "kibbutzim",
        "class": "non-admin settlement",
        "default": [True],
    },
    "kingdom": {
        "link": True,
        "fallback": "monarchy",
    },
    "krai": {
        "link": True,
        "preposition": "of",
        "affix_type": "Suf",
        "class": "subpolity",
    },
    "lake": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "largest city": {
        "link": "[[large]]st [[city]]",
        "entry_placetype_use_the": True,
        "fallback": "city",
        "has_neighborhoods": True,
    },
    "league": {
        "link": True,
        "fallback": "confederation",
    },
    "legislative capital": {
        "link": "separately",
        "fallback": "capital city",
    },
    "library": {
        "link": True,
        "fallback": "building",
    },
    "lieutenancy area": {
        "link": "w",
        "fallback": "ceremonial county",
    },
    "local authority district": {
        "link": "w",
        "fallback": "local government district",
    },
    "local government area": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "local council": {
        "link": "+w:local councils of Malta",
        "preposition": "of",
        "fallback": "municipality",
    },
    "local government district": {
        "link": "w",
        "preposition": "of",
        "affix_type": "suf",
        "affix": "district",
        "class": "subpolity",
    },
    "local government district with borough status": {
        "link": "[[w:local government district|local government district]] with [[w:borough status|borough status]]",
        "plural": "local government districts with borough status",
        "plural_link": "[[w:local government district|local government districts]] with [[w:borough status|borough status]]",
        "preposition": "of",
        "affix_type": "suf",
        "affix": "district",
        "class": "subpolity",
    },
    "local urban district": {
        "link": "w",
        "fallback": "unincorporated community",
    },
    "locality": {
        "link": "+w:locality (settlement)",
        "fallback": "village",
    },
    "London borough": {
        "link": "w",
        "preposition": "of",
        "affix_type": "pref",
        "affix": "borough",
        "fallback": "local government district with borough status",
        "has_neighborhoods": True,
    },
    "macroregion": {
        "link": True,
        "fallback": "region",
    },
    "manor": {
        "link": True,
        "fallback": "building",
    },
    "marginal sea": {
        "link": True,
        "preposition": "of",
        "fallback": "sea",
    },
    "market city": {
        "link": "+market town",
        "fallback": "city",
    },
    "market town": {
        "link": True,
        "fallback": "town",
    },
    "massif": {
        "link": True,
        "fallback": "mountain",
    },
    "megacity": {
        "link": True,
        "fallback": "city",
    },
    "metro station": {
        "link": True,
        "class": "man-made structure",
    },
    "metropolitan borough": {
        "link": True,
        "preposition": "of",
        "affix_type": "Pref",
        "fallback": "local government district",
        "has_neighborhoods": True,
    },
    "metropolitan city": {
        "link": True,
        "preposition": "of",
        "affix_type": "Pref",
        "class": "subpolity",
    },
    "metropolitan county": {
        "link": True,
        "fallback": "county",
    },
    "metropolitan municipality": {
        "link": "w",
        "preposition": "of",
        "affix_type": "Suf",
        "fallback": "municipality",
        "class": "subpolity",
    },
    "microdistrict": {
        "link": True,
        "fallback": "neighborhood",
    },
    "microstate": {
        "link": True,
        "fallback": "country",
    },
    "military base": {
        "link": "w",
        "class": "settlement",
        "default": [True],
    },
    "minster town": {
        "link": "separately",
        "fallback": "town",
    },
    "monarchy": {
        "link": True,
        "fallback": "polity",
    },
    "moor": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "moorland": {
        "link": True,
        "fallback": "moor",
    },
    "motorway": {
        "link": True,
        "fallback": "road",
    },
    "mountain": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "mountain indigenous district": {
        "link": "+w:district (Taiwan)",
        "fallback": "district",
    },
    "mountain indigenous township": {
        "link": "+w:township (Taiwan)",
        "fallback": "township",
    },
    "mountain pass": {
        "link": True,
        "plural": "mountain passes",
        "class": "natural feature",
        "default": [True],
    },
    "mountain range": {
        "link": True,
        "fallback": "mountain",
    },
    "mountainous region": {
        "link": "separately",
        "fallback": "region",
    },
    "mukim": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "municipal district": {
        "link": "w",
        "preposition": "of",
        "affix_type": "Pref",
        "fallback": "municipality",
    },
    "municipality": {
        "link": True,
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "subpolity",
    },
    "municipality with city status": {
        "link": "[[municipality]] with [[w:city status|city status]]",
        "plural": "municipalities with city status",
        "plural_link": "[[municipality|municipalities]] with [[w:city status|city status]]",
        "fallback": "municipality",
    },
    "museum": {
        "link": True,
        "fallback": "building",
    },
    "mythological location": {
        "link": "separately",
        "class": "hypothetical location",
        "default": [True],
    },
    "national capital": {
        "link": "w",
        "fallback": "capital city",
    },
    "national park": {
        "link": True,
        "fallback": "park",
    },
    "neighborhood": {
        "link": True,
        "generic_before_non_cities": "in",
        "generic_before_cities": "of",
        "preposition": "of",
        "class": "non-admin settlement",
    },
    "neighbourhood": {
        "link": True,
        "fallback": "neighborhood",
    },
    "new area": {
        "link": "w",
        "preposition": "in",
        "class": "subpolity",
    },
    "new town": {
        "link": True,
        "fallback": "town",
    },
    "non-city capital": {
        "link": "[[capital]]",
        "entry_placetype_use_the": True,
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "capital",
        "default": [True],
    },
    "non-metropolitan county": {
        "link": "w",
        "fallback": "county",
    },
    "non-metropolitan district": {
        "link": "w",
        "fallback": "local government district",
    },
    "non-sovereign kingdom": {
        "link": "+w:non-sovereign monarchy",
        "generic_before_non_cities": "in",
        "class": "subpolity",
        "default": [True],
    },
    "non-sovereign monarchy": {
        "link": "w",
        "fallback": "non-sovereign kingdom",
    },
    "oblast": {
        "link": True,
        "preposition": "of",
        "affix_type": "Suf",
        "class": "subpolity",
    },
    "ocean": {
        "link": True,
        "holonym_use_the": True,
        "class": "natural feature",
        "default": [True],
    },
    "okrug": {
        "link": True,
        "preposition": "of",
        "affix_type": "Suf",
        "class": "subpolity",
    },
    "overseas collectivity": {
        "link": "w",
        "fallback": "collectivity",
    },
    "overseas department": {
        "link": "w",
        "fallback": "department",
    },
    "overseas territory": {
        "link": "w",
        "fallback": "dependent territory",
    },
    "parish": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "parish municipality": {
        "link": "+w:parish municipality (Quebec)",
        "preposition": "of",
        "fallback": "municipality",
        "has_neighborhoods": True,
    },
    "parish seat": {
        "link": True,
        "entry_placetype_use_the": True,
        "preposition": "of",
        "class": "capital",
        "has_neighborhoods": True,
    },
    "park": {
        "link": True,
        "class": "man-made structure",
        "default": [True],
    },
    "pass": {
        "link": "+mountain pass",
        "plural": "passes",
        "fallback": "mountain pass",
    },
    "path": {
        "link": True,
        "fallback": "road",
    },
    "peak": {
        "link": True,
        "fallback": "mountain",
    },
    "peninsula": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "periphery": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "planned community": {
        "link": True,
        "class": "settlement",
        "has_neighborhoods": True,
    },
    "plateau": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "Polish colony": {
        "link": "[[w:colony (Poland)|colony]]",
        "affix_type": "suf",
        "affix": "colony",
        "fallback": "village",
        "has_neighborhoods": True,
    },
    "polity": {
        "link": True,
        "class": "polity",
        "default": [True],
    },
    "populated place": {
        "link": "+w:populated place",
        "fallback": "village",
    },
    "port": {
        "link": True,
        "class": "man-made structure",
        "default": [True],
    },
    "port city": {
        "link": True,
        "fallback": "city",
    },
    "port town": {
        "link": "w",
        "fallback": "town",
    },
    "prefecture": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "prefecture-level city": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "preserved county": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "primary area": {
        "link": "+w:sv:primärområde",
        "fallback": "neighborhood",
    },
    "principality": {
        "link": True,
        "fallback": "monarchy",
    },
    "promontory": {
        "link": True,
        "fallback": "headland",
    },
    "protectorate": {
        "link": True,
        "fallback": "dependent territory",
    },
    "province": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "provincial capital": {
        "link": True,
        "fallback": "capital city",
    },
    "raion": {
        "link": True,
        "preposition": "of",
        "affix_type": "Suf",
        "class": "subpolity",
    },
    "ranch": {
        "link": True,
        "fallback": "farm",
    },
    "range": {
        "link": True,
        "holonym_use_the": True,
        "class": "natural feature",
    },
    "regency": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "region": {
        "link": True,
        "preposition": "of",
        "fallback": "geographic and cultural area",
        "class": "geographic region",
    },
    "regional capital": {
        "link": "separately",
        "fallback": "capital city",
    },
    "regional county municipality": {
        "link": "w",
        "preposition": "of",
        "affix_type": "Suf",
        "fallback": "municipality",
    },
    "regional district": {
        "link": "w",
        "preposition": "of",
        "affix_type": "Pref",
        "fallback": "district",
    },
    "regional municipality": {
        "link": "w",
        "preposition": "of",
        "affix_type": "Pref",
        "fallback": "municipality",
    },
    "regional unit": {
        "link": "w",
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "registration county": {
        "link": "w",
        "fallback": "county",
    },
    "republic": {
        "link": True,
        "fallback": "constituent republic",
    },
    "research base": {
        "link": "+w:research station",
        "fallback": "research station",
    },
    "research station": {
        "link": "w",
        "class": "non-admin settlement",
        "default": [True],
    },
    "reservoir": {
        "link": True,
        "fallback": "lake",
    },
    "residential area": {
        "link": "separately",
        "fallback": "neighborhood",
    },
    "resort city": {
        "link": "w",
        "fallback": "city",
    },
    "resort town": {
        "link": "w",
        "fallback": "town",
    },
    "river": {
        "link": True,
        "generic_before_non_cities": "in",
        "holonym_use_the": True,
        "class": "natural feature",
        "default": [True],
    },
    "river island": {
        "link": "w",
        "fallback": "island",
    },
    "road": {
        "link": True,
        "class": "man-made structure",
        "default": ["Named roads"],
    },
    "Roman province": {
        "link": "w",
        "default": ["Provinces of the Roman Empire"],
        "class": "subpolity",
    },
    "royal borough": {
        "link": "w",
        "preposition": "of",
        "affix_type": "Pref",
        "fallback": "local government district with borough status",
        "has_neighborhoods": True,
    },
    "royal burgh": {
        "link": True,
        "fallback": "borough",
    },
    "royal capital": {
        "link": "w",
        "fallback": "capital city",
    },
    "rural committee": {
        "link": "w",
        "affix_type": "Suf",
        "has_neighborhoods": True,
        "class": "settlement",
    },
    "rural community": {
        "link": "+w:list of municipalities in New_Brunswick#Rural communities",
        "fallback": "municipality",
    },
    "rural hromada": {
        "link": "[[rural]] [[w:hromada|hromada]]",
        "affix_type": "suf",
        "fallback": "hromada",
    },
    "rural municipality": {
        "link": "w",
        "preposition": "of",
        "affix_type": "Pref",
        "fallback": "municipality",
        "has_neighborhoods": True,
    },
    "rural township": {
        "link": "+w:rural township (Taiwan)",
        "fallback": "township",
    },
    "sanctuary": {
        "link": True,
        "fallback": "temple",
    },
    "satrapy": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "sea": {
        "link": True,
        "holonym_use_the": True,
        "class": "natural feature",
        "default": [True],
    },
    "seaport": {
        "link": True,
        "fallback": "port",
    },
    "seat": {
        "link": True,
        "fallback": "administrative centre",
    },
    "self-administered area": {
        "link": "+w:self-administered zone",
        "preposition": "of",
        "class": "subpolity",
    },
    "self-administered division": {
        "link": "w",
        "fallback": "self-administered area",
    },
    "self-administered zone": {
        "link": "w",
        "fallback": "self-administered area",
    },
    "separatist state": {
        "link": "separately",
        "fallback": "unrecognized country",
    },
    "settlement": {
        "link": True,
        "fallback": "village",
    },
    "settlement hromada": {
        "link": "[[w:Populated places in Ukraine#Rural settlements|settlement]] [[w:hromada|hromada]]",
        "affix_type": "suf",
        "fallback": "hromada",
    },
    "sheading": {
        "link": True,
        "fallback": "district",
    },
    "sheep station": {
        "link": True,
        "fallback": "farm",
    },
    "shire": {
        "link": True,
        "fallback": "county",
    },
    "shire county": {
        "link": "w",
        "fallback": "county",
    },
    "shire town": {
        "link": True,
        "fallback": "county seat",
    },
    "ski resort city": {
        "link": "[[ski resort]] [[city]]",
        "fallback": "city",
    },
    "ski resort town": {
        "link": "[[ski resort]] [[town]]",
        "fallback": "town",
    },
    "spa city": {
        "link": "+w:spa town",
        "fallback": "city",
    },
    "spa town": {
        "link": "w",
        "fallback": "town",
    },
    "space station": {
        "link": True,
        "fallback": "research station",
    },
    "special administrative region": {
        "link": "+w:special administrative regions of China",
        "preposition": "of",
        "class": "subpolity",
        "has_neighborhoods": True,
        "suffix": "",
    },
    "special collectivity": {
        "link": "w",
        "fallback": "collectivity",
    },
    "special municipality": {
        "link": "w",
        "fallback": "municipality",
    },
    "special ward": {
        "link": True,
        "fallback": "municipality",
    },
    "spit": {
        "link": True,
        "fallback": "peninsula",
    },
    "spring": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "star": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "state": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "state capital": {
        "link": True,
        "fallback": "capital city",
    },
    "state park": {
        "link": True,
        "fallback": "park",
    },
    "state-level new area": {
        "link": "w",
        "fallback": "new area",
    },
    "statistical region": {
        "link": True,
        "fallback": "administrative region",
    },
    "statutory city": {
        "link": "w",
        "fallback": "city",
    },
    "statutory town": {
        "link": "w",
        "fallback": "town",
    },
    "strait": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "stream": {
        "link": True,
        "fallback": "river",
    },
    "street": {
        "link": True,
        "fallback": "road",
    },
    "strip": {
        "link": True,
        "fallback": "geographic region",
    },
    "strip of land": {
        "link": "[[strip]] of [[land]]",
        "plural": "strips of land",
        "plural_link": "[[strip]]s of [[land]]",
        "fallback": "geographic region",
    },
    "sub-metropolitan city": {
        "link": "+w:List of cities in Nepal#Sub-metropolitan cities",
        "fallback": "city",
    },
    "sub-prefectural city": {
        "link": "w",
        "fallback": "subprovincial city",
    },
    "subdistrict": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
        "default": [True],
    },
    "subdivision": {
        "link": True,
        "preposition": "of",
        "affix_type": "suf",
        "class": "subpolity",
    },
    "submerged ghost town": {
        "link": "[[submerged]] [[ghost town]]",
        "fallback": "ghost town",
    },
    "subnational kingdom": {
        "link": "+w:subnational monarchy",
        "fallback": "non-sovereign kingdom",
    },
    "subnational monarchy": {
        "link": "w",
        "fallback": "non-sovereign kingdom",
    },
    "subprefecture": {
        "link": True,
        "affix_type": "suf",
        "preposition": "of",
        "class": "subpolity",
    },
    "subprovince": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "subprovincial city": {
        "link": "w",
        "fallback": "prefecture-level city",
    },
    "subprovincial district": {
        "link": "w",
        "preposition": "of",
        "class": "subpolity",
    },
    "subregion": {
        "link": True,
        "fallback": "geographic region",
    },
    "suburb": {
        "link": True,
        "generic_before_non_cities": "in",
        "generic_before_cities": "of",
        "preposition": "of",
        "has_neighborhoods": True,
        "class": "non-admin settlement",
    },
    "suburban area": {
        "link": "w",
        "fallback": "suburb",
    },
    "subway station": {
        "link": "w",
        "fallback": "metro station",
    },
    "sum": {
        "link": "+w:sum (administrative division)",
        "fallback": "division",
    },
    "supercontinent": {
        "link": True,
        "fallback": "continent",
    },
    "tehsil": {
        "link": True,
        "affix_type": "suf",
        "no_affix_strings": ["tehsil", "tahsil"],
        "class": "subpolity",
    },
    "temple": {
        "link": True,
        "fallback": "building",
    },
    "territorial authority": {
        "link": "w",
        "fallback": "district",
    },
    "territory": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "theme": {
        "link": "+w:theme (Byzantine district)",
        "preposition": "of",
        "class": "subpolity",
    },
    "town": {
        "link": True,
        "generic_before_non_cities": "in",
        "has_neighborhoods": True,
        "class": "settlement",
        "default": [True],
    },
    "town with bystatus": {
        "link": "[[town]] with [[bystatus#Norwegian Bokmål|bystatus]]",
        "plural": "towns with bystatus",
        "plural_link": "[[town]]s with [[bystatus#Norwegian Bokmål|bystatus]]",
        "fallback": "town",
    },
    "township": {
        "link": True,
        "has_neighborhoods": True,
        "class": "settlement",
        "default": [True],
    },
    "township municipality": {
        "link": "+w:township municipality (Quebec)",
        "preposition": "of",
        "fallback": "municipality",
        "has_neighborhoods": True,
    },
    "traditional county": {
        "link": True,
        "fallback": "county",
    },
    "traditional region": {
        "link": "w",
        "fallback": "FORMER geographic region",
    },
    "trail": {
        "link": True,
        "fallback": "road",
    },
    "treaty port": {
        "link": "w",
        "fallback": "city",
        "class": "settlement",
    },
    "tributary": {
        "link": True,
        "preposition": "of",
        "fallback": "river",
    },
    "underground station": {
        "link": "w",
        "fallback": "metro station",
    },
    "unincorporated area": {
        "link": "w",
        "fallback": "unincorporated community",
    },
    "unincorporated community": {
        "link": True,
        "generic_before_non_cities": "in",
        "class": "non-admin settlement",
    },
    "unincorporated territory": {
        "link": "w",
        "fallback": "territory",
    },
    "union territory": {
        "link": True,
        "preposition": "of",
        "entry_placetype_indefinite_article": "a",
        "class": "subpolity",
    },
    "unitary authority": {
        "link": True,
        "entry_placetype_indefinite_article": "a",
        "fallback": "local government district",
    },
    "unitary district": {
        "link": "w",
        "entry_placetype_indefinite_article": "a",
        "fallback": "local government district",
    },
    "united township municipality": {
        "link": "+w:united township municipality (Quebec)",
        "entry_placetype_indefinite_article": "a",
        "fallback": "township municipality",
        "has_neighborhoods": True,
    },
    "university": {
        "link": True,
        "entry_placetype_indefinite_article": "a",
        "class": "man-made structure",
        "default": [True],
    },
    "unrecognised country": {
        "link": "w",
        "fallback": "unrecognized country",
    },
    "unrecognized country": {
        "link": "w",
        "class": "polity",
        "default": ["Unrecognized and nearly unrecognized countries"],
    },
    "unrecognised state": {
        "link": "w",
        "fallback": "unrecognized country",
    },
    "unrecognized state": {
        "link": "w",
        "fallback": "unrecognized country",
    },
    "urban area": {
        "link": "separately",
        "fallback": "neighborhood",
    },
    "urban hromada": {
        "link": "[[urban]] [[w:hromada|hromada]]",
        "affix_type": "suf",
        "fallback": "hromada",
    },
    "urban service area": {
        "link": "w",
        "fallback": "city",
    },
    "urban township": {
        "link": "w",
        "fallback": "township",
    },
    "urban-type settlement": {
        "link": "w",
        "fallback": "town",
    },
    "valley": {
        "link": True,
        "class": "natural feature",
        "default": [True],
    },
    "viceroyalty": {
        "link": True,
        "fallback": "dependent territory",
    },
    "village": {
        "link": True,
        "generic_before_non_cities": "in",
        "class": "settlement",
        "default": [True],
    },
    "village development committee": {
        "link": "+w:village development committee (Nepal)",
        "fallback": "village",
    },
    "village municipality": {
        "link": "+w:village municipality (Quebec)",
        "preposition": "of",
        "fallback": "municipality",
        "has_neighborhoods": True,
    },
    "voivodeship": {
        "link": True,
        "preposition": "of",
        "class": "subpolity",
    },
    "volcano": {
        "link": True,
        "plural": "volcanoes",
        "class": "natural feature",
        "default": [True, "Mountains"],
    },
    "ward": {
        "link": True,
        "class": "settlement",
        "fallback": "neighborhood",
    },
    "watercourse": {
        "link": True,
        "fallback": "channel",
    },
    "Welsh community": {
        "link": "[[w:community (Wales)|community]]",
        "preposition": "of",
        "affix_type": "suf",
        "affix": "community",
        "has_neighborhoods": True,
        "class": "settlement",
    },
    "zone": {
        "link": "+w:zone#Place names",
        "preposition": "of",
        "class": "subpolity",
    },
}

PLURAL_PLACETYPE_TO_SINGULAR: dict[str, str] = {
    plural: sg_placetype for sg_placetype, spec in PLACETYPE_DATA.items() if (plural := spec.get("plural"))
}

PLACETYPE_ALIASES: dict[str, str] = {
    "acomm": "autonomous community",
    "adr": "administrative region",
    "adterr": "administrative territory",
    "aobl": "autonomous oblast",
    "aokr": "autonomous okrug",
    "ap": "autonomous province",
    "apref": "autonomous prefecture",
    "aprov": "autonomous province",
    "ar": "autonomous region",
    "arch": "archipelago",
    "arep": "autonomous republic",
    "aterr": "autonomous territory",
    "atu": "autonomous territorial unit",
    "bor": "borough",
    "c": "country",
    "can": "canton",
    "carea": "council area",
    "cc": "constituent country",
    "cdblock": "community development block",
    "cdep": "Crown dependency",
    "CDP": "census-designated place",
    "cdp": "census-designated place",
    "clcity": "county-level city",
    "co": "county",
    "cobor": "county borough",
    "colcity": "county-level city",
    "coll": "collectivity",
    "comm": "community",
    "cont": "continent",
    "contr": "continental region",
    "contregion": "continental region",
    "cpar": "civil parish",
    "damun": "direct-administered municipality",
    "dep": "dependency",
    "department capital": "departmental capital",
    "dept": "department",
    "depterr": "dependent territory",
    "dist": "district",
    "distmun": "district municipality",
    "div": "division",
    "emp": "empire",
    "fpref": "French prefecture",
    "gov": "governorate",
    "govnat": "governorate",
    "home-rule city": "home rule city",
    "home-rule municipality": "home rule municipality",
    "inner-city area": "inner city area",
    "ires": "Indian reservation",
    "isl": "island",
    "lbor": "London borough",
    "lga": "local government area",
    "lgarea": "local government area",
    "lgd": "local government district",
    "lgdist": "local government district",
    "metbor": "metropolitan borough",
    "metcity": "metropolitan city",
    "metmun": "metropolitan municipality",
    "mtn": "mountain",
    "mun": "municipality",
    "mundist": "municipal district",
    "nonmetropolitan county": "non-metropolitan county",
    "obl": "oblast",
    "okr": "okrug",
    "p": "province",
    "par": "parish",
    "parmun": "parish municipality",
    "pen": "peninsula",
    "plcity": "prefecture-level city",
    "plcolony": "Polish colony",
    "pref": "prefecture",
    "prefcity": "prefecture-level city",
    "preflcity": "prefecture-level city",
    "prov": "province",
    "r": "region",
    "range": "mountain range",
    "rcm": "regional county municipality",
    "rcomun": "regional county municipality",
    "rdist": "regional district",
    "rep": "republic",
    "rhrom": "rural hromada",
    "riv": "river",
    "rmun": "regional municipality",
    "robor": "royal borough",
    "romp": "Roman province",
    "runit": "regional unit",
    "rurmun": "rural municipality",
    "s": "state",
    "sar": "special administrative region",
    "shrom": "settlement hromada",
    "spref": "subprefecture",
    "sprefcity": "sub-prefectural city",
    "sprovcity": "subprovincial city",
    "submet city": "sub-metropolitan city",
    "submetropolitan city": "sub-metropolitan city",
    "sub-prefecture-level city": "sub-prefectural city",
    "sub-provincial city": "subprovincial city",
    "sub-provincial district": "subprovincial district",
    "terr": "territory",
    "terrauth": "territorial authority",
    "twp": "township",
    "twpmun": "township municipality",
    "uauth": "unitary authority",
    "ucomm": "unincorporated community",
    "udist": "unitary district",
    "uhrom": "urban hromada",
    "uterr": "union territory",
    "utwpmun": "united township municipality",
    "val": "valley",
    "vdc": "village development committee",
    "vil": "village",
    "voi": "voivodeship",
    "wcomm": "Welsh community",
}

no_link_def_article: dict[str, Any] = {"link": False, "article": "the"}
no_link_no_article: dict[str, Any] = {"link": False, "article": False}

PLACETYPE_QUALIFIERS: dict[str, Any] = {
    # generic qualifiers
    "huge": False,
    "tiny": False,
    "large": False,
    "big": False,
    "mid-size": False,
    "mid-sized": False,
    "small": False,
    "sizable": False,
    "important": False,
    "long": False,
    "short": False,
    "major": False,
    "minor": False,
    "high": False,
    "tall": False,
    "low": False,
    "left": False,
    "right": False,
    "modern": False,
    # "former" qualifiers
    "abandoned": True,
    "ancient": True,
    "deserted": True,
    "extinct": True,
    "former": False,
    "historic": "historical",
    "historical": True,
    "medieval": True,
    "mediaeval": True,
    "ruined": True,
    "traditional": True,
    # sea qualifiers
    "coastal": True,
    "inland": True,
    "maritime": True,
    "overseas": True,
    "seaside": True,
    "beachfront": True,
    "beachside": True,
    "riverside": True,
    # lake qualifiers
    "freshwater": True,
    "saltwater": True,
    "endorheic": True,
    "oxbow": True,
    "ox-bow": "[[oxbow]]",
    "tidal": True,
    # land qualifiers
    "hilltop": True,
    "hilly": True,
    "insular": True,
    "peninsular": True,
    "chalk": True,
    "karst": True,
    "limestone": True,
    "mountainous": True,
    "mountaintop": True,
    "alpine": True,
    "volcanic": True,
    # political status qualifiers
    "autonomous": True,
    "incorporated": True,
    "special": True,
    "unincorporated": True,
    "coterminous": True,
    # monetary status/etc. qualifiers
    "fashionable": True,
    "wealthy": True,
    "affluent": True,
    "declining": True,
    # city vs. rural qualifiers
    "urban": True,
    "suburban": True,
    "exurban": True,
    "outlying": True,
    "remote": True,
    "rural": True,
    "outback": True,
    "inner": False,
    "inner-city": True,
    "central": False,
    "outer": False,
    # land use qualifiers
    "residential": True,
    "agricultural": True,
    "business": True,
    "commercial": True,
    "industrial": True,
    # business use qualifiers
    "railroad": True,
    "railway": True,
    "farming": True,
    "fishing": True,
    "mining": True,
    "logging": True,
    "cattle": True,
    # tourism use qualifiers
    "resort": True,
    "spa": True,
    "ski": True,
    # religious qualifiers
    "holy": True,
    "sacred": True,
    "religious": True,
    "secular": True,
    # qualifiers for nonexistent places
    "claimed": False,
    "fictional": True,
    "legendary": True,
    "mythical": True,
    "mythological": True,
    # directional qualifiers
    "northern": False,
    "southern": False,
    "eastern": False,
    "western": False,
    "north": False,
    "south": False,
    "east": False,
    "west": False,
    "northeastern": False,
    "southeastern": False,
    "northwestern": False,
    "southwestern": False,
    "northeast": False,
    "southeast": False,
    "northwest": False,
    "southwest": False,
    # seasonal qualifiers
    "summer": True,
    "winter": True,
    # legal status qualifiers
    "official": True,
    "unofficial": True,
    "de facto": True,
    "de-facto": "[[de facto]]",
    "de jure": True,
    "de-jure": "[[de jure]]",
    # misc. qualifiers
    "planned": True,
    "chartered": True,
    "landlocked": True,
    "uninhabited": True,
    # superlative qualifiers
    "first": no_link_def_article,
    "second": no_link_def_article,
    "third": no_link_def_article,
    "fourth": no_link_def_article,
    "last": no_link_def_article,
    "only": no_link_def_article,
    "sole": no_link_def_article,
    "main": no_link_def_article,
    "largest": no_link_def_article,
    "biggest": no_link_def_article,
    "smallest": no_link_def_article,
    "shortest": no_link_def_article,
    "longest": no_link_def_article,
    "tallest": no_link_def_article,
    "highest": no_link_def_article,
    "lowest": no_link_def_article,
    "leftmost": no_link_def_article,
    "rightmost": no_link_def_article,
    "innermost": no_link_def_article,
    "outermost": no_link_def_article,
    "northernmost": no_link_def_article,
    "southernmost": no_link_def_article,
    "westernmost": no_link_def_article,
    "easternmost": no_link_def_article,
    "northwesternmost": no_link_def_article,
    "southwesternmost": no_link_def_article,
    "northeasternmost": no_link_def_article,
    "southeasternmost": no_link_def_article,
    "several": no_link_no_article,
    "various": no_link_no_article,
    "numerous": no_link_no_article,
    "multiple": no_link_no_article,
    "many": no_link_no_article,
    "other": no_link_no_article,
}

FORMER_QUALIFIERS: dict[str, list[str]] = {
    "abandoned": ["FORMER"],
    "ancient": ["ANCIENT", "FORMER"],
    "former": ["FORMER"],
    "extinct": ["FORMER"],
    "historic": ["FORMER"],
    "historical": ["FORMER"],
    "medieval": ["ANCIENT", "FORMER"],
    "mediaeval": ["ANCIENT", "FORMER"],
    "ruined": ["ANCIENT", "FORMER"],
    "traditional": ["FORMER"],
}

QUALIFIER_TO_PLACETYPE_EQUIVS: dict[str, str] = {
    "fictional": "fictional location",
    "legendary": "mythological location",
    "mythical": "mythological location",
    "mythological": "mythological location",
    "claimed": "claimed political division",
}

PLACENAME_ARTICLE: dict[str, dict[str, str]] = {
    "archipelago": {
        "Cyclades": "the",
        "Dodecanese": "the",
    },
    "country": {
        "Holy Roman Empire": "the",
    },
    "empire": {
        "Holy Roman Empire": "the",
    },
    "island": {
        "North Island": "the",
        "South Island": "the",
    },
    "region": {
        "Balkans": "the",
        "Russian Far East": "the",
        "Caribbean": "the",
        "Caucasus": "the",
        "Middle East": "the",
        "New Territories": "the",
        "North Caucasus": "the",
        "South Caucasus": "the",
        "West Bank": "the",
        "Gaza Strip": "the",
    },
    "valley": {
        "San Fernando Valley": "the",
    },
}

PLACENAME_THE_RE: dict[str, list[str]] = {
    "*": [
        r"^Isle of ",
        r" Islands$",
        r" Mountains$",
        r" Empire$",
        r" Country$",
        r" Region$",
        r" District$",
        r"^City of ",
    ],
    "bay": [r"^Bay of "],
    "lake": [r"^Lake of "],
    "country": [r"^Republic of ", r" Republic$"],
    "republic": [r"^Republic of ", r" Republic$"],
    "region": [r" [Rr]egion$"],
    "river": [r" River$"],
    "local government area": [r"^Shire of "],
    "county": [r"^Shire of "],
    "Indian reservation": [r" Reservation", r" Nation"],
    "tribal jurisdictional area": [r" Reservation", r" Nation"],
}


def remove_links_and_html(text: str) -> str:
    text = re.sub(r"\[\[([^\[\]]+)\]\]", r"\1", text)
    return re.sub(r"<.*?>", "", text)


def maybe_singularize_placetype(
    placetype: str | None, plural_placetype_to_singular: dict[str, str], singularize: Callable[[str], str]
) -> str | None:
    if placetype is None:
        return None
    if placetype in plural_placetype_to_singular:
        return plural_placetype_to_singular[placetype]
    retval = singularize(placetype)
    return None if retval == placetype else retval


def pluralize_placetype(placetype: str, do_ucfirst: bool = False) -> str:
    ptdata = PLACETYPE_DATA.get(placetype)
    if ptdata and ptdata.get("plural"):
        placetype = ptdata["plural"]
    else:
        placetype = pluralize(placetype)
    return placetype[0].upper() + placetype[1:] if do_ucfirst else placetype


def get_placetype_data(placetype: str, from_category: bool = False) -> tuple[str, dict[str, Any], str] | None:
    ptdata = PLACETYPE_DATA.get(placetype)
    if ptdata:
        return placetype, ptdata, "direct"
    if from_category:
        ptdata = PLACETYPE_DATA.get(f"{placetype}!")
        if ptdata:
            return f"{placetype}!", ptdata, "direct-category"
    sg_placetype = maybe_singularize_placetype(placetype, PLURAL_PLACETYPE_TO_SINGULAR, singularize)
    if sg_placetype:
        ptdata = PLACETYPE_DATA.get(sg_placetype)
        if ptdata:
            return sg_placetype, ptdata, "plural"
    return None


def placetype_is_ignorable(placetype: str) -> bool:
    return placetype in {"and", "or"} or placetype.startswith("(")


def resolve_placetype_aliases(placetype: str) -> str:
    return PLACETYPE_ALIASES.get(placetype, placetype)


def get_placetype_prop(placetype: str, key: str) -> Any:
    placetype = resolve_placetype_aliases(placetype)
    return PLACETYPE_DATA.get(placetype, {}).get(key)


def split_qualifiers_from_placetype(placetype: str, no_canon_qualifiers: bool = False) -> list[list[str | None]]:
    splits = [[None, None, resolve_placetype_aliases(placetype)]]
    prev_qualifier = None
    while m := re.match(r"^(.*?) (.*)$", placetype):
        qualifier, reduced_placetype = m[1], m[1]
        canon = PLACETYPE_QUALIFIERS.get(qualifier)
        if canon is None:
            break
        new_qualifier = qualifier
        if isinstance(canon, dict):
            canon = canon.get("link")
        if not no_canon_qualifiers and canon is not False:
            new_qualifier = f"[[{qualifier}]]" if canon is True else canon
        splits.append([prev_qualifier, new_qualifier, resolve_placetype_aliases(reduced_placetype)])
        prev_qualifier = f"{prev_qualifier} {new_qualifier}" if prev_qualifier else new_qualifier
        placetype = reduced_placetype
    return splits


def get_placetype_equivs(placetype: str, props: dict[str, Any] | None) -> list[dict[str, Any]]:
    no_fallback = None
    no_split_qualifiers = None
    no_check_for_inherently_former = None
    from_category = None
    register_former_as_non_former = None
    form_of_directive = None
    if props:
        no_fallback = props.get("no_fallback")
        no_split_qualifiers = props.get("no_split_qualifiers")
        no_check_for_inherently_former = props.get("no_check_for_inherently_former")
        from_category = props.get("from_category")
        register_former_as_non_former = props.get("register_former_as_non_former")
        form_of_directive = props.get("form_of_directive")
    equivs: list[dict[str, Any]] = []

    def insert_placetype_and_fallbacks(qualifier: str | None, placetype: str, form_of_prefix: str | None = None):
        def insert_equiv(pt: str):
            if form_of_prefix:
                insert_placetype_and_fallbacks(qualifier, f"{form_of_prefix} {pt}")
            else:
                equivs.append({"qualifier": qualifier, "placetype": pt})

        result = get_placetype_data(placetype, bool(from_category))
        if result:
            canon_placetype, ptdata, ptmatch = result
            insert_equiv(canon_placetype)
            if no_fallback:
                return
            first_placetype = len(equivs)
            while True:
                pt_value = PLACETYPE_DATA[canon_placetype]
                fallback = pt_value.get("fallback")
                if fallback:
                    insert_equiv(fallback)
                    last_placetype = len(equivs)
                    if last_placetype - first_placetype >= 10:
                        [equivs[i]["placetype"] for i in range(first_placetype, last_placetype)]
                        # Could log or handle fallback loop detection here
                    canon_placetype = fallback
                else:
                    break

    def process_and_insert_placetype(qualifier: str | None, reduced_placetype: str):
        if form_of_directive:
            insert_placetype_and_fallbacks(qualifier, reduced_placetype, form_of_directive)
            if not no_fallback:
                reduced_placetype_equivs = get_placetype_equivs(reduced_placetype, None)
                directive_type = get_equiv_placetype_prop_from_equivs(
                    reduced_placetype_equivs,
                    lambda pt: get_placetype_prop(pt, f"{form_of_directive}_type"),
                ) or get_equiv_placetype_prop_from_equivs(
                    reduced_placetype_equivs,
                    lambda pt: get_placetype_prop(pt, "class"),
                )
                if not directive_type:
                    get_equiv_placetype_prop_from_equivs(
                        reduced_placetype_equivs,
                        lambda pt: PLACETYPE_DATA.get(pt),
                    )
                elif directive_type != "!":
                    insert_placetype_and_fallbacks(qualifier, str(directive_type), form_of_directive)
        else:
            insert_placetype_and_fallbacks(qualifier, reduced_placetype)

    if no_split_qualifiers:
        splits = [[None, None, resolve_placetype_aliases(placetype)]]
    else:
        splits = split_qualifiers_from_placetype(placetype, False)

    for split in splits:
        prev_qualifier, this_qualifier, reduced_placetype = split[0], split[1], split[2]
        if this_qualifier and "[" in this_qualifier:
            unlinked_this_qualifier = remove_links_and_html(this_qualifier)
        else:
            unlinked_this_qualifier = this_qualifier
        qualifiers = FORMER_QUALIFIERS.get(str(unlinked_this_qualifier)) if this_qualifier else None
        if not qualifiers and not no_check_for_inherently_former:
            qualifiers = get_equiv_placetype_prop(
                reduced_placetype,
                lambda pt: get_placetype_prop(str(pt), "inherently_former"),
                {"no_check_for_inherently_former": True},
            )
        if qualifiers:
            reduced_placetype_equivs = get_placetype_equivs(
                str(reduced_placetype), {"no_check_for_inherently_former": True}
            )
            former_type = get_equiv_placetype_prop_from_equivs(
                reduced_placetype_equivs,
                lambda pt: get_placetype_prop(pt, "former_type") or get_placetype_prop(pt, "class"),
            )
            if not former_type:
                get_equiv_placetype_prop_from_equivs(
                    reduced_placetype_equivs,
                    lambda pt: PLACETYPE_DATA.get(pt),
                )
            elif former_type != "!":
                for qualifier in qualifiers:
                    process_and_insert_placetype(prev_qualifier, f"{qualifier} {reduced_placetype}")
                for qualifier in qualifiers:
                    process_and_insert_placetype(prev_qualifier, f"{qualifier} {former_type}")
                if register_former_as_non_former:
                    process_and_insert_placetype(prev_qualifier, str(reduced_placetype))
                if form_of_directive and not no_fallback:
                    for qualifier in qualifiers:
                        insert_placetype_and_fallbacks(prev_qualifier, f"{form_of_directive} {qualifier} place")
                break

        if this_qualifier and this_qualifier in QUALIFIER_TO_PLACETYPE_EQUIVS:
            equivs.append({"qualifier": prev_qualifier, "placetype": QUALIFIER_TO_PLACETYPE_EQUIVS[this_qualifier]})
            break

        qualifier_combined = f"{prev_qualifier} {this_qualifier}" if prev_qualifier else this_qualifier
        process_and_insert_placetype(qualifier_combined, str(reduced_placetype))

        if no_fallback:
            result = get_placetype_data(str(reduced_placetype), bool(from_category))
            if result:
                break

    if (
        form_of_directive
        and not no_fallback
        and (len(splits) > 1 or get_placetype_data(placetype, bool(from_category)))
    ):
        insert_placetype_and_fallbacks(None, f"{form_of_directive} place")

    return equivs


def get_placetype_article(placetype: str, ucfirst: bool = False) -> str | bool | None:
    art = None
    m = re.match(r"^(.*?) (.*)$", placetype)
    if m:
        qualifier, _reduced_placetype = m[1], m[1]
        canon = PLACETYPE_QUALIFIERS.get(qualifier)
        if isinstance(canon, dict):
            art = canon.get("article")
    if art is False:
        return art
    if art is None:
        placetype_use_the = get_placetype_prop(placetype, "entry_placetype_use_the")
        if placetype_use_the:
            art = "the"
        else:
            art = get_placetype_prop(placetype, "entry_placetype_indefinite_article") or singularize(placetype)
    if ucfirst and art:
        art = art[0].upper() + art[1:]
    return art


def get_placetype_entry_preposition(placetype: str) -> str:
    pt_prep = get_placetype_prop(placetype, "preposition")
    return pt_prep or "in"


def get_equiv_placetype_prop_from_equivs(
    equivs: list[dict[str, Any]], fun: Callable[[str], Any], continue_on_nil_only: bool = False
) -> tuple[Any, dict[str, Any] | None]:
    for equiv in equivs:
        retval = fun(equiv["placetype"])
        if (continue_on_nil_only and retval is not None) or (not continue_on_nil_only and retval):
            return retval, equiv
    return None, None


def get_equiv_placetype_prop(
    placetype: str | None,
    fun: Callable[[str | None], Any],
    props: dict[str, Any] | None,
) -> tuple[Any, dict[str, Any] | None]:
    if placetype is None:
        return fun(None), None
    equivs = get_placetype_equivs(placetype, props)
    continue_on_nil_only = props.get("continue_on_nil_only") if props else False
    return get_equiv_placetype_prop_from_equivs(equivs, fun, bool(continue_on_nil_only))


def key_holonym_into_place_desc(place_desc: dict[str, Any], holonym: dict[str, Any]) -> None:
    if not holonym.get("placetype"):
        return

    equiv_placetypes = get_placetype_equivs(holonym["placetype"], {"no_fallback": True})
    unlinked_placename = holonym["unlinked_placename"]
    for equiv in equiv_placetypes:
        placetype = equiv["placetype"]
        if "holonyms_by_placetype" not in place_desc or place_desc["holonyms_by_placetype"] is None:
            place_desc["holonyms_by_placetype"] = {}
        if placetype not in place_desc["holonyms_by_placetype"]:
            place_desc["holonyms_by_placetype"][placetype] = [unlinked_placename]
        else:
            place_desc["holonyms_by_placetype"][placetype].append(unlinked_placename)


def make_placetype_link(link: Any, sg_placetype: str, orig_placetype: str | None) -> str:
    if link is True:
        return orig_placetype or sg_placetype

    if link == "w":
        return orig_placetype or sg_placetype

    if link == "separately":
        if orig_placetype:
            sg_words = sg_placetype.split(" ")
            orig_words = orig_placetype.split(" ")
            result_words = []
            for sg_word, orig_word in zip(sg_words, orig_words):
                if sg_word == orig_word:
                    result_words.append(sg_word)
                else:
                    result_words.append(orig_word)
            return " ".join(result_words)
        else:
            return sg_placetype

    if isinstance(link, str) and link.startswith("+"):
        return orig_placetype or sg_placetype

    if orig_placetype is None:
        return link

    return pluralize(link) if pluralize else link


def get_placetype_display_form(
    placetype: str,
    category_type: Any,
    return_full: bool,
    noerror: bool,
) -> tuple[str | None, dict[str, Any] | None]:
    from_category = bool(category_type)
    result = get_placetype_data(placetype, from_category)
    if result:
        canon_placetype, ptdata, ptmatch = result
        raw_link: Any = None

        def is_linked_string(s: Any) -> bool:
            return isinstance(s, str) and "[[" in s

        if category_type:
            fetched_full = False

            def fetch_maybe_full(prop: str) -> tuple[Any, bool]:
                retval = ptdata.get(f"full_{prop}")
                if retval is not None and return_full:
                    return retval, True
                return ptdata.get(prop), False

            def maybe_prefix(s: str) -> str:
                return f"names of {s}" if return_full and not fetched_full else s

            if category_type == "top-level":
                raw_link, fetched_full = fetch_maybe_full("category_link_top_level")
            elif category_type == "noncity":
                raw_link, fetched_full = fetch_maybe_full("category_link_before_noncity")
            elif category_type == "city":
                raw_link, fetched_full = fetch_maybe_full("category_link_before_city")
            if isinstance(raw_link, str):
                return maybe_prefix(raw_link), ptdata
            elif raw_link is not None:
                return raw_link, ptdata
            raw_link, fetched_full = fetch_maybe_full("category_link")
            if raw_link is False:
                return "", ptdata
            if is_linked_string(raw_link):
                return maybe_prefix(raw_link), ptdata
            if ptmatch == "plural":
                raw_link, fetched_full = fetch_maybe_full("plural_link")
                if raw_link is False:
                    return "", ptdata
                if is_linked_string(raw_link):
                    return maybe_prefix(raw_link), ptdata
            if raw_link is None:
                raw_link, fetched_full = fetch_maybe_full("link")
            if raw_link is False:
                return "", ptdata
            return maybe_prefix(
                make_placetype_link(raw_link, canon_placetype, placetype if placetype != canon_placetype else None)
            ), ptdata
        else:
            if ptmatch == "plural":
                raw_link = ptdata.get("plural_link")
                if is_linked_string(raw_link):
                    return raw_link, ptdata
            if raw_link is None:
                raw_link = ptdata.get("link")
            return make_placetype_link(
                raw_link, canon_placetype, placetype if placetype != canon_placetype else None
            ), ptdata
    return None, None


def resolve_unlinked_placename_display_aliases(placetype: str, placename: str) -> str:
    equiv_placetypes = get_placetype_equivs(placetype, None)
    equiv_placetypes = [equiv["placetype"] for equiv in equiv_placetypes]
    all_display_aliases_found: list[Any] = []
    all_others_found: list[Any] = []
    for group, key, spec in iterate_matching_location(
        placetypes=equiv_placetypes,
        placename=placename,
        alias_resolution="display",
    ):
        if getattr(spec, "alias_of", None) and getattr(spec, "display", None):
            all_display_aliases_found.append((group, key, spec, getattr(spec, "display_as_full", None)))
        else:
            all_others_found.append((group, key, spec))
    if not all_display_aliases_found:
        return placename
    group, key, spec, as_full = all_display_aliases_found[0]
    full, elliptical = key_to_placename(group, key)
    return full if as_full else elliptical


def resolve_placename_display_aliases(placetype: str, placename: str) -> str:
    # If the placename is a link, apply the alias inside the link.
    # Matches both piped and unpiped links.
    if not (m := re.match(r"^\[\[([^|\[\]]+)\|?([^\|\[\]]*)\]\]$", placename)):
        return resolve_unlinked_placename_display_aliases(placetype, placename)
    link, linktext = m[1], m[1]
    return (
        resolve_unlinked_placename_display_aliases(placetype, linktext)
        if linktext != ""
        else resolve_unlinked_placename_display_aliases(placetype, link)
    )


def get_holonyms_to_check(
    place_desc: dict[str, Any], first_holonym_index: int | None, include_raw_text_holonyms: bool
) -> tuple[Callable[[dict[str, Any], int], Any], dict[str, Any], int]:
    stop_at_also = first_holonym_index is not None

    def iterator(place_desc: dict[str, Any], index: int):
        while True:
            index += 1
            this_holonym = place_desc["holonyms"][index] if index < len(place_desc["holonyms"]) else None
            if this_holonym is None or (
                stop_at_also
                and index > (first_holonym_index or 0)
                and getattr(this_holonym, "continue_cat_loop", False)
            ):
                return None
            if include_raw_text_holonyms or getattr(this_holonym, "placetype", None):
                return index, this_holonym

    return iterator, place_desc, (first_holonym_index - 1 if first_holonym_index is not None else 0)


def iterate_matching_holonym_location(data: dict[str, Any]) -> Any:
    holonym_placetype = data["holonym_placetype"]
    holonym_placename = data["holonym_placename"]
    holonym_index = data.get("holonym_index")
    place_desc = data["place_desc"]
    matching_location_iterator = iterate_matching_location(
        placetypes=holonym_placetype,
        placename=holonym_placename,
    )

    def generator():
        while True:
            group, key, spec = matching_location_iterator()
            if not group:
                return
            container_trail: list[Any] = []
            containers_mismatch = False
            for containers in spec.iterate_containers(group, key, spec):  # Using method from spec or replace as needed
                container_trail.append(containers)
                match_at_level = False
                mismatch_at_level = False
                iterator, pd, idx = get_holonyms_to_check(
                    place_desc, holonym_index + 1 if holonym_index else None, False
                )
                while True:
                    res = iterator(pd, idx)
                    if res is None:
                        break
                    other_holonym_index, other_holonym = res
                    idx = other_holonym_index
                    other_source_holonym = getattr(other_holonym, "augmented_from_holonym", None)
                    if (
                        other_source_holonym
                        and getattr(other_source_holonym, "placetype", None) == holonym_placetype
                        and getattr(other_source_holonym, "unlinked_placename", None) != holonym_placename
                    ):
                        continue
                    holonym_matches_at_level = False
                    holonym_exists_with_same_placetype = False
                    for container in containers:
                        if not getattr(container.spec, "no_check_holonym_mismatch", False):
                            full_container_placename, elliptical_container_placename = key_to_placename(
                                container.group, container.key
                            )
                            placetypes = container.spec.placetype
                            if not isinstance(placetypes, list):
                                placetypes = [placetypes]
                            placetype_equivs: list[Any] = []
                            for pt in placetypes:
                                m_table_extend(placetype_equivs, get_placetype_equivs(pt, None))
                            this_holonym_matches = get_equiv_placetype_prop_from_equivs(
                                placetype_equivs,
                                lambda placetype: (
                                    getattr(other_holonym, "placetype", None) == placetype
                                    and getattr(other_holonym, "unlinked_placename", None)
                                    in [full_container_placename, elliptical_container_placename]
                                ),
                            )
                            if this_holonym_matches:
                                holonym_matches_at_level = True
                                break
                            this_holonym_exists_with_same_placetype = get_equiv_placetype_prop_from_equivs(
                                placetype_equivs,
                                lambda placetype: getattr(other_holonym, "placetype", None) == placetype,
                            )
                            if this_holonym_exists_with_same_placetype:
                                # Check for alias match
                                for oh_group, oh_key, oh_spec, oh_container_trail in iterate_matching_holonym_location(
                                    {
                                        "holonym_placetype": getattr(other_holonym, "placetype", None),
                                        "holonym_placename": getattr(other_holonym, "unlinked_placename", None),
                                        "holonym_index": other_holonym_index,
                                        "place_desc": place_desc,
                                    }
                                ):
                                    oh_full_placename, oh_elliptical_placename = key_to_placename(oh_group, oh_key)
                                    if (
                                        oh_full_placename == full_container_placename
                                        or oh_elliptical_placename == elliptical_container_placename
                                    ):
                                        this_holonym_matches = True
                                        break
                                if this_holonym_matches:
                                    holonym_matches_at_level = True
                                    break
                                else:
                                    holonym_exists_with_same_placetype = True
                    if holonym_matches_at_level:
                        match_at_level = True
                        break
                    if holonym_exists_with_same_placetype:
                        mismatch_at_level = True
                if not match_at_level and mismatch_at_level:
                    containers_mismatch = True
                    break
            if not containers_mismatch:
                yield group, key, spec, container_trail

    return generator()


def find_matching_holonym_location(data: dict[str, Any]):
    all_found: list[Any] = []
    all_found.extend(
        (group, key, spec, container_trail)
        for group, key, spec, container_trail in iterate_matching_holonym_location(data)
    )
    if not all_found:
        return None
    elif len(all_found) > 1:
        holonym_placetype = data["holonym_placetype"]
        if isinstance(holonym_placetype, list):
            holonym_placetype = ",".join(holonym_placetype)
        found_keys = [key for _, key, _, _ in all_found]
        raise RuntimeError(
            f"Found multiple matching locations for holonym '{holonym_placetype}/{data['holonym_placename']}'; specify disambiguating context in the containing holonyms: {found_keys}"
        )
    else:
        return all_found[0]


def check_already_seen_string(holonym_placename: str, already_seen_strings: Sequence[str]) -> bool:
    canon_placename = holonym_placename.lower()
    if not isinstance(already_seen_strings, list | tuple):
        already_seen_strings = [already_seen_strings]
    return any(already_seen_string in canon_placename for already_seen_string in already_seen_strings)
