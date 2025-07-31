"""
Source: https://en.wiktionary.org/w/index.php?title=Module:place/locations&oldid=85452422
"""

import re
from collections.abc import Callable, Iterator, Sequence
from typing import Any


def make_key_to_placename(
    container_patterns: str | Sequence[str] | None, divtype_patterns: str | Sequence[str] | None
) -> Callable[[str], tuple[str, str]]:
    if isinstance(container_patterns, str) or container_patterns is None:
        container_patterns = [container_patterns] if container_patterns else []
    if isinstance(divtype_patterns, str) or divtype_patterns is None:
        divtype_patterns = [divtype_patterns] if divtype_patterns else []

    def key_to_placename(key: str) -> tuple[str, str]:
        full_placename = key
        # Remove first matching container pattern
        for container_pattern in container_patterns:
            if container_pattern:
                new_full, nsubs = re.subn(container_pattern, "", full_placename)
                if nsubs > 0:
                    full_placename = new_full
                    break
        elliptical_placename = full_placename
        # Remove first matching divtype pattern
        for divtype_pattern in divtype_patterns:
            if divtype_pattern:
                new_elliptical, nsubs = re.subn(divtype_pattern, "", elliptical_placename)
                if nsubs > 0:
                    elliptical_placename = new_elliptical
                    break
        return full_placename, elliptical_placename

    return key_to_placename


def make_placename_to_key(
    container_suffix: str | None,
    divtype_suffix: str = "",
) -> Callable[[str], str]:
    """
    Returns a function that takes a placename and creates a key by appending
    divtype_suffix if not already present, and then container_suffix if provided.
    """

    def placename_to_key(placename: str) -> str:
        key = placename
        if divtype_suffix and not key.endswith(divtype_suffix):
            key += divtype_suffix
        if container_suffix:
            key += container_suffix
        return key

    return placename_to_key


def make_canonicalize_key_container(
    suffix: str | None, placetype: str | None
) -> Callable[[str | dict[str, Any]], dict[str, Any]]:
    """
    Returns a function that takes a container (str or dict) and returns a dict with key and placetype
    if a string was given, or returns the original dict if not a string.
    """

    def canonicalize(container: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(container, str):
            return {"key": container + (suffix or ""), "placetype": placetype}
        else:
            return container

    return canonicalize


def canonicalize_continent_container(key: Any, continents: dict[str, dict[str, Any]]) -> Any:
    if not isinstance(key, str):
        return key
    continent_info = continents.get(key)
    if continent_info:
        return {"key": key, "placetype": continent_info["placetype"]}
    return None


CONTINENTS = {
    "Earth": {
        "the": True,
        "placetype": "planet",
        "addl_parents": ["nature"],
        "fulldesc": "=the planet Earth and the features found on it",
    },
    "Africa": {
        "placetype": "continent",
        "container": {"key": "Earth", "placetype": "planet"},
    },
    "America": {
        "placetype": ["supercontinent", "continent"],
        "container": {"key": "Earth", "placetype": "planet"},
        "keydesc": "America, in the sense of North America and South America combined",
        "wp": "Americas",
    },
    "Americas": {
        "alias_of": "America",
        "the": True,
    },
    "North America": {
        "placetype": "continent",
        "container": {"key": "America", "placetype": "supercontinent"},
    },
    "Caribbean": {
        "the": True,
        "placetype": ["continental region", "region"],
        "container": {"key": "North America", "placetype": "continent"},
    },
    "Central America": {
        "placetype": ["continental region", "region"],
        "container": {"key": "North America", "placetype": "continent"},
    },
    "South America": {
        "placetype": "continent",
        "container": {"key": "America", "placetype": "supercontinent"},
    },
    "Antarctica": {
        "placetype": "continent",
        "container": {"key": "Earth", "placetype": "planet"},
        "fulldesc": "=the territory of Antarctica",
    },
    "Eurasia": {
        "placetype": ["supercontinent", "continent"],
        "container": {"key": "Earth", "placetype": "planet"},
        "keydesc": "Eurasia, i.e. Europe and Asia together",
    },
    "Asia": {
        "placetype": "continent",
        "container": {"key": "Eurasia", "placetype": "supercontinent"},
    },
    "Europe": {
        "placetype": "continent",
        "container": {"key": "Eurasia", "placetype": "supercontinent"},
    },
    "Oceania": {
        "placetype": "continent",
        "container": {"key": "Earth", "placetype": "planet"},
    },
    "Melanesia": {
        "placetype": ["continental region", "region"],
        "container": {"key": "Oceania", "placetype": "continent"},
    },
    "Micronesia": {
        "placetype": ["continental region", "region"],
        "container": {"key": "Oceania", "placetype": "continent"},
    },
    "Polynesia": {
        "placetype": ["continental region", "region"],
        "container": {"key": "Oceania", "placetype": "continent"},
    },
}

CONTINENTS_GROUP = {
    "default_overriding_bare_label_parents": {},
    "default_divs": [{"type": "countries", "prep": "in"}],
    "default_no_include_container_in_desc": True,
    "default_no_container_cat": True,
    "default_no_container_parent": True,
    "default_no_auto_augment_container": True,
    "default_no_generic_place_cat": True,
    "default_no_check_holonym_mismatch": True,
    "data": CONTINENTS,
}

COUNTRIES = {
    "Afghanistan": {"container": "Asia", "divs": ["provinces", "districts"]},
    "Albania": {
        "container": "Europe",
        "divs": ["counties", "municipalities", "communes", {"type": "administrative units"}],
        "british_spelling": True,
    },
    "Algeria": {"container": "Africa", "divs": ["provinces", "communes", "districts", "municipalities"]},
    "Andorra": {"container": "Europe", "divs": ["parishes"], "british_spelling": True},
    "Angola": {"container": "Africa", "divs": ["provinces", "municipalities"]},
    "Antigua and Barbuda": {"container": "Caribbean", "divs": ["provinces"], "british_spelling": True},
    "Argentina": {"container": "South America", "divs": ["provinces", "departments", "municipalities"]},
    "Armenia": {
        "container": ["Europe", "Asia"],
        "divs": ["provinces", "districts", "municipalities"],
        "british_spelling": True,
    },
    "Republic of Armenia": {"alias_of": "Armenia", "the": True},
    "Australia": {
        "container": "Oceania",
        "divs": [
            {"type": "states"},
            {"type": "territories"},
            {"type": "ABBREVIATION_OF states"},
            {"type": "ABBREVIATION_OF territories"},
            "local government areas",
            "dependent territories",
        ],
        "british_spelling": True,
    },
    "Austria": {"container": "Europe", "divs": ["states", "districts", "municipalities"], "british_spelling": True},
    "Azerbaijan": {"container": ["Europe", "Asia"], "divs": ["districts", "municipalities"], "british_spelling": True},
    "Bahamas": {"the": True, "container": "Caribbean", "divs": ["districts"], "british_spelling": True, "wp": "The %l"},
    "Bahrain": {"container": "Asia", "divs": ["governorates"]},
    "Bangladesh": {"container": "Asia", "divs": ["divisions", "districts", "municipalities"], "british_spelling": True},
    "Barbados": {"container": "Caribbean", "divs": ["parishes"], "british_spelling": True},
    "Belarus": {"container": "Europe", "divs": ["regions", "districts"], "british_spelling": True},
    "Belgium": {"container": "Europe", "divs": ["regions", "provinces", "municipalities"], "british_spelling": True},
    "Belize": {"container": "Central America", "divs": ["districts"], "british_spelling": True},
    "Benin": {"container": "Africa", "divs": ["departments", "communes"]},
    "Bhutan": {"container": "Asia", "divs": ["districts", "gewogs"]},
    "Bolivia": {"container": "South America", "divs": ["provinces", "departments", "municipalities"]},
    "Bosnia and Herzegovina": {
        "container": "Europe",
        "divs": ["entities", "cantons", "municipalities"],
        "british_spelling": True,
    },
    "Bosnia and Hercegovina": {"alias_of": "Bosnia and Herzegovina", "display": True},
    "Bosnia": {"alias_of": "Bosnia and Herzegovina", "display": True},
    "Botswana": {"container": "Africa", "divs": ["districts", "subdistricts"], "british_spelling": True},
    "Brazil": {
        "container": "South America",
        "divs": ["states", "municipalities", "macroregions", {"type": "ABBREVIATION_OF states"}],
    },
    "Brunei": {"container": "Asia", "divs": ["districts", "mukims"], "british_spelling": True},
    "Bulgaria": {"container": "Europe", "divs": ["provinces", "municipalities"], "british_spelling": True},
    "Burkina Faso": {"container": "Africa", "divs": ["regions", "departments", "provinces"]},
    "Burundi": {"container": "Africa", "divs": ["provinces", "communes"]},
    "Cambodia": {"container": "Asia", "divs": ["provinces", "districts"]},
    "Cameroon": {"container": "Africa", "divs": ["regions", "departments"]},
    "Canada": {
        "container": "North America",
        "divs": [
            {"type": "provinces"},
            {"type": "territories"},
            {"type": "ABBREVIATION_OF provinces"},
            {"type": "ABBREVIATION_OF territories"},
            "counties",
            "districts",
            "municipalities",
            "regional municipalities",
            "rural municipalities",
            "parishes",
            "Indian reserves",
            "census divisions",
            {"type": "townships", "prep": "in"},
        ],
        "british_spelling": True,
    },
    "Cape Verde": {"container": "Africa", "divs": ["municipalities", "parishes"]},
    "Central African Republic": {"the": True, "container": "Africa", "divs": ["prefectures", "subprefectures"]},
    "Chad": {"container": "Africa", "divs": ["regions", "departments"]},
    "Chile": {"container": "South America", "divs": ["regions", "provinces", "communes"]},
    "China": {
        "container": "Asia",
        "divs": [
            {"type": "provinces"},
            {"type": "autonomous regions"},
            {"type": "FORMER provinces"},
            "special administrative regions",
            "prefectures",
            {"type": "FORMER prefectures"},
            "prefecture-level cities",
            {"type": "counties"},
            {"type": "county-level cities"},
            {"type": "FORMER counties"},
            {"type": "FORMER county-level cities"},
            "districts",
            {"type": "FORMER districts"},
            "subdistricts",
            "townships",
            "municipalities",
            {"type": "direct-administered municipalities"},
        ],
    },
    "People's Republic of China": {"alias_of": "China", "the": True},
    "Colombia": {"container": "South America", "divs": ["departments", "municipalities"]},
    "Comoros": {"the": True, "container": "Africa", "divs": ["autonomous islands"]},
    "Costa Rica": {"container": "Central America", "divs": ["provinces", "cantons"]},
    "Croatia": {"container": "Europe", "divs": ["counties", "municipalities"], "british_spelling": True},
    "Cuba": {"container": "Caribbean", "divs": ["provinces", "municipalities"]},
    "Cyprus": {"container": ["Europe", "Asia"], "divs": ["districts"], "british_spelling": True},
    "Czech Republic": {
        "the": True,
        "container": "Europe",
        "divs": ["regions", "districts", "municipalities"],
        "british_spelling": True,
    },
    "Czechia": {"alias_of": "Czech Republic"},
    "Democratic Republic of the Congo": {"the": True, "container": "Africa", "divs": ["provinces", "territories"]},
    "Congo": {"alias_of": "Democratic Republic of the Congo", "display": True, "the": True},
    "Denmark": {
        "container": "Europe",
        "divs": ["regions", "municipalities", "dependent territories"],
        "british_spelling": True,
    },
    "Djibouti": {"container": "Africa", "divs": ["regions", "districts"]},
    "Dominica": {"container": "Caribbean", "divs": ["parishes"], "british_spelling": True},
    "Dominican Republic": {
        "the": True,
        "container": "Caribbean",
        "divs": ["provinces", "municipalities"],
        "keydesc": "the [[Dominican Republic]], the country that shares the [[Caribbean]] island of [[Hispaniola]] with [[Haiti]]",
    },
    "East Timor": {"container": "Asia", "divs": ["municipalities"], "wp": "Timor-Leste"},
    "Timor-Leste": {"alias_of": "East Timor", "display": True},
    "Ecuador": {"container": "South America", "divs": ["provinces", "cantons"]},
    "Egypt": {"container": "Africa", "divs": ["governorates", "regions"], "british_spelling": True},
    "El Salvador": {"container": "Central America", "divs": ["departments", "municipalities"]},
    "Equatorial Guinea": {"container": "Africa", "divs": ["provinces"]},
    "Eritrea": {"container": "Africa", "divs": ["regions", "subregions"]},
    "Estonia": {"container": "Europe", "divs": ["counties", "municipalities"], "british_spelling": True},
    "Eswatini": {"container": "Africa", "british_spelling": True},
    "Swaziland": {"alias_of": "Eswatini", "display": True},
    "Ethiopia": {"container": "Africa", "divs": ["regions", "zones"]},
    "Federated States of Micronesia": {"the": True, "container": "Micronesia", "divs": ["states"]},
    "Micronesia": {"alias_of": "Federated States of Micronesia"},
    "Fiji": {"container": "Melanesia", "divs": ["divisions", "provinces"], "british_spelling": True},
    "Finland": {"container": "Europe", "divs": ["regions", "municipalities"], "british_spelling": True},
    "France": {
        "container": "Europe",
        "divs": [
            "regions",
            "cantons",
            "collectivities",
            "communes",
            {"type": "municipalities"},
            "departments",
            {"type": "prefectures"},
            {"type": "French prefectures"},
            "dependent territories",
            "territories",
            "provinces",
        ],
        "british_spelling": True,
    },
    "Gabon": {"container": "Africa", "divs": ["provinces", "departments"]},
    "Gambia": {
        "the": True,
        "container": "Africa",
        "divs": ["divisions", "districts"],
        "british_spelling": True,
        "wp": "The %l",
    },
    "Georgia": {
        "container": ["Europe", "Asia"],
        "divs": ["regions", "districts"],
        "keydesc": "the country of [[Georgia]], in [[Eurasia]]",
        "british_spelling": True,
        "wp": "%l (country)",
    },
    "Germany": {
        "container": "Europe",
        "divs": ["states", "regions", "municipalities", "districts"],
        "british_spelling": True,
    },
    "Ghana": {"container": "Africa", "divs": ["regions", "districts"], "british_spelling": True},
    "Greece": {
        "container": "Europe",
        "divs": ["regions", "regional units", "municipalities", {"type": "peripheries"}],
        "british_spelling": True,
    },
    "Grenada": {"container": "Caribbean", "divs": ["parishes"], "british_spelling": True},
    "Guatemala": {"container": "Central America", "divs": ["departments", "municipalities"]},
    "Guinea": {"container": "Africa", "divs": ["regions", "prefectures"]},
    "Guinea-Bissau": {"container": "Africa", "divs": ["regions"]},
    "Guyana": {"container": "South America", "divs": ["regions"], "british_spelling": True},
    "Haiti": {"container": "Caribbean", "divs": ["departments", "arrondissements"]},
    "Honduras": {"container": "Central America", "divs": ["departments", "municipalities"]},
    "Hungary": {"container": "Europe", "divs": ["counties", "districts"], "british_spelling": True},
    "Iceland": {"container": "Europe", "divs": ["regions", "municipalities", "counties"], "british_spelling": True},
    "India": {
        "container": "Asia",
        "divs": [
            {"type": "states"},
            {"type": "union territories"},
            {"type": "ABBREVIATION_OF states"},
            {"type": "ABBREVIATION_OF union territories"},
            "divisions",
            "districts",
            "municipalities",
        ],
        "british_spelling": True,
    },
    "Indonesia": {"container": "Asia", "divs": ["regencies", "provinces", {"type": "ABBREVIATION_OF provinces"}]},
    "Iran": {"container": "Asia", "divs": ["provinces", "counties"]},
    "Iraq": {"container": "Asia", "divs": ["governorates", "districts"]},
    "Ireland": {
        "container": "Europe",
        "addl_parents": ["British Isles"],
        "divs": ["counties", "districts", "provinces"],
        "british_spelling": True,
        "wp": "Republic of %l",
    },
    "Republic of Ireland": {"alias_of": "Ireland", "the": True},
    "Israel": {"container": "Asia", "divs": ["districts"]},
    "Italy": {
        "container": "Europe",
        "divs": ["regions", "provinces", "metropolitan cities", "municipalities", {"type": "autonomous regions"}],
        "british_spelling": True,
    },
    "Ivory Coast": {"container": "Africa", "divs": ["districts", "regions"]},
    "Côte d'Ivoire": {"alias_of": "Ivory Coast"},
    "Jamaica": {"container": "Caribbean", "divs": ["parishes"], "british_spelling": True},
    "Japan": {"container": "Asia", "divs": ["prefectures", "subprefectures", "municipalities"]},
    "Jordan": {"container": "Asia", "divs": ["governorates"]},
    "Kazakhstan": {"container": ["Asia", "Europe"], "divs": ["regions", "districts"]},
    "Kenya": {"container": "Africa", "divs": ["counties"], "british_spelling": True},
    "Kiribati": {"container": "Micronesia", "british_spelling": True},
    "Kosovo": {"container": "Europe", "divs": ["districts", "municipalities"], "british_spelling": True},
    "Kuwait": {"container": "Asia", "divs": ["governorates", "areas"]},
    "Kyrgyzstan": {"container": "Asia", "divs": ["regions", "districts"]},
    "Laos": {"container": "Asia", "divs": ["provinces", "districts"]},
    "Latvia": {"container": "Europe", "divs": ["municipalities"], "british_spelling": True},
    "Lebanon": {"container": "Asia", "divs": ["governorates", "districts"]},
    "Lesotho": {"container": "Africa", "divs": ["districts"], "british_spelling": True},
    "Liberia": {"container": "Africa", "divs": ["counties", "districts"]},
    "Libya": {"container": "Africa", "divs": ["districts", "municipalities"]},
    "Liechtenstein": {"container": "Europe", "divs": ["municipalities"], "british_spelling": True},
    "Lithuania": {"container": "Europe", "divs": ["counties", "municipalities"], "british_spelling": True},
    "Luxembourg": {"container": "Europe", "divs": ["cantons", "districts"], "british_spelling": True},
    "Madagascar": {"container": "Africa", "divs": ["regions", "districts"]},
    "Malawi": {"container": "Africa", "divs": ["regions", "districts"], "british_spelling": True},
    "Malaysia": {"container": "Asia", "divs": ["states", "federal territories", "districts"], "british_spelling": True},
    "Maldives": {
        "the": True,
        "container": "Asia",
        "divs": ["provinces", "administrative atolls"],
        "british_spelling": True,
    },
    "Mali": {"container": "Africa", "divs": ["regions", "cercles"]},
    "Malta": {"container": "Europe", "divs": ["regions", "local councils"], "british_spelling": True},
    "Marshall Islands": {"the": True, "container": "Micronesia", "divs": ["municipalities"]},
    "Mauritania": {"container": "Africa", "divs": ["regions", "departments"]},
    "Mauritius": {"container": "Africa", "divs": ["districts"], "british_spelling": True},
    "Mexico": {
        "container": "North America",
        "addl_parents": ["Central America"],
        "divs": ["states", "municipalities", {"type": "ABBREVIATION_OF states"}],
    },
    "Moldova": {
        "container": "Europe",
        "divs": [{"type": "districts"}, {"type": "autonomous territorial units"}, "communes", "municipalities"],
        "british_spelling": True,
    },
    "Monaco": {
        "placetype": ["city-state", "country"],
        "container": "Europe",
        "bare_category_parent_type": {"type": "countries", "prep": "in"},
        "is_city": True,
        "british_spelling": True,
    },
    "Mongolia": {"container": "Asia", "divs": ["provinces", "districts"]},
    "Montenegro": {"container": "Europe", "divs": ["municipalities"]},
    "Morocco": {"container": "Africa", "divs": ["regions", "prefectures", "provinces"]},
    "Mozambique": {"container": "Africa", "divs": ["provinces", "districts"]},
    "Myanmar": {
        "container": "Asia",
        "divs": [
            "regions",
            "states",
            "union territories",
            {"type": "self-administered zones"},
            {"type": "self-administered divisions"},
            "districts",
        ],
    },
    "Burma": {"alias_of": "Myanmar"},
    "Namibia": {"container": "Africa", "divs": ["regions", "constituencies"], "british_spelling": True},
    "Nauru": {"container": "Micronesia", "divs": ["districts"], "british_spelling": True},
    "Nepal": {"container": "Asia", "divs": ["provinces", "districts"]},
    "Netherlands": {
        "the": True,
        "placetype": ["country", "constituent country"],
        "container": "Europe",
        "divs": [
            "provinces",
            "municipalities",
            {"type": "FORMER municipalities"},
            "dependent territories",
            "constituent countries",
        ],
        "british_spelling": True,
    },
    "New Zealand": {
        "container": "Polynesia",
        "divs": ["regions", "dependent territories", "territorial authorities", {"type": "districts"}],
        "british_spelling": True,
    },
    "Nicaragua": {"container": "Central America", "divs": ["departments", "municipalities"]},
    "Niger": {"container": "Africa", "divs": ["regions", "departments"]},
    "Nigeria": {
        "container": "Africa",
        "divs": ["states", {"type": "federal territories"}, "local government areas"],
        "british_spelling": True,
    },
    "North Korea": {"container": "Asia", "addl_parents": ["Korea"], "divs": ["provinces", "counties"]},
    "North Macedonia": {"container": "Europe", "divs": ["regions", "municipalities"], "british_spelling": True},
    "Macedonia": {"alias_of": "North Macedonia", "display": True},
    "Republic of North Macedonia": {"alias_of": "North Macedonia", "the": True},
    "Republic of Macedonia": {"alias_of": "North Macedonia", "the": True},
    "Norway": {
        "container": "Europe",
        "divs": ["counties", "municipalities", "dependent territories", "districts", "unincorporated areas"],
        "british_spelling": True,
    },
    "Oman": {"container": "Asia", "divs": ["governorates", "provinces"]},
    "Pakistan": {
        "container": "Asia",
        "divs": [
            {"type": "provinces"},
            {"type": "administrative territories"},
            {"type": "federal territories"},
            {"type": "territories"},
            "divisions",
            "districts",
        ],
        "british_spelling": True,
    },
    "Palau": {"container": "Micronesia", "divs": ["states"]},
    "Palestine": {"container": "Asia", "divs": ["governorates"]},
    "State of Palestine": {"alias_of": "Palestine", "the": True},
    "Panama": {"container": "Central America", "divs": ["provinces", "districts"]},
    "Papua New Guinea": {"container": "Melanesia", "divs": ["provinces", "districts"], "british_spelling": True},
    "Paraguay": {"container": "South America", "divs": ["departments", "districts"]},
    "Peru": {"container": "South America", "divs": ["regions", "provinces", "districts"]},
    "Philippines": {
        "the": True,
        "container": "Asia",
        "divs": ["regions", "provinces", "districts", "municipalities", "barangays"],
    },
    "Poland": {
        "divs": ["voivodeships", "counties", {"type": "Polish colonies"}],
        "container": "Europe",
        "british_spelling": True,
    },
    "Portugal": {
        "container": "Europe",
        "divs": [{"type": "autonomous regions"}, {"type": "districts"}, "provinces", "municipalities"],
        "british_spelling": True,
    },
    "Qatar": {"container": "Asia", "divs": ["municipalities", "zones"]},
    "Republic of the Congo": {"the": True, "container": "Africa", "divs": ["departments", "districts"]},
    "Congo Republic": {"alias_of": "Republic of the Congo", "display": True, "the": True},
    "Romania": {
        "container": "Europe",
        "divs": ["regions", "counties", "communes", {"type": "ABBREVIATION_OF counties"}],
        "british_spelling": True,
    },
    "Russia": {
        "container": ["Europe", "Asia"],
        "divs": [
            "federal subjects",
            "republics",
            "autonomous oblasts",
            "autonomous okrugs",
            "oblasts",
            "krais",
            "federal cities",
            "districts",
            "federal districts",
        ],
        "british_spelling": True,
    },
    "Rwanda": {"container": "Africa", "divs": ["provinces", "districts"]},
    "Saint Kitts and Nevis": {"container": "Caribbean", "divs": ["parishes"], "british_spelling": True},
    "Saint Lucia": {"container": "Caribbean", "divs": ["districts"], "british_spelling": True},
    "Saint Vincent and the Grenadines": {"container": "Caribbean", "divs": ["parishes"], "british_spelling": True},
    "Samoa": {"container": "Polynesia", "divs": ["districts"], "british_spelling": True},
    "San Marino": {"container": "Europe", "divs": ["municipalities"], "british_spelling": True},
    "São Tomé and Príncipe": {"container": "Africa", "divs": ["districts"]},
    "Saudi Arabia": {"container": "Asia", "divs": ["provinces", "governorates"]},
    "Senegal": {"container": "Africa", "divs": ["regions", "departments"]},
    "Serbia": {"container": "Europe", "divs": ["districts", "municipalities", "autonomous provinces"]},
    "Seychelles": {"container": "Africa", "divs": ["districts"], "british_spelling": True},
    "Sierra Leone": {"container": "Africa", "divs": ["provinces", "districts"], "british_spelling": True},
    "Singapore": {"container": "Asia", "divs": ["districts"], "british_spelling": True},
    "Slovakia": {"container": "Europe", "divs": ["regions", "districts"], "british_spelling": True},
    "Slovenia": {"container": "Europe", "divs": ["statistical regions", "municipalities"], "british_spelling": True},
    "Solomon Islands": {"the": True, "container": "Melanesia", "divs": ["provinces"], "british_spelling": True},
    "Somalia": {"container": "Africa", "divs": ["regions", "districts"]},
    "South Africa": {
        "container": "Africa",
        "divs": [
            "provinces",
            "districts",
            {"type": "district municipalities"},
            {"type": "metropolitan municipalities"},
            "municipalities",
        ],
        "british_spelling": True,
    },
    "South Korea": {"container": "Asia", "addl_parents": ["Korea"], "divs": ["provinces", "counties", "districts"]},
    "South Sudan": {"container": "Africa", "divs": ["regions", "states", "counties"], "british_spelling": True},
    "Spain": {
        "container": "Europe",
        "divs": ["autonomous communities", "provinces", "municipalities", "comarcas", "autonomous cities"],
        "british_spelling": True,
    },
    "Sri Lanka": {"container": "Asia", "divs": ["provinces", "districts"], "british_spelling": True},
    "Sudan": {"container": "Africa", "divs": ["states", "districts"], "british_spelling": True},
    "Suriname": {"container": "South America", "divs": ["districts"]},
    "Sweden": {"container": "Europe", "divs": ["provinces", "counties", "municipalities"], "british_spelling": True},
    "Switzerland": {
        "container": "Europe",
        "divs": ["cantons", "municipalities", "districts"],
        "british_spelling": True,
    },
    "Syria": {"container": "Asia", "divs": ["governorates", "districts"]},
    "Taiwan": {"container": "Asia", "divs": ["counties", "districts", "townships", "special municipalities"]},
    "Republic of China": {"alias_of": "Taiwan", "the": True},
    "Tajikistan": {"container": "Asia", "divs": ["regions", "districts"]},
    "Tanzania": {"container": "Africa", "divs": ["regions", "districts"], "british_spelling": True},
    "Thailand": {"container": "Asia", "divs": ["provinces", "districts", "subdistricts"]},
    "Togo": {"container": "Africa", "divs": ["provinces", "prefectures"]},
    "Tonga": {"container": "Polynesia", "divs": ["divisions"], "british_spelling": True},
    "Trinidad and Tobago": {"container": "Caribbean", "divs": ["regions", "municipalities"], "british_spelling": True},
    "Tunisia": {"container": "Africa", "divs": ["governorates", "delegations"]},
    "Turkey": {"container": ["Europe", "Asia"], "divs": ["provinces", "districts"]},
    "Türkiye": {"alias_of": "Turkey", "display": True},
    "Turkmenistan": {"container": "Asia", "divs": ["regions", {"type": "provinces"}, "districts"]},
    "Tuvalu": {"container": "Polynesia", "divs": ["atolls"], "british_spelling": True},
    "Uganda": {"container": "Africa", "divs": ["districts", "counties"], "british_spelling": True},
    "Ukraine": {
        "container": "Europe",
        "divs": [{"type": "oblasts"}, {"type": "autonomous republics"}, "raions", "hromadas"],
        "british_spelling": True,
    },
    "United Arab Emirates": {"the": True, "container": "Asia", "divs": ["emirates"]},
    "UAE": {"alias_of": "United Arab Emirates", "display": True, "the": True},
    "U.A.E.": {"alias_of": "United Arab Emirates", "display": True, "the": True},
    "United Kingdom": {
        "the": True,
        "container": "Europe",
        "addl_parents": ["British Isles"],
        "divs": [
            "constituent countries",
            "counties",
            "districts",
            "boroughs",
            "territories",
            "dependent territories",
            "traditional counties",
        ],
        "keydesc": "the [[United Kingdom]] of Great Britain and Northern Ireland",
        "british_spelling": True,
    },
    "UK": {"alias_of": "United Kingdom", "display": True, "the": True},
    "U.K.": {"alias_of": "United Kingdom", "display": True, "the": True},
    "United States": {
        "the": True,
        "container": "North America",
        "divs": [
            "counties",
            "county seats",
            "states",
            "territories",
            "dependent territories",
            {"type": "ABBREVIATION_OF states"},
            {"type": "DEROGATORY_NAME_FOR states"},
            {"type": "NICKNAME_FOR states"},
            {"type": "OFFICIAL_NICKNAME_FOR states"},
            {"type": "boroughs", "prep": "in"},
            "municipalities",
            {"type": "census-designated places", "prep": "in"},
            {"type": "unincorporated communities", "prep": "in"},
            "Indian reservations",
        ],
    },
    "US": {"alias_of": "United States", "display": True, "the": True},
    "U.S.": {"alias_of": "United States", "display": True, "the": True},
    "USA": {"alias_of": "United States", "display": True, "the": True},
    "U.S.A.": {"alias_of": "United States", "display": True, "the": True},
    "United States of America": {"alias_of": "United States", "display": True, "the": True},
    "Uruguay": {"container": "South America", "divs": ["departments", "municipalities"]},
    "Uzbekistan": {"container": "Asia", "divs": ["regions", "districts"]},
    "Vanuatu": {"container": "Melanesia", "divs": ["provinces"], "british_spelling": True},
    "Vatican City": {
        "placetype": ["city-state", "country"],
        "container": "Europe",
        "bare_category_parent_type": {"type": "countries", "prep": "in"},
        "addl_parents": ["Rome"],
        "is_city": True,
        "british_spelling": True,
    },
    "Vatican": {"alias_of": "Vatican City", "the": True},
    "Venezuela": {"container": "South America", "divs": ["states", "municipalities"]},
    "Vietnam": {"container": "Asia", "divs": ["provinces", "districts", "municipalities"]},
    "Western Sahara": {
        "placetype": ["territory", "country"],
        "container": "Africa",
        "bare_category_parent_type": {"type": "countries", "prep": "in"},
    },
    "Sahrawi Arab Democratic Republic": {"alias_of": "Western Sahara", "the": True},
    "Yemen": {"container": "Asia", "divs": ["governorates", "districts"]},
    "Zambia": {"container": "Africa", "divs": ["provinces", "districts"], "british_spelling": True},
    "Zimbabwe": {"container": "Africa", "divs": ["provinces", "districts"], "british_spelling": True},
}

COUNTRIES_GROUP = {
    "canonicalize_key_container": canonicalize_continent_container,
    "default_overriding_bare_label_parents": ["+++", "countries"],
    "default_placetype": "country",
    "default_no_container_cat": True,
    "default_no_container_parent": True,
    "default_no_auto_augment_container": True,
    "data": COUNTRIES,
}

COUNTRY_LIKE_ENTITIES = {
    "Akrotiri and Dhekelia": {
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Cyprus", "Europe", "Asia"],
        "british_spelling": True,
    },
    "American Samoa": {
        "placetype": ["unincorporated territory", "overseas territory", "territory"],
        "container": "United States",
        "addl_parents": ["Polynesia"],
    },
    "Anguilla": {
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Abkhazia": {
        "placetype": ["unrecognized country", "country"],
        "addl_parents": ["Georgia", "Europe", "Asia"],
        "divs": ["districts"],
        "keydesc": "the de-facto independent state of [[Abkhazia]], internationally recognized as part of the country of [[Georgia]]",
        "british_spelling": True,
    },
    "Ashmore and Cartier Islands": {
        "the": True,
        "placetype": ["external territory", "territory"],
        "container": "Australia",
        "addl_parents": ["Asia"],
    },
    "Aruba": {
        "placetype": ["constituent country", "country"],
        "container": "Netherlands",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Bermuda": {
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["North America"],
        "british_spelling": True,
    },
    "Bonaire": {
        "placetype": ["special municipality", "municipality", "overseas territory", "territory"],
        "container": "Netherlands",
        "addl_parents": ["Caribbean"],
        "is_city": True,
        "british_spelling": True,
    },
    "British Indian Ocean Territory": {
        "the": True,
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Asia"],
        "british_spelling": True,
    },
    "British Virgin Islands": {
        "the": True,
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Bouvet Island": {
        "placetype": ["dependent territory", "territory"],
        "container": "Norway",
        "addl_parents": ["Africa"],
        "british_spelling": True,
    },
    "Cayman Islands": {
        "the": True,
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Christmas Island": {
        "placetype": ["external territory", "territory"],
        "container": "Australia",
        "addl_parents": ["Asia"],
        "british_spelling": True,
    },
    "Clipperton Island": {
        "placetype": ["overseas territory", "territory"],
        "container": "France",
        "addl_parents": ["North America"],
    },
    "Cocos Islands": {
        "the": True,
        "placetype": ["external territory", "territory"],
        "container": "Australia",
        "addl_parents": ["Asia"],
        "wp": "Cocos (Keeling) Islands",
        "british_spelling": True,
    },
    "Cocos (Keeling) Islands": {"alias_of": "Cocos Islands", "display": True, "the": True},
    "Keeling Islands": {"alias_of": "Cocos Islands", "display": True, "the": True},
    "Cook Islands": {
        "the": True,
        "placetype": ["country"],
        "container": "New Zealand",
        "addl_parents": ["Polynesia"],
        "british_spelling": True,
    },
    "Curaçao": {
        "placetype": ["constituent country", "country"],
        "container": "Netherlands",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Easter Island": {
        "placetype": ["special territory", "territory"],
        "container": "Chile",
        "addl_parents": ["Polynesia"],
    },
    "Falkland Islands": {
        "the": True,
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["South America"],
        "british_spelling": True,
    },
    "Faroe Islands": {
        "the": True,
        "placetype": ["autonomous territory", "territory"],
        "container": "Denmark",
        "addl_parents": ["Europe"],
        "british_spelling": True,
    },
    "French Guiana": {
        "placetype": ["overseas department", "department", "administrative region", "region"],
        "container": "France",
        "divs": ["communes"],
        "addl_parents": ["South America"],
        "british_spelling": True,
    },
    "French Polynesia": {
        "placetype": ["overseas collectivity", "collectivity"],
        "container": "France",
        "addl_parents": ["Polynesia"],
        "british_spelling": True,
    },
    "French Southern and Antarctic Lands": {
        "the": True,
        "placetype": ["overseas territory", "territory"],
        "container": "France",
        "addl_parents": ["Africa"],
    },
    "Gibraltar": {
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Europe"],
        "is_city": True,
        "british_spelling": True,
    },
    "Greenland": {
        "placetype": ["autonomous territory", "territory"],
        "container": "Denmark",
        "addl_parents": ["North America"],
        "divs": ["municipalities"],
        "british_spelling": True,
    },
    "Guadeloupe": {
        "placetype": ["overseas department", "department", "administrative region", "region"],
        "container": "France",
        "addl_parents": ["Caribbean"],
        "divs": ["communes"],
        "british_spelling": True,
    },
    "Guam": {
        "placetype": ["unincorporated territory", "overseas territory", "territory"],
        "container": "United States",
        "addl_parents": ["Micronesia"],
    },
    "Guernsey": {
        "placetype": ["crown dependency", "dependency", "dependent territory", "bailiwick", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["British Isles", "Europe"],
        "british_spelling": True,
        "wp": "Bailiwick of %l",
    },
    "Bailiwick of Guernsey": {"alias_of": "Guernsey", "the": True},
    "Heard Island and McDonald Islands": {
        "the": True,
        "placetype": ["external territory", "territory"],
        "container": "Australia",
        "addl_parents": ["Africa"],
    },
    "Hong Kong": {
        "placetype": ["special administrative region", "city"],
        "container": "China",
        "is_city": True,
        "british_spelling": True,
    },
    "Isle of Man": {
        "the": True,
        "placetype": ["crown dependency", "dependency", "dependent territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["British Isles", "Europe"],
        "british_spelling": True,
    },
    "Jan Mayen": {
        "placetype": ["unincorporated area", "dependent territory", "territory", "island"],
        "container": "Norway",
        "addl_parents": ["Europe"],
        "british_spelling": True,
    },
    "Jersey": {
        "placetype": ["crown dependency", "dependency", "dependent territory", "bailiwick", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["British Isles", "Europe"],
        "british_spelling": True,
    },
    "Bailiwick of Jersey": {"alias_of": "Jersey", "the": True},
    "Macau": {
        "placetype": ["special administrative region", "city"],
        "container": "China",
        "is_city": True,
        "british_spelling": True,
    },
    "Martinique": {
        "placetype": ["overseas department", "department", "administrative region", "region"],
        "container": "France",
        "divs": ["communes"],
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Mayotte": {
        "placetype": ["overseas department", "department", "administrative region", "region"],
        "container": "France",
        "divs": ["communes"],
        "addl_parents": ["Africa"],
        "british_spelling": True,
    },
    "Montserrat": {
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "New Caledonia": {
        "placetype": ["special collectivity", "collectivity"],
        "container": "France",
        "addl_parents": ["Melanesia"],
        "british_spelling": True,
    },
    "New Zealand Subantarctic Islands": {
        "the": True,
        "placetype": ["dependent territory", "territory"],
        "container": "New Zealand",
        "addl_parents": ["Antarctica"],
        "british_spelling": True,
    },
    "Niue": {
        "placetype": ["country"],
        "container": "New Zealand",
        "addl_parents": ["Polynesia"],
        "british_spelling": True,
    },
    "Norfolk Island": {
        "placetype": ["external territory", "territory"],
        "container": "Australia",
        "addl_parents": ["Polynesia"],
        "british_spelling": True,
    },
    "Northern Cyprus": {
        "placetype": ["unrecognized country", "country"],
        "addl_parents": ["Cyprus", "Turkey", "Europe", "Asia"],
        "divs": ["districts"],
        "keydesc": "the de-facto independent state of [[Northern Cyprus]], internationally recognized as part of the country of [[Cyprus]]",
        "british_spelling": True,
    },
    "Northern Mariana Islands": {
        "the": True,
        "placetype": ["commonwealth", "unincorporated territory", "overseas territory", "territory"],
        "container": "United States",
        "addl_parents": ["Micronesia"],
    },
    "Pitcairn Islands": {
        "the": True,
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Polynesia"],
        "british_spelling": True,
    },
    "Puerto Rico": {
        "placetype": ["commonwealth", "overseas territory", "territory"],
        "container": "United States",
        "addl_parents": ["Caribbean"],
        "divs": ["municipalities"],
    },
    "Réunion": {
        "placetype": ["overseas department", "department", "administrative region", "region"],
        "container": "France",
        "divs": ["communes"],
        "addl_parents": ["Africa"],
        "british_spelling": True,
    },
    "Saba": {
        "placetype": ["special municipality", "municipality", "overseas territory", "territory"],
        "container": "Netherlands",
        "addl_parents": ["Caribbean"],
        "is_city": True,
        "british_spelling": True,
    },
    "Saint Barthélemy": {
        "placetype": ["overseas collectivity", "collectivity"],
        "container": "France",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Saint Helena, Ascension and Tristan da Cunha": {
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "divs": [{"type": "constituent parts"}],
        "addl_parents": ["Atlantic Ocean", "Africa"],
        "british_spelling": True,
    },
    "Ascension Island": {
        "placetype": ["constituent part", "territory", "island"],
        "container": {"key": "Saint Helena, Ascension and Tristan da Cunha", "placetype": "overseas territory"},
        "addl_parents": ["Atlantic Ocean"],
    },
    "Saint Helena": {
        "placetype": ["constituent part", "territory", "island"],
        "container": {"key": "Saint Helena, Ascension and Tristan da Cunha", "placetype": "overseas territory"},
        "addl_parents": ["Atlantic Ocean"],
    },
    "Tristan da Cunha": {
        "placetype": ["constituent part", "territory", "archipelago"],
        "container": {"key": "Saint Helena, Ascension and Tristan da Cunha", "placetype": "overseas territory"},
        "addl_parents": ["Atlantic Ocean"],
    },
    "Saint Martin": {
        "placetype": ["overseas collectivity", "collectivity"],
        "container": "France",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Saint Pierre and Miquelon": {
        "placetype": ["overseas collectivity", "collectivity"],
        "container": "France",
        "divs": ["communes"],
        "addl_parents": ["North America"],
        "british_spelling": True,
    },
    "Sint Eustatius": {
        "placetype": ["special municipality", "municipality", "overseas territory", "territory"],
        "container": "Netherlands",
        "addl_parents": ["Caribbean"],
        "is_city": True,
        "british_spelling": True,
    },
    "Sint Maarten": {
        "placetype": ["constituent country", "country"],
        "container": "Netherlands",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "Somaliland": {
        "placetype": ["unrecognized country", "country"],
        "addl_parents": ["Somalia", "Africa"],
        "keydesc": "the de-facto independent state of [[Somaliland]], internationally recognized as part of the country of [[Somalia]]",
        "british_spelling": True,
    },
    "South Georgia": {
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Atlantic Ocean"],
        "british_spelling": True,
    },
    "South Ossetia": {
        "placetype": ["unrecognized country", "country"],
        "addl_parents": ["Georgia", "Europe", "Asia"],
        "keydesc": "the de-facto independent state of [[South Ossetia]], internationally recognized as part of the country of [[Georgia]]",
        "british_spelling": True,
    },
    "South Sandwich Islands": {
        "the": True,
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Atlantic Ocean"],
        "wp": True,
        "british_spelling": True,
    },
    "Svalbard": {
        "placetype": ["unincorporated area", "dependent territory", "territory", "archipelago"],
        "container": "Norway",
        "addl_parents": ["Europe"],
        "british_spelling": True,
    },
    "Tokelau": {
        "placetype": ["dependent territory", "territory"],
        "container": "New Zealand",
        "addl_parents": ["Polynesia"],
        "british_spelling": True,
    },
    "Transnistria": {
        "placetype": ["unrecognized country", "country"],
        "addl_parents": ["Moldova", "Europe"],
        "keydesc": "the de-facto independent state of [[Transnistria]], internationally recognized as part of [[Moldova]]",
        "british_spelling": True,
    },
    "Turks and Caicos Islands": {
        "the": True,
        "placetype": ["overseas territory", "territory"],
        "container": "United Kingdom",
        "addl_parents": ["Caribbean"],
        "british_spelling": True,
    },
    "United States Minor Outlying Islands": {
        "the": True,
        "placetype": ["unincorporated territory", "overseas territory", "territory"],
        "container": "United States",
        "addl_parents": ["Islands", "Micronesia", "Polynesia", "Caribbean"],
    },
    "Wake Island": {
        "placetype": ["unincorporated territory", "overseas territory", "territory"],
        "container": "United States",
        "addl_parents": ["Micronesia"],
    },
    "United States Virgin Islands": {
        "the": True,
        "placetype": ["unincorporated territory", "overseas territory", "territory"],
        "container": "United States",
        "addl_parents": ["Caribbean"],
    },
    "U.S. Virgin Islands": {"alias_of": "United States Virgin Islands", "display": True, "the": True},
    "US Virgin Islands": {"alias_of": "United States Virgin Islands", "display": True, "the": True},
    "Wallis and Futuna": {
        "placetype": ["overseas collectivity", "collectivity"],
        "container": "France",
        "addl_parents": ["Polynesia"],
        "british_spelling": True,
    },
}

COUNTRY_LIKE_ENTITIES_GROUP = {
    "key_to_placename": False,
    "placename_to_key": False,
    "canonicalize_key_container": make_canonicalize_key_container(None, "country"),
    "default_overriding_bare_label_parents": ["country-like entities"],
    "default_no_container_cat": True,
    "default_no_container_parent": True,
    "default_no_auto_augment_container": True,
    "data": COUNTRY_LIKE_ENTITIES,
}

FORMER_COUNTRIES = {
    "Artsakh": {
        "placetype": ["unrecognized country", "country"],
        "addl_parents": ["Azerbaijan", "Europe", "Asia"],
        "keydesc": "the former de-facto independent state of [[Artsakh]], internationally recognized as part of [[Azerbaijan]]",
        "british_spelling": True,
    },
    "Nagorno-Karabakh": {
        "alias_of": "Artsakh",
    },
    "Czechoslovakia": {
        "container": "Europe",
        "british_spelling": True,
    },
    "East Germany": {
        "container": "Europe",
        "addl_parents": ["Germany"],
        "british_spelling": True,
    },
    "North Vietnam": {
        "container": "Asia",
        "addl_parents": ["Vietnam"],
    },
    "Persia": {
        "placetype": ["empire", "country"],
        "container": "Asia",
        "divs": ["provinces"],
    },
    "Byzantine Empire": {
        "the": True,
        "placetype": ["empire", "country"],
        "container": ["Europe", "Africa", "Asia"],
        "addl_parents": ["Ancient Europe", "Ancient Near East"],
        "divs": ["provinces", "themes"],
    },
    "Roman Empire": {
        "the": True,
        "placetype": ["empire", "country"],
        "container": ["Europe", "Africa", "Asia"],
        "addl_parents": ["Rome"],
        "divs": ["provinces", {"type": "FORMER provinces"}],
    },
    "South Vietnam": {
        "container": "Asia",
        "addl_parents": ["Vietnam"],
    },
    "Soviet Union": {
        "the": True,
        "container": ["Europe", "Asia"],
        "divs": ["republics", "autonomous republics"],
        "british_spelling": True,
    },
    "West Germany": {
        "container": "Europe",
        "addl_parents": ["Germany"],
        "british_spelling": True,
    },
    "Yugoslavia": {
        "container": "Europe",
        "divs": ["districts"],
        "keydesc": "the former [[Kingdom of Yugoslavia]] (1918–1943) or the former [[Socialist Federal Republic of Yugoslavia]] (1943–1992)",
        "british_spelling": True,
    },
}

FORMER_COUNTRIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": canonicalize_continent_container,
    "default_overriding_bare_label_parents": ["former countries and country-like entities"],
    "default_is_former_place": True,
    "default_placetype": "country",
    "default_no_container_parent": True,
    "default_no_auto_augment_container": True,
    "data": FORMER_COUNTRIES,
}

AUSTRALIA_STATES_AND_TERRITORIES = {
    "Australian Capital Territory, Australia": {"the": True, "placetype": "territory"},
    "Jervis Bay Territory, Australia": {"the": True, "placetype": "territory"},
    "New South Wales, Australia": {},
    "Northern Territory, Australia": {"the": True, "placetype": "territory"},
    "Queensland, Australia": {},
    "South Australia, Australia": {},
    "Tasmania, Australia": {},
    "Victoria, Australia": {},
    "Western Australia, Australia": {},
}


AUSTRALIA_STATES_AND_TERRITORIES = {
    "Australian Capital Territory, Australia": {"the": True, "placetype": "territory"},
    "Jervis Bay Territory, Australia": {"the": True, "placetype": "territory"},
    "New South Wales, Australia": {},
    "Northern Territory, Australia": {"the": True, "placetype": "territory"},
    "Queensland, Australia": {},
    "South Australia, Australia": {},
    "Tasmania, Australia": {},
    "Victoria, Australia": {},
    "Western Australia, Australia": {},
}

AUSTRALIA_GROUP = {
    "default_container": "Australia",
    "default_placetype": "state",
    "default_divs": "local government areas",
    "data": AUSTRALIA_STATES_AND_TERRITORIES,
}

AUSTRIA_STATES = {
    "Vienna, Austria": {},
    "Lower Austria, Austria": {},
    "Upper Austria, Austria": {},
    "Styria, Austria": {},
    "Tyrol, Austria": {"wp": "Tyrol (state)"},
    "Carinthia, Austria": {},
    "Salzburg, Austria": {"wp": "Salzburg (state)"},
    "Vorarlberg, Austria": {},
    "Burgenland, Austria": {},
}

AUSTRIA_GROUP = {
    "default_container": "Austria",
    "default_placetype": "state",
    "default_divs": "municipalities",
    "data": AUSTRIA_STATES,
}

BANGLADESH_DIVISIONS: dict[str, Any] = {
    "Barisal Division, Bangladesh": {},
    "Chittagong Division, Bangladesh": {},
    "Dhaka Division, Bangladesh": {},
    "Khulna Division, Bangladesh": {},
    "Mymensingh Division, Bangladesh": {},
    "Rajshahi Division, Bangladesh": {},
    "Rangpur Division, Bangladesh": {},
    "Sylhet Division, Bangladesh": {},
}

BANGLADESH_GROUP = {
    "key_to_placename": make_key_to_placename(", Bangladesh$", " Division$"),
    "placename_to_key": make_placename_to_key(", Bangladesh", " Division"),
    "default_container": "Bangladesh",
    "default_placetype": "division",
    "default_divs": "districts",
    "data": BANGLADESH_DIVISIONS,
}

BRAZIL_STATES = {
    "Acre, Brazil": {"wp": "%l (state)"},
    "Alagoas, Brazil": {},
    "Amapá, Brazil": {},
    "Amazonas, Brazil": {"wp": "%l (Brazilian state)"},
    "Bahia, Brazil": {},
    "Ceará, Brazil": {},
    "Distrito Federal, Brazil": {"wp": "Federal District (Brazil)"},
    "Espírito Santo, Brazil": {},
    "Goiás, Brazil": {},
    "Maranhão, Brazil": {},
    "Mato Grosso, Brazil": {},
    "Mato Grosso do Sul, Brazil": {},
    "Minas Gerais, Brazil": {},
    "Pará, Brazil": {},
    "Paraíba, Brazil": {},
    "Paraná, Brazil": {"wp": "%l (state)"},
    "Pernambuco, Brazil": {},
    "Piauí, Brazil": {},
    "Rio de Janeiro, Brazil": {"wp": "%l (state)"},
    "Rio Grande do Norte, Brazil": {},
    "Rio Grande do Sul, Brazil": {},
    "Rondônia, Brazil": {},
    "Roraima, Brazil": {},
    "Santa Catarina, Brazil": {"wp": "%l (state)"},
    "São Paulo, Brazil": {"wp": "%l (state)"},
    "Sergipe, Brazil": {},
    "Tocantins, Brazil": {},
}
BRAZIL_GROUP = {
    "default_container": "Brazil",
    "default_placetype": "state",
    "default_divs": "municipalities",
    "data": BRAZIL_STATES,
}

CANADA_PROVINCES_AND_TERRITORIES = {
    "Alberta, Canada": {
        "divs": [
            {"type": "municipal districts", "container_parent_type": "rural municipalities"},
        ]
    },
    "British Columbia, Canada": {
        "divs": [
            {"type": "regional districts", "container_parent_type": False},
            "regional municipalities",
        ]
    },
    "Manitoba, Canada": {"divs": ["rural municipalities"]},
    "New Brunswick, Canada": {"divs": ["counties", "parishes", {"type": "civil parishes"}]},
    "Newfoundland and Labrador, Canada": {},
    "Northwest Territories, Canada": {"the": True, "placetype": "territory"},
    "Nova Scotia, Canada": {"divs": ["counties", "regional municipalities"]},
    "Nunavut, Canada": {"placetype": "territory"},
    "Ontario, Canada": {"divs": ["counties", "regional municipalities", {"type": "townships", "prep": "in"}]},
    "Prince Edward Island, Canada": {"divs": ["counties", "parishes", "rural municipalities"]},
    "Saskatchewan, Canada": {"divs": ["rural municipalities"]},
    "Quebec, Canada": {
        "divs": [
            "counties",
            {"type": "regional county municipalities", "container_parent_type": "regional municipalities"},
            {"type": "regions", "container_parent_type": False},
            {"type": "townships", "prep": "in"},
            {"type": "parish municipalities"},
            {"type": "township municipalities"},
            {"type": "village municipalities"},
        ]
    },
    "Yukon, Canada": {"placetype": "territory"},
    "Yukon Territory, Canada": {"alias_of": "Yukon, Canada", "the": True},
}

CANADA_GROUP = {
    "default_container": "Canada",
    "default_placetype": "province",
    "data": CANADA_PROVINCES_AND_TERRITORIES,
}

CHINA_PROVINCES_AND_AUTONOMOUS_REGIONS = {
    "Anhui, China": {},
    "Fujian, China": {},
    "Fuchien, China": {"alias_of": "Fujian, China", "display": True},
    "Gansu, China": {},
    "Guangdong, China": {},
    "Guangxi, China": {"placetype": "autonomous region"},
    "Guizhou, China": {},
    "Hainan, China": {},
    "Hebei, China": {},
    "Heilongjiang, China": {},
    "Henan, China": {},
    "Hubei, China": {},
    "Hunan, China": {},
    "Inner Mongolia, China": {"placetype": "autonomous region"},
    "Jiangsu, China": {},
    "Jiangxi, China": {},
    "Jilin, China": {},
    "Liaoning, China": {},
    "Ningxia, China": {"placetype": "autonomous region"},
    "Qinghai, China": {},
    "Shaanxi, China": {},
    "Shandong, China": {},
    "Shanxi, China": {},
    "Sichuan, China": {},
    "Tibet, China": {"placetype": "autonomous region", "wp": "Tibet Autonomous Region"},
    "Xinjiang, China": {"placetype": "autonomous region"},
    "Yunnan, China": {},
    "Zhejiang, China": {},
}

CHINA_GROUP = {
    "default_container": "China",
    "default_placetype": "province",
    "default_divs": [
        "prefectures",
        "prefecture-level cities",
        "districts",
        "subdistricts",
        "townships",
        {"type": "counties", "cat_as": "counties and county-level cities"},
        {"type": "county-level cities", "cat_as": "counties and county-level cities"},
    ],
    "data": CHINA_PROVINCES_AND_AUTONOMOUS_REGIONS,
}

CHINA_PREFECTURE_LEVEL_CITIES = {
    "Guangzhou": {"container": "Guangdong"},
    "Dongguan": {"container": "Guangdong"},
    "Foshan": {"container": "Guangdong"},
    "Huizhou": {"container": "Guangdong"},
    "Jiangmen": {"container": "Guangdong"},
    "Shenzhen": {"container": "Guangdong"},
    "Zhongshan": {"container": "Guangdong"},
    "Shanghai": {"placetype": ["direct-administered municipality", "municipality", "city"]},
    "Changshu": {"container": "Jiangsu"},
    "Changzhou": {"container": "Jiangsu"},
    "Suzhou": {"container": "Jiangsu"},
    "Wuxi": {"container": "Jiangsu"},
    "Beijing": {"placetype": ["direct-administered municipality", "municipality", "city"]},
    "Chengdu": {"container": "Sichuan"},
    "Xiamen": {"container": "Fujian"},
    "Jinjiang": {"container": "Fujian"},
    "Quanzhou": {"container": "Fujian"},
    "Putian": {"container": "Fujian"},
    "Hangzhou": {"container": "Zhejiang"},
    "Shaoxing": {"container": "Zhejiang"},
    "Xi'an": {"container": "Shaanxi"},
    "Xianyang": {"container": "Shaanxi"},
    "Chongqing": {"placetype": ["direct-administered municipality", "municipality", "city"]},
    "Wuhan": {"container": "Hubei"},
    "Tianjin": {"placetype": ["direct-administered municipality", "municipality", "city"]},
    "Changsha": {"container": "Hunan"},
    "Zhuzhou": {"container": "Hunan"},
    "Zhengzhou": {"container": "Henan"},
    "Nanjing": {"container": "Jiangsu"},
    "Shenyang": {"container": "Liaoning"},
    "Fushun": {"container": "Liaoning"},
    "Hefei": {"container": "Anhui"},
    "Shantou": {"container": "Guangdong"},
    "Chaozhou": {"container": "Guangdong"},
    "Jieyang": {"container": "Guangdong"},
    "Qingdao": {"container": "Shandong"},
    "Ningbo": {"container": "Zhejiang"},
    "Cixi": {"container": "Zhejiang"},
    "Yuyao": {"container": "Zhejiang"},
    "Wenzhou": {"container": "Zhejiang"},
    "Rui'an": {
        "placetype": "county-level city",
        "container": {"key": "Wenzhou", "placetype": "prefecture-level city"},
        "divs": ["subdistricts", "townships"],
    },
    "Kunming": {"container": "Yunnan"},
    "Jinan": {"container": "Shandong", "wp": "%l, %c"},
    "Shijiazhuang": {"container": "Hebei"},
    "Taiyuan": {"container": "Shanxi"},
    "Harbin": {"container": "Heilongjiang"},
    "Nanning": {"container": {"key": "Guangxi, China", "placetype": "autonomous region"}},
    "Dalian": {"container": "Liaoning"},
    "Guiyang": {"container": "Guizhou"},
    "Changchun": {"container": "Jilin"},
    "Nanchang": {"container": "Jiangxi"},
    "Ürümqi": {"container": {"key": "Xinjiang, China", "placetype": "autonomous region"}},
    "Urumqi": {"alias_of": "Ürümqi", "display": True},
    "Fuzhou": {"container": "Fujian"},
    "Linyi": {"container": "Shandong"},
    "Zibo": {"container": "Shandong"},
    "Luoyang": {"container": "Henan"},
    "Lanzhou": {"container": "Gansu"},
    "Nantong": {"container": "Jiangsu"},
    "Weifang": {"container": "Shandong"},
    "Jiangyin": {"container": "Jiangsu"},
    "Zhangjiagang": {"container": "Jiangsu"},
    "Xuzhou": {"container": "Jiangsu"},
    "Handan": {"container": "Hebei"},
    "Hohhot": {"container": {"key": "Inner Mongolia, China", "placetype": "autonomous region"}},
    "Haikou": {"container": "Hainan"},
    "Tangshan": {"container": "Hebei"},
    "Xinxiang": {"container": "Henan"},
    "Yiwu": {"container": "Zhejiang"},
    "Zhuhai": {"container": "Guangdong"},
    "Taizhou, Zhejiang": {"container": "Zhejiang"},
    "Taizhou": {"alias_of": "Taizhou, Zhejiang"},
    "Yantai": {"container": "Shandong"},
    "Yinchuan": {"container": {"key": "Ningxia, China", "placetype": "autonomous region"}},
    "Liuzhou": {"container": {"key": "Guangxi, China", "placetype": "autonomous region"}},
    "Anshan": {"container": "Liaoning"},
    "Yangzhou": {"container": "Jiangsu"},
    "Jiaxing": {"container": "Zhejiang"},
    "Xining": {"container": "Qinghai"},
    "Baoding": {"container": "Hebei"},
    "Baotou": {"container": {"key": "Inner Mongolia, China", "placetype": "autonomous region"}},
    "Ganzhou": {"container": "Jiangxi"},
    "Pingdingshan": {"container": "Henan"},
    "Zunyi": {"container": "Guizhou"},
    "Bengbu": {"container": "Anhui"},
    "Datong": {"container": "Shanxi"},
    "Anyang": {"container": "Henan"},
    "Huai'an": {"container": "Jiangsu"},
    "Zaozhuang": {"container": "Shandong"},
    "Zhanjiang": {"container": "Guangdong"},
    "Huainan": {"container": "Anhui"},
    "Jining": {"container": "Shandong"},
    "Daqing": {"container": "Heilongjiang"},
    "Wuhu": {"container": "Anhui"},
    "Guilin": {"container": {"key": "Guangxi, China", "placetype": "autonomous region"}},
    "Mianyang": {"container": "Sichuan"},
    "Xiangyang": {"container": "Hubei"},
    "Huzhou": {"container": "Zhejiang"},
    "Puyang": {"container": "Henan"},
    "Shangqiu": {"container": "Henan"},
    "Qinhuangdao": {"container": "Hebei"},
    "Xingtai": {"container": "Hebei"},
    "Nanyang": {"container": "Henan", "wp": "%l, %c"},
    "Jiaozuo": {"container": "Henan"},
    "Jilin City": {"container": "Jilin"},
    "Jilin": {"alias_of": "Jilin City"},
    "Jinhua": {"container": "Zhejiang"},
    "Shangrao": {"container": "Jiangxi"},
    "Heze": {"container": "Shandong"},
    "Yulin": {"container": {"key": "Guangxi, China", "placetype": "autonomous region"}, "wp": "%l, %c"},
    "Tai'an": {"container": "Shandong"},
    "Weihai": {"container": "Shandong"},
    "Yancheng": {"container": "Jiangsu"},
    "Zhangjiakou": {"container": "Hebei"},
    "Maoming": {"container": "Guangdong"},
    "Nanchong": {"container": "Sichuan"},
    "Fuyang": {"container": "Anhui", "wp": "%l, %c"},
    "Xuchang": {"container": "Henan"},
    "Yichang": {"container": "Hubei"},
    "Dazhou": {"container": "Sichuan"},
    "Kaifeng": {"container": "Henan"},
    "Luzhou": {"container": "Sichuan"},
    "Qingyuan": {"container": "Guangdong"},
    "Huaibei": {"container": "Anhui"},
    "Yibin": {"container": "Sichuan"},
    "Lu'an": {"container": "Anhui"},
    "Dezhou": {"container": "Shandong"},
    "Rizhao": {"container": "Shandong"},
    "Changzhi": {"container": "Shanxi"},
    "Hengyang": {"container": "Hunan"},
    "Jinzhou": {"container": "Liaoning"},
    "Liaocheng": {"container": "Shandong"},
    "Changde": {"container": "Hunan"},
    "Suqian": {"container": "Jiangsu"},
    "Xinyang": {"container": "Henan"},
    "Baoji": {"container": "Shaanxi"},
    "Yueyang": {"container": "Hunan"},
    "Zhenjiang": {"container": "Jiangsu"},
    "Wanzhou": {
        "placetype": "district",
        "container": {"key": "Chongqing", "placetype": "direct-administered municipality"},
        "divs": ["subdistricts", "townships"],
        "wp": "%l, %c",
    },
    "Ulanhad": {"container": {"key": "Inner Mongolia, China", "placetype": "autonomous region"}},
    "Chifeng": {"alias_of": "Ulanhad"},
    "Ulankhad": {"alias_of": "Ulanhad", "display": True},
    "Ezhou": {"container": "Hubei"},
    "Zhaoqing": {"container": "Guangdong"},
    "Lianyungang": {"container": "Jiangsu"},
    "Qujing": {"container": "Yunnan"},
    "Shuyang": {
        "placetype": "county",
        "container": {"key": "Suqian", "placetype": "prefecture-level city"},
        "divs": ["subdistricts", "townships"],
        "wp": "%l County",
    },
    "Yongkang": {
        "placetype": "county-level city",
        "container": {"key": "Jinhua", "placetype": "prefecture-level city"},
        "divs": ["subdistricts", "townships"],
        "wp": "%l, Zhejiang",
    },
    "Zhoukou": {"container": "Henan"},
    "Beihai": {"container": {"key": "Guangxi, China", "placetype": "autonomous region"}},
    "Jiujiang": {"container": "Jiangxi"},
    "Shaoyang": {"container": "Hunan"},
    "Chuzhou": {"container": "Anhui"},
    "Hengshui": {"container": "Hebei"},
    "Shiyan": {"container": "Hubei"},
    "Huludao": {"container": "Liaoning"},
    "Dongying": {"container": "Shandong"},
    "Guigang": {"container": {"key": "Guangxi, China", "placetype": "autonomous region"}},
    "Liuyang": {
        "placetype": "county-level city",
        "container": {"key": "Changsha", "placetype": "prefecture-level city"},
        "divs": ["subdistricts", "townships"],
    },
    "Cangzhou": {"container": "Hebei"},
    "Liupanshui": {"container": "Guizhou"},
    "Panjin": {"container": "Liaoning"},
    "Qiqihar": {"container": "Heilongjiang"},
    "Linfen": {"container": "Shanxi"},
    "Tengzhou": {
        "placetype": "county-level city",
        "container": {"key": "Zaozhuang", "placetype": "prefecture-level city"},
        "divs": ["subdistricts", "townships"],
    },
    "Kunshan": {"container": "Jiangsu"},
    "Zhumadian": {"container": "Henan"},
    "Bijie": {"container": "Guizhou"},
}


CHINA_PREFECTURE_LEVEL_CITIES_GROUP = {
    "key_to_placename": False,
    "placename_to_key": False,
    "default_container": "China",
    "canonicalize_key_container": make_canonicalize_key_container(", China", "province"),
    "default_placetype": ["prefecture-level city", "city"],
    "default_divs": [
        "districts",
        "subdistricts",
        "townships",
        {"type": "counties", "cat_as": "counties and county-level cities"},
        {"type": "county-level cities", "cat_as": "counties and county-level cities"},
    ],
    "data": CHINA_PREFECTURE_LEVEL_CITIES,
}
CHINA_PREFECTURE_LEVEL_CITIES_2 = {
    "Taizhou, Jiangsu": {"container": "Jiangsu"},
    "Taizhou": {"alias_of": "Taizhou, Jiangsu"},
    "Suzhou, Anhui": {"container": "Anhui"},
    "Suzhou": {"alias_of": "Suzhou, Anhui"},
}

CHINA_PREFECTURE_LEVEL_CITIES_GROUP_2 = {
    "placename_to_key": False,
    "default_container": "China",
    "canonicalize_key_container": make_canonicalize_key_container(", China", "province"),
    "default_placetype": ["prefecture-level city", "city"],
    "default_divs": [
        "districts",
        "subdistricts",
        "townships",
        {"type": "counties", "cat_as": "counties and county-level cities"},
        {"type": "county-level cities", "cat_as": "counties and county-level cities"},
    ],
    "data": CHINA_PREFECTURE_LEVEL_CITIES_2,
}

FINLAND_REGIONS = {
    "Lapland, Finland": {"wp": "%l (%c)"},
    "North Ostrobothnia, Finland": {},
    "Northern Ostrobothnia, Finland": {"alias_of": "North Ostrobothnia, Finland", "display": True},
    "Kainuu, Finland": {},
    "North Karelia, Finland": {},
    "Northern Savonia, Finland": {},
    "North Savo, Finland": {"alias_of": "Northern Savonia, Finland", "display": True},
    "Southern Savonia, Finland": {},
    "South Savo, Finland": {"alias_of": "Southern Savonia, Finland", "display": True},
    "South Karelia, Finland": {},
    "Central Finland, Finland": {},
    "South Ostrobothnia, Finland": {},
    "Southern Ostrobothnia, Finland": {"alias_of": "South Ostrobothnia, Finland", "display": True},
    "Ostrobothnia, Finland": {"wp": "%l (region)"},
    "Central Ostrobothnia, Finland": {},
    "Pirkanmaa, Finland": {},
    "Satakunta, Finland": {},
    "Päijänne Tavastia, Finland": {},
    "Päijät-Häme, Finland": {"alias_of": "Päijänne Tavastia, Finland", "display": True},
    "Tavastia Proper, Finland": {},
    "Kanta-Häme, Finland": {"alias_of": "Tavastia Proper, Finland", "display": True},
    "Kymenlaakso, Finland": {},
    "Uusimaa, Finland": {},
    "Southwest Finland, Finland": {},
    "Åland Islands, Finland": {"the": True, "wp": "Åland"},
    "Åland, Finland": {"alias_of": "Åland Islands, Finland"},
}

FINLAND_GROUP = {
    "default_container": "Finland",
    "default_placetype": "region",
    "default_divs": "municipalities",
    "data": FINLAND_REGIONS,
}

FRANCE_ADMINISTRATIVE_REGIONS = {
    "Auvergne-Rhône-Alpes, France": {},
    "Bourgogne-Franche-Comté, France": {},
    "Brittany, France": {"wp": "%l (administrative region)"},
    "Centre-Val de Loire, France": {},
    "Corsica, France": {},
    "Grand Est, France": {},
    "Hauts-de-France, France": {},
    "Île-de-France, France": {},
    "Normandy, France": {"wp": "%l (administrative region)"},
    "Nouvelle-Aquitaine, France": {},
    "Occitania, France": {"wp": "%l (administrative region)"},
    "Occitanie, France": {"alias_of": "Occitania, France", "display": True},
    "Pays de la Loire, France": {},
    "Provence-Alpes-Côte d'Azur, France": {},
}

FRANCE_GROUP = {
    "default_container": "France",
    "default_placetype": "region",
    "default_divs": [
        "communes",
        {"type": "municipalities", "cat_as": "communes"},
        "departments",
        {"type": "prefectures", "cat_as": ["prefectures", "departmental capitals"]},
        {"type": "French prefectures", "cat_as": ["prefectures", "departmental capitals"]},
    ],
    "data": FRANCE_ADMINISTRATIVE_REGIONS,
}

FRANCE_DEPARTMENTS = {
    "Ain, France": {"container": "Auvergne-Rhône-Alpes"},
    "Aisne, France": {"container": "Hauts-de-France"},
    "Allier, France": {"container": "Auvergne-Rhône-Alpes"},
    "Alpes-de-Haute-Provence, France": {"container": "Provence-Alpes-Côte d'Azur"},
    "Hautes-Alpes, France": {"container": "Provence-Alpes-Côte d'Azur"},
    "Alpes-Maritimes, France": {"container": "Provence-Alpes-Côte d'Azur"},
    "Ardèche, France": {"container": "Auvergne-Rhône-Alpes"},
    "Ardennes, France": {"container": "Grand Est", "wp": "%l (department)"},
    "Ariège, France": {"container": "Occitania", "wp": "%l (department)"},
    "Aube, France": {"container": "Grand Est"},
    "Aude, France": {"container": "Occitania"},
    "Aveyron, France": {"container": "Occitania"},
    "Bouches-du-Rhône, France": {"container": "Provence-Alpes-Côte d'Azur"},
    "Calvados, France": {"container": "Normandy", "wp": "%l (department)"},
    "Cantal, France": {"container": "Auvergne-Rhône-Alpes"},
    "Charente, France": {"container": "Nouvelle-Aquitaine"},
    "Charente-Maritime, France": {"container": "Nouvelle-Aquitaine"},
    "Cher, France": {"container": "Centre-Val de Loire", "wp": "%l (department)"},
    "Corrèze, France": {"container": "Nouvelle-Aquitaine"},
    "Corse-du-Sud, France": {"container": "Corsica"},
    "Haute-Corse, France": {"container": "Corsica"},
    "Côte-d'Or, France": {"container": "Bourgogne-Franche-Comté"},
    "Côte d'Or, France": {"alias_of": "Côte-d'Or, France", "display": True},
    "Côtes-d'Armor, France": {"container": "Brittany"},
    "Côtes d'Armor, France": {"alias_of": "Côtes-d'Armor, France", "display": True},
    "Creuse, France": {"container": "Nouvelle-Aquitaine"},
    "Dordogne, France": {"container": "Nouvelle-Aquitaine"},
    "Doubs, France": {"container": "Bourgogne-Franche-Comté"},
    "Drôme, France": {"container": "Auvergne-Rhône-Alpes"},
    "Eure, France": {"container": "Normandy"},
    "Eure-et-Loir, France": {"container": "Centre-Val de Loire"},
    "Finistère, France": {"container": "Brittany"},
    "Gard, France": {"container": "Occitania"},
    "Haute-Garonne, France": {"container": "Occitania"},
    "Gers, France": {"container": "Occitania"},
    "Gironde, France": {"container": "Nouvelle-Aquitaine"},
    "Hérault, France": {"container": "Occitania"},
    "Ille-et-Vilaine, France": {"container": "Brittany"},
    "Indre, France": {"container": "Centre-Val de Loire"},
    "Indre-et-Loire, France": {"container": "Centre-Val de Loire"},
    "Isère, France": {"container": "Auvergne-Rhône-Alpes"},
    "Jura, France": {"container": "Bourgogne-Franche-Comté", "wp": "%l (department)"},
    "Landes, France": {"container": "Nouvelle-Aquitaine", "wp": "%l (department)"},
    "Loir-et-Cher, France": {"container": "Centre-Val de Loire"},
    "Loire, France": {"container": "Auvergne-Rhône-Alpes", "wp": "%l (department)"},
    "Haute-Loire, France": {"container": "Auvergne-Rhône-Alpes"},
    "Loire-Atlantique, France": {"container": "Pays de la Loire"},
    "Loiret, France": {"container": "Centre-Val de Loire"},
    "Lot, France": {"container": "Occitania", "wp": "%l (department)"},
    "Lot-et-Garonne, France": {"container": "Nouvelle-Aquitaine"},
    "Lozère, France": {"container": "Occitania"},
    "Maine-et-Loire, France": {"container": "Pays de la Loire"},
    "Manche, France": {"container": "Normandy"},
    "Marne, France": {"container": "Grand Est", "wp": "%l (department)"},
    "Haute-Marne, France": {"container": "Grand Est"},
    "Mayenne, France": {"container": "Pays de la Loire"},
    "Meurthe-et-Moselle, France": {"container": "Grand Est"},
    "Meuse, France": {"container": "Grand Est", "wp": "%l (department)"},
    "Morbihan, France": {"container": "Brittany"},
    "Moselle, France": {"container": "Grand Est", "wp": "%l (department)"},
    "Nièvre, France": {"container": "Bourgogne-Franche-Comté"},
    "Nord, France": {"container": "Hauts-de-France", "wp": "%l (French department)"},
    "Oise, France": {"container": "Hauts-de-France"},
    "Orne, France": {"container": "Normandy"},
    "Pas-de-Calais, France": {"container": "Hauts-de-France"},
    "Puy-de-Dôme, France": {"container": "Auvergne-Rhône-Alpes"},
    "Pyrénées-Atlantiques, France": {"container": "Nouvelle-Aquitaine"},
    "Hautes-Pyrénées, France": {"container": "Occitania"},
    "Pyrénées-Orientales, France": {"container": "Occitania"},
    "Bas-Rhin, France": {"container": "Grand Est"},
    "Haut-Rhin, France": {"container": "Grand Est"},
    "Rhône, France": {"container": "Auvergne-Rhône-Alpes", "wp": "%l (department)"},
    "Metropolis of Lyon, France": {"container": "Auvergne-Rhône-Alpes", "the": True},
    "Lyon Metropolis, France": {"alias_of": "Metropolis of Lyon, France"},
    "Lyon, France": {"alias_of": "Metropolis of Lyon, France"},
    "Haute-Saône, France": {"container": "Bourgogne-Franche-Comté"},
    "Saône-et-Loire, France": {"container": "Bourgogne-Franche-Comté"},
    "Sarthe, France": {"container": "Pays de la Loire"},
    "Savoie, France": {"container": "Auvergne-Rhône-Alpes"},
    "Haute-Savoie, France": {"container": "Auvergne-Rhône-Alpes"},
    "Paris, France": {"container": "Île-de-France"},
    "Seine-Maritime, France": {"container": "Normandy"},
    "Seine-et-Marne, France": {"container": "Île-de-France"},
    "Yvelines, France": {"container": "Île-de-France"},
    "Deux-Sèvres, France": {"container": "Nouvelle-Aquitaine"},
    "Somme, France": {"container": "Hauts-de-France", "wp": "%l (department)"},
    "Tarn, France": {"container": "Occitania", "wp": "%l (department)"},
    "Tarn-et-Garonne, France": {"container": "Occitania"},
    "Var, France": {"container": "Provence-Alpes-Côte d'Azur", "wp": "%l (department)"},
    "Vaucluse, France": {"container": "Provence-Alpes-Côte d'Azur"},
    "Vendée, France": {"container": "Pays de la Loire"},
    "Vienne, France": {"container": "Nouvelle-Aquitaine", "wp": "%l (department)"},
    "Haute-Vienne, France": {"container": "Nouvelle-Aquitaine"},
    "Vosges, France": {"container": "Grand Est", "wp": "%l (department)"},
    "Yonne, France": {"container": "Bourgogne-Franche-Comté"},
    "Territoire de Belfort, France": {"container": "Bourgogne-Franche-Comté"},
    "Essonne, France": {"container": "Île-de-France"},
    "Hauts-de-Seine, France": {"container": "Île-de-France"},
    "Seine-Saint-Denis, France": {"container": "Île-de-France"},
    "Val-de-Marne, France": {"container": "Île-de-France"},
    "Val-d'Oise, France": {"container": "Île-de-France"},
}

FRANCE_DEPARTMENTS_GROUP = {
    "placename_to_key": make_placename_to_key(", France"),
    "canonicalize_key_container": make_canonicalize_key_container(", France", "region"),
    "default_placetype": "department",
    "default_divs": [
        "communes",
        {"type": "municipalities", "cat_as": "communes"},
    ],
    "data": FRANCE_DEPARTMENTS,
}


GERMANY_STATES = {
    "Baden-Württemberg, Germany": {},
    "Bavaria, Germany": {},
    "Brandenburg, Germany": {},
    "Hesse, Germany": {},
    "Lower Saxony, Germany": {},
    "Mecklenburg-Vorpommern, Germany": {},
    "Mecklenburg-Western Pomerania, Germany": {
        "alias_of": "Mecklenburg-Vorpommern, Germany",
        "display": True,
    },
    "North Rhine-Westphalia, Germany": {},
    "Rhineland-Palatinate, Germany": {},
    "Saarland, Germany": {},
    "Saxony, Germany": {},
    "Saxony-Anhalt, Germany": {},
    "Schleswig-Holstein, Germany": {},
    "Thuringia, Germany": {},
}
GERMANY_GROUP = {
    "default_container": "Germany",
    "default_placetype": "state",
    "default_divs": ["districts", "municipalities"],
    "data": GERMANY_STATES,
}

GREECE_REGIONS = {
    "Attica, Greece": {"wp": "%l (region)"},
    "Central Greece, Greece": {"wp": "%l (administrative region)"},
    "Central Macedonia, Greece": {},
    "Crete, Greece": {},
    "Eastern Macedonia and Thrace, Greece": {},
    "Epirus, Greece": {"wp": "%l (region)"},
    "Ionian Islands, Greece": {"the": True, "wp": "%l (region)"},
    "North Aegean, Greece": {"the": True},
    "Peloponnese, Greece": {"wp": "%l (region)"},
    "South Aegean, Greece": {"the": True},
    "Thessaly, Greece": {},
    "Western Greece, Greece": {},
    "Western Macedonia, Greece": {},
    "Mount Athos, Greece": {"placetype": ["autonomous region", "region"], "wp": "Monastic community of Mount Athos"},
}
GREECE_GROUP = {"default_container": "Greece", "default_placetype": "region", "data": GREECE_REGIONS}

india_polity_with_divisions = ["divisions", "districts"]
india_polity_without_divisions = ["districts"]

INDIA_STATES_AND_UNION_TERRITORIES = {
    "Andaman and Nicobar Islands, India": {
        "the": True,
        "placetype": "union territory",
        "divs": india_polity_without_divisions,
    },
    "Andhra Pradesh, India": {
        "divs": india_polity_without_divisions,
    },
    "Arunachal Pradesh, India": {
        "divs": india_polity_with_divisions,
    },
    "Assam, India": {
        "divs": india_polity_with_divisions,
    },
    "Bihar, India": {
        "divs": india_polity_with_divisions,
    },
    "Chandigarh, India": {
        "placetype": "union territory",
        "divs": india_polity_without_divisions,
    },
    "Chhattisgarh, India": {
        "divs": india_polity_with_divisions,
    },
    "Dadra and Nagar Haveli and Daman and Diu, India": {
        "placetype": "union territory",
        "divs": india_polity_without_divisions,
    },
    "Delhi, India": {
        "placetype": "union territory",
        "divs": india_polity_with_divisions,
    },
    "Goa, India": {
        "divs": india_polity_without_divisions,
    },
    "Gujarat, India": {
        "divs": india_polity_without_divisions,
    },
    "Haryana, India": {
        "divs": india_polity_with_divisions,
    },
    "Himachal Pradesh, India": {
        "divs": india_polity_with_divisions,
    },
    "Jammu and Kashmir, India": {
        "placetype": "union territory",
        "divs": india_polity_with_divisions,
        "wp": "%l (union territory)",
    },
    "Jharkhand, India": {
        "divs": india_polity_with_divisions,
    },
    "Karnataka, India": {
        "divs": india_polity_with_divisions,
    },
    "Kerala, India": {
        "divs": india_polity_without_divisions,
    },
    "Ladakh, India": {
        "placetype": "union territory",
        "divs": india_polity_with_divisions,
    },
    "Lakshadweep, India": {
        "placetype": "union territory",
        "divs": india_polity_without_divisions,
    },
    "Madhya Pradesh, India": {
        "divs": india_polity_with_divisions,
    },
    "Maharashtra, India": {
        "divs": india_polity_with_divisions,
    },
    "Manipur, India": {
        "divs": india_polity_without_divisions,
    },
    "Meghalaya, India": {
        "divs": india_polity_with_divisions,
    },
    "Mizoram, India": {
        "divs": india_polity_without_divisions,
    },
    "Nagaland, India": {
        "divs": india_polity_with_divisions,
    },
    "Odisha, India": {
        "divs": india_polity_with_divisions,
    },
    "Puducherry, India": {
        "placetype": "union territory",
        "divs": india_polity_without_divisions,
        "wp": "%l (union territory)",
    },
    "Pondicherry, India": {
        "alias_of": "Puducherry, India",
        "display": True,
    },
    "Punjab, India": {
        "divs": india_polity_with_divisions,
        "wp": "%l, %c",
    },
    "Rajasthan, India": {
        "divs": india_polity_with_divisions,
    },
    "Sikkim, India": {
        "divs": india_polity_without_divisions,
    },
    "Tamil Nadu, India": {
        "divs": india_polity_without_divisions,
    },
    "Telangana, India": {
        "divs": india_polity_without_divisions,
    },
    "Tripura, India": {
        "divs": india_polity_without_divisions,
    },
    "Uttar Pradesh, India": {
        "divs": india_polity_with_divisions,
    },
    "Uttarakhand, India": {
        "divs": india_polity_with_divisions,
    },
    "West Bengal, India": {
        "divs": india_polity_with_divisions,
    },
}
INDIA_GROUP = {"default_container": "India", "default_placetype": "state", "data": INDIA_STATES_AND_UNION_TERRITORIES}
INDONESIA_PROVINCES = {
    "Aceh, Indonesia": {},
    "Bali, Indonesia": {},
    "Bangka Belitung Islands, Indonesia": {"the": True},
    "Banten, Indonesia": {},
    "Bengkulu, Indonesia": {},
    "Central Java, Indonesia": {},
    "Central Kalimantan, Indonesia": {},
    "Central Papua, Indonesia": {},
    "Central Sulawesi, Indonesia": {},
    "East Java, Indonesia": {},
    "East Kalimantan, Indonesia": {},
    "East Nusa Tenggara, Indonesia": {},
    "Gorontalo, Indonesia": {},
    "Highland Papua, Indonesia": {"wp": "%l"},
    "Special Capital Region of Jakarta, Indonesia": {"the": True, "wp": "Jakarta"},
    "Jakarta, Indonesia": {"alias_of": "Special Capital Region of Jakarta, Indonesia"},
    "Jambi, Indonesia": {},
    "Lampung, Indonesia": {},
    "Maluku, Indonesia": {},
    "North Kalimantan, Indonesia": {},
    "North Maluku, Indonesia": {},
    "North Sulawesi, Indonesia": {},
    "North Papua, Indonesia": {},
    "North Sumatra, Indonesia": {},
    "Papua, Indonesia": {"wp": "%l (province)"},
    "Riau, Indonesia": {},
    "Riau Islands, Indonesia": {"the": True},
    "Southeast Sulawesi, Indonesia": {},
    "South Kalimantan, Indonesia": {},
    "South Papua, Indonesia": {},
    "South Sulawesi, Indonesia": {},
    "South Sumatra, Indonesia": {},
    "Southwest Papua, Indonesia": {},
    "West Java, Indonesia": {},
    "West Kalimantan, Indonesia": {},
    "West Nusa Tenggara, Indonesia": {},
    "West Papua, Indonesia": {"wp": "%l (province)"},
    "West Sulawesi, Indonesia": {},
    "West Sumatra, Indonesia": {},
    "Special Region of Yogyakarta, Indonesia": {"the": True},
    "Yogyakarta, Indonesia": {"alias_of": "Special Region of Yogyakarta, Indonesia"},
}
INDONESIA_GROUP = {"default_container": "Indonesia", "default_placetype": "province", "data": INDONESIA_PROVINCES}

IRAN_PROVINCES = {
    "Alborz Province, Iran": {},
    "Ardabil Province, Iran": {},
    "Bushehr Province, Iran": {},
    "Chaharmahal and Bakhtiari Province, Iran": {},
    "East Azerbaijan Province, Iran": {},
    "Fars Province, Iran": {},
    "Pars Province, Iran": {"alias_of": "Fars Province, Iran", "display": True},
    "Gilan Province, Iran": {},
    "Golestan Province, Iran": {},
    "Hamadan Province, Iran": {},
    "Hormozgan Province, Iran": {},
    "Ilam Province, Iran": {},
    "Isfahan Province, Iran": {},
    "Kerman Province, Iran": {},
    "Kermanshah Province, Iran": {},
    "Khuzestan Province, Iran": {},
    "Kohgiluyeh and Boyer-Ahmad Province, Iran": {},
    "Kurdistan Province, Iran": {},
    "Lorestan Province, Iran": {},
    "Markazi Province, Iran": {},
    "Mazandaran Province, Iran": {},
    "North Khorasan Province, Iran": {},
    "Qazvin Province, Iran": {},
    "Qom Province, Iran": {},
    "Razavi Khorasan Province, Iran": {},
    "Semnan Province, Iran": {},
    "Sistan and Baluchestan Province, Iran": {},
    "South Khorasan Province, Iran": {},
    "Tehran Province, Iran": {},
    "West Azerbaijan Province, Iran": {},
    "Yazd Province, Iran": {},
    "Zanjan Province, Iran": {},
}
IRAN_GROUP = {
    "key_to_placename": make_key_to_placename(", Iran", " Province$"),
    "placename_to_key": make_placename_to_key(", Iran", " Province"),
    "default_container": "Iran",
    "default_placetype": "province",
    "default_wp": "%e province",
    "data": IRAN_PROVINCES,
}

IRELAND_COUNTIES: dict[str, Any] = {
    "County Carlow, Ireland": {},
    "County Cavan, Ireland": {},
    "County Clare, Ireland": {},
    "County Cork, Ireland": {},
    "County Donegal, Ireland": {},
    "County Dublin, Ireland": {},
    "County Galway, Ireland": {},
    "County Kerry, Ireland": {},
    "County Kildare, Ireland": {},
    "County Kilkenny, Ireland": {},
    "County Laois, Ireland": {},
    "County Leitrim, Ireland": {},
    "County Limerick, Ireland": {},
    "County Longford, Ireland": {},
    "County Louth, Ireland": {},
    "County Mayo, Ireland": {},
    "County Meath, Ireland": {},
    "County Monaghan, Ireland": {},
    "County Offaly, Ireland": {},
    "County Roscommon, Ireland": {},
    "County Sligo, Ireland": {},
    "County Tipperary, Ireland": {},
    "County Waterford, Ireland": {},
    "County Westmeath, Ireland": {},
    "County Wexford, Ireland": {},
    "County Wicklow, Ireland": {},
}

IRELAND_GROUP = {
    "key_to_placename": (lambda key: ((key := re.sub(r", Ireland$", "", key)), re.sub(r"^County ", "", key))),
    "placename_to_key": (
        lambda placename: (
            (placename if placename.startswith(("County ", "City ")) else f"County {placename}") + ", Ireland"
        )
    ),
    "default_container": "Ireland",
    "default_placetype": "county",
    "data": IRELAND_COUNTIES,
}

ITALY_ADMINISTRATIVE_REGIONS = {
    "Abruzzo, Italy": {},
    "Aosta Valley, Italy": {"placetype": ["autonomous region", "administrative region", "region"]},
    "Apulia, Italy": {},
    "Basilicata, Italy": {},
    "Calabria, Italy": {},
    "Campania, Italy": {},
    "Emilia-Romagna, Italy": {},
    "Friuli-Venezia Giulia, Italy": {"placetype": ["autonomous region", "administrative region", "region"]},
    "Lazio, Italy": {},
    "Liguria, Italy": {},
    "Lombardy, Italy": {},
    "Marche, Italy": {},
    "Molise, Italy": {},
    "Piedmont, Italy": {},
    "Sardinia, Italy": {"placetype": ["autonomous region", "administrative region", "region"]},
    "Sicily, Italy": {"placetype": ["autonomous region", "administrative region", "region"]},
    "Trentino-Alto Adige, Italy": {"placetype": ["autonomous region", "administrative region", "region"]},
    "Tuscany, Italy": {},
    "Umbria, Italy": {},
    "Veneto, Italy": {},
}

ITALY_GROUP = {"default_container": "Italy", "default_placetype": "region", "data": ITALY_ADMINISTRATIVE_REGIONS}


def laos_placename_to_key(placename: str) -> str:
    if placename == "Vientiane Prefecture":
        return f"{placename}, Laos"
    if placename.endswith(" Province"):
        return f"{placename}, Laos"
    return f"{placename} Province, Laos"


JAPAN_PREFECTURES = {
    "Aichi Prefecture, Japan": {},
    "Akita Prefecture, Japan": {},
    "Aomori Prefecture, Japan": {},
    "Chiba Prefecture, Japan": {},
    "Ehime Prefecture, Japan": {},
    "Fukui Prefecture, Japan": {},
    "Fukuoka Prefecture, Japan": {},
    "Fukushima Prefecture, Japan": {},
    "Gifu Prefecture, Japan": {},
    "Gunma Prefecture, Japan": {},
    "Hiroshima Prefecture, Japan": {},
    "Hokkaido Prefecture, Japan": {"divs": "subprefectures", "wp": "Hokkaido"},
    "Hyōgo Prefecture, Japan": {},
    "Hyogo Prefecture, Japan": {"alias_of": "Hyōgo Prefecture, Japan", "display": True},
    "Ibaraki Prefecture, Japan": {},
    "Ishikawa Prefecture, Japan": {},
    "Iwate Prefecture, Japan": {},
    "Kagawa Prefecture, Japan": {},
    "Kagoshima Prefecture, Japan": {},
    "Kanagawa Prefecture, Japan": {},
    "Kōchi Prefecture, Japan": {},
    "Kochi Prefecture, Japan": {"alias_of": "Kōchi Prefecture, Japan", "display": True},
    "Kumamoto Prefecture, Japan": {},
    "Kyoto Prefecture, Japan": {},
    "Mie Prefecture, Japan": {},
    "Miyagi Prefecture, Japan": {},
    "Miyazaki Prefecture, Japan": {},
    "Nagano Prefecture, Japan": {},
    "Nagasaki Prefecture, Japan": {},
    "Nara Prefecture, Japan": {},
    "Niigata Prefecture, Japan": {},
    "Ōita Prefecture, Japan": {},
    "Oita Prefecture, Japan": {"alias_of": "Ōita Prefecture, Japan", "display": True},
    "Okayama Prefecture, Japan": {},
    "Okinawa Prefecture, Japan": {},
    "Osaka Prefecture, Japan": {},
    "Saga Prefecture, Japan": {},
    "Saitama Prefecture, Japan": {},
    "Shiga Prefecture, Japan": {},
    "Shimane Prefecture, Japan": {},
    "Shizuoka Prefecture, Japan": {},
    "Tochigi Prefecture, Japan": {},
    "Tokushima Prefecture, Japan": {},
    "Tottori Prefecture, Japan": {},
    "Toyama Prefecture, Japan": {},
    "Wakayama Prefecture, Japan": {},
    "Yamagata Prefecture, Japan": {},
    "Yamaguchi Prefecture, Japan": {},
    "Yamanashi Prefecture, Japan": {},
}
JAPAN_GROUP = {
    "key_to_placename": make_key_to_placename(", Japan$", " Prefecture$"),
    "placename_to_key": make_placename_to_key(", Japan", " Prefecture"),
    "default_container": "Japan",
    "default_placetype": "prefecture",
    "data": JAPAN_PREFECTURES,
}

LAOS_PROVINCES = {
    "Attapeu Province, Laos": {},
    "Bokeo Province, Laos": {},
    "Bolikhamxai Province, Laos": {},
    "Champasak Province, Laos": {},
    "Houaphanh Province, Laos": {},
    "Khammouane Province, Laos": {},
    "Luang Namtha Province, Laos": {},
    "Luang Prabang Province, Laos": {},
    "Oudomxay Province, Laos": {},
    "Phongsaly Province, Laos": {},
    "Salavan Province, Laos": {},
    "Savannakhet Province, Laos": {},
    "Vientiane Province, Laos": {},
    "Vientiane Prefecture, Laos": {"placetype": "prefecture", "wp": "%l"},
    "Sainyabuli Province, Laos": {},
    "Sekong Province, Laos": {},
    "Xaisomboun Province, Laos": {},
    "Xiangkhouang Province, Laos": {},
}
LAOS_GROUP = {
    "key_to_placename": make_key_to_placename(", Laos$", [" Province$", " Prefecture$"]),
    "placename_to_key": laos_placename_to_key,
    "default_container": "Laos",
    "default_placetype": "province",
    "default_wp": "%e province",
    "data": LAOS_PROVINCES,
}

LEBANON_GOVERNORATES = {
    "Akkar Governorate, Lebanon": {},
    "Baalbek-Hermel Governorate, Lebanon": {},
    "Beirut Governorate, Lebanon": {},
    "Beqaa Governorate, Lebanon": {},
    "Keserwan-Jbeil Governorate, Lebanon": {},
    "Mount Lebanon Governorate, Lebanon": {},
    "Nabatieh Governorate, Lebanon": {},
    "North Governorate, Lebanon": {"no_auto_augment_container": True},
    "South Governorate, Lebanon": {"no_auto_augment_container": True},
}
LEBANON_GROUP = {
    "key_to_placename": make_key_to_placename(", Lebanon$", " Governorate$"),
    "placename_to_key": make_placename_to_key(", Lebanon", " Governorate"),
    "default_container": "Lebanon",
    "default_placetype": "governorate",
    "data": LEBANON_GOVERNORATES,
}

MALAYSIA_STATES: dict[str, Any] = {
    "Johor, Malaysia": {},
    "Kedah, Malaysia": {},
    "Kelantan, Malaysia": {},
    "Malacca, Malaysia": {},
    "Negeri Sembilan, Malaysia": {},
    "Pahang, Malaysia": {},
    "Penang, Malaysia": {},
    "Perak, Malaysia": {},
    "Perlis, Malaysia": {},
    "Sabah, Malaysia": {},
    "Sarawak, Malaysia": {},
    "Selangor, Malaysia": {},
    "Terengganu, Malaysia": {},
}
MALAYSIA_GROUP = {
    "default_container": "Malaysia",
    "default_placetype": "state",
    "default_wp": "%l, %c",
    "data": MALAYSIA_STATES,
}

MALTA_REGIONS = {
    "Eastern Region, Malta": {"no_auto_augment_container": True},
    "Gozo Region, Malta": {"wp": "%l"},
    "Northern Region, Malta": {"no_auto_augment_container": True},
    "Port Region, Malta": {},
    "Southern Region, Malta": {"no_auto_augment_container": True},
    "Western Region, Malta": {"no_auto_augment_container": True},
}
MALTA_GROUP = {
    "key_to_placename": make_key_to_placename(", Malta$", " Region"),
    "placename_to_key": make_placename_to_key(", Malta", " Region"),
    "default_container": "Malta",
    "default_placetype": "region",
    "default_wp": "%l, %c",
    "default_the": True,
    "data": MALTA_REGIONS,
}

MEXICO_STATES = {
    "Aguascalientes, Mexico": {},
    "Baja California, Mexico": {},
    "Baja California Norte, Mexico": {"alias_of": "Baja California, Mexico"},
    "Baja California Sur, Mexico": {},
    "Campeche, Mexico": {},
    "Chiapas, Mexico": {},
    "Chihuahua, Mexico": {"wp": "%l (state)"},
    "Coahuila, Mexico": {},
    "Colima, Mexico": {},
    "Durango, Mexico": {},
    "Guanajuato, Mexico": {},
    "Guerrero, Mexico": {},
    "Hidalgo, Mexico": {"wp": "%l (state)"},
    "Jalisco, Mexico": {},
    "State of Mexico, Mexico": {"the": True},
    "Mexico, Mexico": {"alias_of": "State of Mexico, Mexico"},
    "Michoacán, Mexico": {},
    "Michoacan, Mexico": {"alias_of": "Michoacán, Mexico", "display": True},
    "Morelos, Mexico": {},
    "Nayarit, Mexico": {},
    "Nuevo León, Mexico": {},
    "Nuevo Leon, Mexico": {"alias_of": "Nuevo León, Mexico", "display": True},
    "Oaxaca, Mexico": {},
    "Puebla, Mexico": {},
    "Querétaro, Mexico": {},
    "Queretaro, Mexico": {"alias_of": "Querétaro, Mexico", "display": True},
    "Quintana Roo, Mexico": {},
    "San Luis Potosí, Mexico": {},
    "San Luis Potosi, Mexico": {"alias_of": "San Luis Potosí, Mexico", "display": True},
    "Sinaloa, Mexico": {},
    "Sonora, Mexico": {},
    "Tabasco, Mexico": {},
    "Tamaulipas, Mexico": {},
    "Tlaxcala, Mexico": {},
    "Veracruz, Mexico": {},
    "Yucatán, Mexico": {},
    "Yucatan, Mexico": {"alias_of": "Yucatán, Mexico", "display": True},
    "Zacatecas, Mexico": {},
}
MEXICO_GROUP = {"default_container": "Mexico", "default_placetype": "state", "data": MEXICO_STATES}


def moldova_placename_to_key(placename: str, moldova_districts_and_autonomous_territorial_units: dict[str, Any]) -> str:
    elliptical_key = f"{placename}, Moldova"
    if elliptical_key in moldova_districts_and_autonomous_territorial_units:
        return elliptical_key
    if placename.endswith(" District"):
        return f"{placename}, Moldova"
    return f"{placename} District, Moldova"


MOLDOVA_DISTRICTS_AND_AUTONOMOUS_TERRITORIAL_UNITS = {
    "Anenii Noi District, Moldova": {},
    "Basarabeasca District, Moldova": {},
    "Briceni District, Moldova": {},
    "Cahul District, Moldova": {},
    "Cantemir District, Moldova": {},
    "Călărași District, Moldova": {},
    "Căușeni District, Moldova": {},
    "Cimișlia District, Moldova": {},
    "Criuleni District, Moldova": {},
    "Dondușeni District, Moldova": {},
    "Drochia District, Moldova": {},
    "Dubăsari District, Moldova": {},
    "Edineț District, Moldova": {},
    "Fălești District, Moldova": {},
    "Florești District, Moldova": {},
    "Glodeni District, Moldova": {},
    "Hîncești District, Moldova": {},
    "Ialoveni District, Moldova": {},
    "Leova District, Moldova": {},
    "Nisporeni District, Moldova": {},
    "Ocnița District, Moldova": {},
    "Orhei District, Moldova": {},
    "Rezina District, Moldova": {},
    "Rîșcani District, Moldova": {},
    "Sîngerei District, Moldova": {},
    "Soroca District, Moldova": {},
    "Strășeni District, Moldova": {},
    "Șoldănești District, Moldova": {},
    "Ștefan Vodă District, Moldova": {},
    "Taraclia District, Moldova": {},
    "Telenești District, Moldova": {},
    "Ungheni District, Moldova": {},
    "Chișinău, Moldova": {"placetype": "municipality"},
    "Bălți, Moldova": {"placetype": "municipality"},
    "Gagauzia, Moldova": {"placetype": ["autonomous territorial unit", "autonomous region", "region"]},
    "Bender, Moldova": {"placetype": "municipality"},
    "Tighina, Moldova": {"alias_of": "Bender, Moldova"},
    "Transnistria, Moldova": {"placetype": ["autonomous territorial unit", "autonomous region", "region"]},
    "Left Bank of the Dniester, Moldova": {"alias_of": "Transnistria, Moldova", "the": True},
    "Administrative-Territorial Units of the Left Bank of the Dniester, Moldova": {
        "alias_of": "Transnistria, Moldova",
        "the": True,
    },
}
MOLDOVA_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Moldova$", " District"),
    "placename_to_key": moldova_placename_to_key,
    "default_container": "Moldova",
    "default_placetype": ["district", "raion"],
    "default_divs": "communes",
    "data": MOLDOVA_DISTRICTS_AND_AUTONOMOUS_TERRITORIAL_UNITS,
}

MOROCCO_REGIONS = {
    "Tangier-Tetouan-Al Hoceima, Morocco": {},
    "Oriental, Morocco": {"wp": "%l (%c)"},
    "L'Oriental, Morocco": {"alias_of": "Oriental, Morocco", "display": True},
    "Fez-Meknes, Morocco": {},
    "Rabat-Sale-Kenitra, Morocco": {"wp": "Rabat-Salé-Kénitra"},
    "Rabat-Salé-Kénitra, Morocco": {"alias_of": "Rabat-Sale-Kenitra, Morocco", "display": True},
    "Beni Mellal-Khenifra, Morocco": {"wp": "Béni Mellal-Khénifra"},
    "Béni Mellal-Khénifra, Morocco": {"alias_of": "Beni Mellal-Khenifra, Morocco", "display": True},
    "Casablanca-Settat, Morocco": {},
    "Marrakesh-Safi, Morocco": {"wp": "Marrakesh–Safi"},
    "Marrakech-Safi, Morocco": {"alias_of": "Marrakesh-Safi, Morocco", "display": True},
    "Draa-Tafilalet, Morocco": {"wp": "Drâa-Tafilalet"},
    "Drâa-Tafilalet, Morocco": {"alias_of": "Draa-Tafilalet, Morocco", "display": True},
    "Souss-Massa, Morocco": {},
    "Guelmim-Oued Noun, Morocco": {},
    "Laayoune-Sakia El Hamra, Morocco": {"wp": "Laâyoune-Sakia El Hamra"},
    "Laâyoune-Sakia El Hamra, Morocco": {"alias_of": "Laayoune-Sakia El Hamra, Morocco", "display": True},
    "Dakhla-Oued Ed-Dahab, Morocco": {},
}
MOROCCO_GROUP: dict[str, Any] = {
    "default_container": "Morocco",
    "default_placetype": "region",
    "data": MOROCCO_REGIONS,
}

NETHERLANDS_PROVINCES = {
    "Drenthe, Netherlands": {},
    "Flevoland, Netherlands": {},
    "Friesland, Netherlands": {},
    "Gelderland, Netherlands": {},
    "Groningen, Netherlands": {"wp": "%l (province)"},
    "Limburg, Netherlands": {"wp": "%l (%c)"},
    "North Brabant, Netherlands": {},
    "Noord-Brabant, Netherlands": {"alias_of": "North Brabant, Netherlands", "display": True},
    "North Holland, Netherlands": {},
    "Noord-Holland, Netherlands": {"alias_of": "North Holland, Netherlands", "display": True},
    "Overijssel, Netherlands": {},
    "South Holland, Netherlands": {},
    "Zuid-Holland, Netherlands": {"alias_of": "South Holland, Netherlands", "display": True},
    "Utrecht, Netherlands": {"wp": "%l (province)"},
    "Zeeland, Netherlands": {},
}
NETHERLANDS_GROUP: dict[str, Any] = {
    "default_container": "Netherlands",
    "default_placetype": "province",
    "default_divs": "municipalities",
    "data": NETHERLANDS_PROVINCES,
}

NEW_ZEALAND_REGIONS = {
    # North Island regions
    "Northland, New Zealand": {"wp": "%l Region"},
    "Auckland, New Zealand": {"wp": "%l Region"},
    "Waikato, New Zealand": {},
    "Bay of Plenty, New Zealand": {"the": True, "wp": "%l Region"},
    "Gisborne, New Zealand": {"placetype": ["region", "district"], "wp": "%l District"},
    "Hawke's Bay, New Zealand": {},
    "Taranaki, New Zealand": {},
    "Manawatū-Whanganui, New Zealand": {},
    "Manawatu-Whanganui, New Zealand": {"alias_of": "Manawatū-Whanganui, New Zealand", "display": True},
    "Manawatu-Wanganui, New Zealand": {"alias_of": "Manawatū-Whanganui, New Zealand", "display": True},
    "Wellington, New Zealand": {"wp": "%l Region"},
    # South Island regions
    "Tasman, New Zealand": {"placetype": ["region", "district"], "wp": "%l District"},
    "Nelson, New Zealand": {"placetype": ["region", "city"], "wp": "%l, %c", "is_city": True},
    "Marlborough, New Zealand": {"placetype": ["region", "district"], "wp": "%l District"},
    "West Coast, New Zealand": {"the": True, "wp": "%l Region"},
    "Canterbury, New Zealand": {"wp": "%l Region"},
    "Otago, New Zealand": {},
    "Southland, New Zealand": {"wp": "%l Region"},
}
NEW_ZEALAND_GROUP: dict[str, Any] = {
    "default_container": "New Zealand",
    "default_placetype": "region",
    "data": NEW_ZEALAND_REGIONS,
}

NIGERIA_STATES = {
    "Abia State, Nigeria": {},
    "Adamawa State, Nigeria": {},
    "Akwa Ibom State, Nigeria": {},
    "Anambra State, Nigeria": {},
    "Bauchi State, Nigeria": {},
    "Bayelsa State, Nigeria": {},
    "Benue State, Nigeria": {},
    "Borno State, Nigeria": {},
    "Cross River State, Nigeria": {},
    "Delta State, Nigeria": {},
    "Ebonyi State, Nigeria": {},
    "Edo State, Nigeria": {},
    "Ekiti State, Nigeria": {},
    "Enugu State, Nigeria": {},
    "Federal Capital Territory, Nigeria": {
        "placetype": ["federal territory", "territory", "state"],
        "the": True,
        "wp": "%l (%c)",
    },
    "Gombe State, Nigeria": {},
    "Imo State, Nigeria": {},
    "Jigawa State, Nigeria": {},
    "Kaduna State, Nigeria": {},
    "Kano State, Nigeria": {},
    "Katsina State, Nigeria": {},
    "Kebbi State, Nigeria": {},
    "Kogi State, Nigeria": {},
    "Kwara State, Nigeria": {},
    "Lagos State, Nigeria": {},
    "Nasarawa State, Nigeria": {},
    "Niger State, Nigeria": {},
    "Ogun State, Nigeria": {},
    "Ondo State, Nigeria": {},
    "Osun State, Nigeria": {},
    "Oyo State, Nigeria": {},
    "Plateau State, Nigeria": {},
    "Rivers State, Nigeria": {},
    "Sokoto State, Nigeria": {},
    "Taraba State, Nigeria": {},
    "Yobe State, Nigeria": {},
    "Zamfara State, Nigeria": {},
}
NIGERIA_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Nigeria$", " State$"),
    "placename_to_key": make_placename_to_key(", Nigeria", " State"),
    "default_container": "Nigeria",
    "default_placetype": "state",
    "data": NIGERIA_STATES,
}

NORTH_KOREA_PROVINCES = {
    "Chagang Province, North Korea": {},
    "North Hamgyong Province, North Korea": {},
    "South Hamgyong Province, North Korea": {},
    "North Hwanghae Province, North Korea": {},
    "South Hwanghae Province, North Korea": {},
    "Kangwon Province, North Korea": {"wp": "%l (%c)"},
    "North Pyongan Province, North Korea": {},
    "South Pyongan Province, North Korea": {},
    "Ryanggang Province, North Korea": {},
}
NORTH_KOREA_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", North Korea$", " Province$"),
    "placename_to_key": make_placename_to_key(", North Korea", " Province"),
    "default_container": "North Korea",
    "default_placetype": "province",
    "data": NORTH_KOREA_PROVINCES,
}

NORWEGIAN_COUNTIES: dict[str, Any] = {
    "Oslo, Norway": {},
    "Rogaland, Norway": {},
    "Møre og Romsdal, Norway": {},
    "Nordland, Norway": {},
    "Østfold, Norway": {},
    "Akershus, Norway": {},
    "Buskerud, Norway": {},
    "Innlandet, Norway": {},
    "Vestfold, Norway": {},
    "Telemark, Norway": {},
    "Agder, Norway": {},
    "Vestland, Norway": {},
    "Trøndelag, Norway": {},
    "Troms, Norway": {},
    "Finnmark, Norway": {},
}
NORWAY_GROUP: dict[str, Any] = {
    "default_container": "Norway",
    "default_placetype": "county",
    "data": NORWEGIAN_COUNTIES,
}

PAKISTAN_PROVINCES_AND_TERRITORIES = {
    "Azad Kashmir, Pakistan": {
        "placetype": ["administrative territory", "autonomous territory", "territory"],
    },
    "Azad Jammu and Kashmir, Pakistan": {
        "alias_of": "Azad Kashmir, Pakistan",
        "display": True,
    },
    "Balochistan, Pakistan": {
        "wp": "%l, %c",
    },
    "Gilgit-Baltistan, Pakistan": {
        "placetype": ["administrative territory", "territory"],
    },
    "Islamabad Capital Territory, Pakistan": {
        "the": True,
        "placetype": ["federal territory", "administrative territory", "territory"],
    },
    "Islamabad, Pakistan": {
        "alias_of": "Islamabad Capital Territory, Pakistan",
    },
    "Khyber Pakhtunkhwa, Pakistan": {},
    "Punjab, Pakistan": {
        "wp": "%l, %c",
    },
    "Sindh, Pakistan": {},
}
PAKISTAN_GROUP: dict[str, Any] = {
    "default_container": "Pakistan",
    "default_placetype": "province",
    "default_divs": "divisions",
    "data": PAKISTAN_PROVINCES_AND_TERRITORIES,
}

PHILIPPINES_PROVINCES = {
    "Abra, Philippines": {"wp": "%l (province)"},
    "Agusan del Norte, Philippines": {},
    "Agusan del Sur, Philippines": {},
    "Aklan, Philippines": {},
    "Albay, Philippines": {},
    "Antique, Philippines": {"wp": "%l (province)"},
    "Apayao, Philippines": {},
    "Aurora, Philippines": {"wp": "%l (province)"},
    "Basilan, Philippines": {},
    "Bataan, Philippines": {},
    "Batanes, Philippines": {},
    "Batangas, Philippines": {},
    "Benguet, Philippines": {},
    "Biliran, Philippines": {},
    "Bohol, Philippines": {},
    "Bukidnon, Philippines": {},
    "Bulacan, Philippines": {},
    "Cagayan, Philippines": {},
    "Camarines Norte, Philippines": {},
    "Camarines Sur, Philippines": {},
    "Camiguin, Philippines": {},
    "Capiz, Philippines": {},
    "Catanduanes, Philippines": {},
    "Cavite, Philippines": {},
    "Cebu, Philippines": {},
    "Cotabato, Philippines": {},
    "Davao de Oro, Philippines": {},
    "Davao del Norte, Philippines": {},
    "Davao del Sur, Philippines": {},
    "Davao Occidental, Philippines": {},
    "Davao Oriental, Philippines": {},
    "Dinagat Islands, Philippines": {"the": True},
    "Eastern Samar, Philippines": {},
    "Guimaras, Philippines": {},
    "Ifugao, Philippines": {},
    "Ilocos Norte, Philippines": {},
    "Ilocos Sur, Philippines": {},
    "Iloilo, Philippines": {},
    "Isabela, Philippines": {"wp": "%l (province)"},
    "Kalinga, Philippines": {"wp": "%l (province)"},
    "La Union, Philippines": {},
    "Laguna, Philippines": {"wp": "%l (province)"},
    "Lanao del Norte, Philippines": {},
    "Lanao del Sur, Philippines": {},
    "Leyte, Philippines": {"wp": "%l (province)"},
    "Maguindanao del Norte, Philippines": {},
    "Maguindanao del Sur, Philippines": {},
    "Marinduque, Philippines": {},
    "Masbate, Philippines": {},
    "Misamis Occidental, Philippines": {},
    "Misamis Oriental, Philippines": {},
    "Mountain Province, Philippines": {},
    "Negros Occidental, Philippines": {},
    "Negros Oriental, Philippines": {},
    "Northern Samar, Philippines": {},
    "Nueva Ecija, Philippines": {},
    "Nueva Vizcaya, Philippines": {},
    "Occidental Mindoro, Philippines": {},
    "Oriental Mindoro, Philippines": {},
    "Palawan, Philippines": {},
    "Pampanga, Philippines": {},
    "Pangasinan, Philippines": {},
    "Quezon, Philippines": {},
    "Quirino, Philippines": {},
    "Rizal, Philippines": {"wp": "%l (province)"},
    "Romblon, Philippines": {},
    "Samar, Philippines": {"wp": "%l (province)"},
    "Sarangani, Philippines": {},
    "Siquijor, Philippines": {},
    "Sorsogon, Philippines": {},
    "South Cotabato, Philippines": {},
    "Southern Leyte, Philippines": {},
    "Sultan Kudarat, Philippines": {},
    "Sulu, Philippines": {},
    "Surigao del Norte, Philippines": {},
    "Surigao del Sur, Philippines": {},
    "Tarlac, Philippines": {},
    "Tawi-Tawi, Philippines": {},
    "Zambales, Philippines": {},
    "Zamboanga del Norte, Philippines": {},
    "Zamboanga del Sur, Philippines": {},
    "Zamboanga Sibugay, Philippines": {},
    "Metro Manila, Philippines": {"placetype": ["region", "province"]},
}
PHILIPPINES_GROUP: dict[str, Any] = {
    "default_container": "Philippines",
    "default_placetype": "province",
    "default_divs": ["municipalities", "barangays"],
    "data": PHILIPPINES_PROVINCES,
}

POLAND_VOIVODESHIPS = {
    "Lower Silesian Voivodeship, Poland": {},
    "Kuyavian-Pomeranian Voivodeship, Poland": {},
    "Lublin Voivodeship, Poland": {},
    "Lubusz Voivodeship, Poland": {},
    "Lodz Voivodeship, Poland": {"wp": "Łódź Voivodeship"},
    "Łódź Voivodeship, Poland": {"alias_of": "Lodz Voivodeship, Poland", "display": True, "display_as_full": True},
    "Lesser Poland Voivodeship, Poland": {},
    "Masovian Voivodeship, Poland": {},
    "Opole Voivodeship, Poland": {},
    "Subcarpathian Voivodeship, Poland": {},
    "Podlaskie Voivodeship, Poland": {},
    "Pomeranian Voivodeship, Poland": {},
    "Silesian Voivodeship, Poland": {},
    "Holy Cross Voivodeship, Poland": {"wp": "Świętokrzyskie Voivodeship"},
    "Świętokrzyskie Voivodeship, Poland": {
        "alias_of": "Holy Cross Voivodeship, Poland",
        "display": True,
        "display_as_full": True,
    },
    "Warmian-Masurian Voivodeship, Poland": {},
    "Greater Poland Voivodeship, Poland": {},
    "West Pomeranian Voivodeship, Poland": {},
}
POLAND_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Poland$", " Voivodeship$"),
    "placename_to_key": make_placename_to_key(", Poland", " Voivodeship"),
    "default_container": "Poland",
    "default_placetype": "voivodeship",
    "default_divs": [
        {"type": "Polish colonies", "cat_as": [{"type": "villages", "prep": "in"}]},
    ],
    "data": POLAND_VOIVODESHIPS,
}


def portugal_placename_to_key(placename: str) -> str:
    if placename in {"Azores", "Madeira"}:
        return f"{placename}, Portugal"
    if placename.endswith(" District"):
        return f"{placename}, Portugal"
    return f"{placename} District, Portugal"


PORTUGAL_DISTRICTS_AND_AUTONOMOUS_REGIONS = {
    "Azores, Portugal": {"the": True, "placetype": ["autonomous region", "region"]},
    "Aveiro District, Portugal": {},
    "Beja District, Portugal": {},
    "Braga District, Portugal": {},
    "Bragança District, Portugal": {},
    "Castelo Branco District, Portugal": {},
    "Coimbra District, Portugal": {},
    "Évora District, Portugal": {},
    "Faro District, Portugal": {},
    "Guarda District, Portugal": {},
    "Leiria District, Portugal": {},
    "Lisbon District, Portugal": {},
    "Lisboa District, Portugal": {"alias_of": "Lisbon District, Portugal", "display": True},
    "Madeira, Portugal": {"placetype": ["autonomous region", "region"]},
    "Portalegre District, Portugal": {},
    "Porto District, Portugal": {},
    "Santarém District, Portugal": {},
    "Setúbal District, Portugal": {},
    "Viana do Castelo District, Portugal": {},
    "Vila Real District, Portugal": {},
    "Viseu District, Portugal": {},
}
PORTUGAL_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Portugal$", " District$"),
    "placename_to_key": portugal_placename_to_key,
    "default_container": "Portugal",
    "default_placetype": "district",
    "default_divs": "municipalities",
    "data": PORTUGAL_DISTRICTS_AND_AUTONOMOUS_REGIONS,
}

ROMANIA_COUNTIES: dict[str, Any] = {
    "Alba County, Romania": {},
    "Arad County, Romania": {},
    "Argeș County, Romania": {},
    "Bacău County, Romania": {},
    "Bihor County, Romania": {},
    "Bistrița-Năsăud County, Romania": {},
    "Botoșani County, Romania": {},
    "Brașov County, Romania": {},
    "Brăila County, Romania": {},
    "Buzău County, Romania": {},
    "Caraș-Severin County, Romania": {},
    "Cluj County, Romania": {},
    "Constanța County, Romania": {},
    "Covasna County, Romania": {},
    "Călărași County, Romania": {},
    "Dolj County, Romania": {},
    "Dâmbovița County, Romania": {},
    "Galați County, Romania": {},
    "Giurgiu County, Romania": {},
    "Gorj County, Romania": {},
    "Harghita County, Romania": {},
    "Hunedoara County, Romania": {},
    "Ialomița County, Romania": {},
    "Iași County, Romania": {},
    "Ilfov County, Romania": {},
    "Maramureș County, Romania": {},
    "Mehedinți County, Romania": {},
    "Mureș County, Romania": {},
    "Neamț County, Romania": {},
    "Olt County, Romania": {},
    "Prahova County, Romania": {},
    "Satu Mare County, Romania": {},
    "Sibiu County, Romania": {},
    "Suceava County, Romania": {},
    "Sălaj County, Romania": {},
    "Teleorman County, Romania": {},
    "Timiș County, Romania": {},
    "Tulcea County, Romania": {},
    "Vaslui County, Romania": {},
    "Vrancea County, Romania": {},
    "Vâlcea County, Romania": {},
}
ROMANIA_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Romania$", " County$"),
    "placename_to_key": make_placename_to_key(", Romania", " County"),
    "default_container": "Romania",
    "default_placetype": "county",
    "default_divs": "communes",
    "data": ROMANIA_COUNTIES,
}


def make_russia_federal_subject_spec(
    spectype: str, use_the: bool | None = None, wp: str | None = None
) -> dict[str, Any]:
    return {
        "placetype": spectype,
        "the": bool(use_the),
        "bare_category_parent_type": ["federal subjects", f"{spectype}s"],
        "wp": wp,
    }


RUSSIA_AUTONOMOUS_OKRUG_NO_THE: dict[str, Any] = {
    "placetype": ["autonomous okrug", "okrug"],
    "bare_category_parent_type": ["federal subjects", "autonomous okrugs"],
}

RUSSIA_AUTONOMOUS_OKRUG_THE: dict[str, Any] = {
    "placetype": ["autonomous okrug", "okrug"],
    "bare_category_parent_type": ["federal subjects", "autonomous okrugs"],
    "the": True,
}
RUSSIA_KRAI = make_russia_federal_subject_spec("krai")
RUSSIA_OBLAST = make_russia_federal_subject_spec("oblast")
RUSSIA_REPUBLIC_THE = make_russia_federal_subject_spec("republic", use_the=True)
RUSSIA_REPUBLIC_NO_THE = make_russia_federal_subject_spec("republic")


RUSSIA_FEDERAL_SUBJECTS: dict[str, Any] = {
    # autonomous oblasts
    "Jewish Autonomous Oblast, Russia": {
        "the": True,
        "placetype": ["autonomous oblast", "oblast"],
        "bare_category_parent_type": ["federal subjects", "autonomous oblasts"],
    },
    # autonomous okrugs
    "Chukotka Autonomous Okrug, Russia": RUSSIA_AUTONOMOUS_OKRUG_THE,
    "Chukotka, Russia": {"alias_of": "Chukotka Autonomous Okrug, Russia"},
    "Khanty-Mansi Autonomous Okrug, Russia": RUSSIA_AUTONOMOUS_OKRUG_THE,
    "Khanty-Mansia, Russia": {"alias_of": "Khanty-Mansi Autonomous Okrug, Russia"},
    "Khantia-Mansia, Russia": {"alias_of": "Khanty-Mansi Autonomous Okrug, Russia"},
    "Yugra, Russia": {"alias_of": "Khanty-Mansi Autonomous Okrug, Russia"},
    "Nenets Autonomous Okrug, Russia": RUSSIA_AUTONOMOUS_OKRUG_THE,
    "Nenetsia, Russia": {"alias_of": "Nenets Autonomous Okrug, Russia"},
    "Yamalo-Nenets Autonomous Okrug, Russia": RUSSIA_AUTONOMOUS_OKRUG_THE,
    "Yamalia, Russia": {"alias_of": "Yamalo-Nenets Autonomous Okrug, Russia"},
    # krais
    "Altai Krai, Russia": RUSSIA_KRAI,
    "Kamchatka Krai, Russia": RUSSIA_KRAI,
    "Khabarovsk Krai, Russia": RUSSIA_KRAI,
    "Krasnodar Krai, Russia": RUSSIA_KRAI,
    "Krasnoyarsk Krai, Russia": RUSSIA_KRAI,
    "Perm Krai, Russia": RUSSIA_KRAI,
    "Primorsky Krai, Russia": RUSSIA_KRAI,
    "Stavropol Krai, Russia": RUSSIA_KRAI,
    "Zabaykalsky Krai, Russia": RUSSIA_KRAI,
    # oblasts
    "Amur Oblast, Russia": RUSSIA_OBLAST,
    "Arkhangelsk Oblast, Russia": RUSSIA_OBLAST,
    "Astrakhan Oblast, Russia": RUSSIA_OBLAST,
    "Belgorod Oblast, Russia": RUSSIA_OBLAST,
    "Bryansk Oblast, Russia": RUSSIA_OBLAST,
    "Chelyabinsk Oblast, Russia": RUSSIA_OBLAST,
    "Irkutsk Oblast, Russia": RUSSIA_OBLAST,
    "Ivanovo Oblast, Russia": RUSSIA_OBLAST,
    "Kaliningrad Oblast, Russia": RUSSIA_OBLAST,
    "Kaluga Oblast, Russia": RUSSIA_OBLAST,
    "Kemerovo Oblast, Russia": RUSSIA_OBLAST,
    "Kirov Oblast, Russia": RUSSIA_OBLAST,
    "Kostroma Oblast, Russia": RUSSIA_OBLAST,
    "Kurgan Oblast, Russia": RUSSIA_OBLAST,
    "Kursk Oblast, Russia": RUSSIA_OBLAST,
    "Leningrad Oblast, Russia": RUSSIA_OBLAST,
    "Lipetsk Oblast, Russia": RUSSIA_OBLAST,
    "Magadan Oblast, Russia": RUSSIA_OBLAST,
    "Moscow Oblast, Russia": RUSSIA_OBLAST,
    "Murmansk Oblast, Russia": RUSSIA_OBLAST,
    "Nizhny Novgorod Oblast, Russia": RUSSIA_OBLAST,
    "Novgorod Oblast, Russia": RUSSIA_OBLAST,
    "Novosibirsk Oblast, Russia": RUSSIA_OBLAST,
    "Omsk Oblast, Russia": RUSSIA_OBLAST,
    "Orenburg Oblast, Russia": RUSSIA_OBLAST,
    "Oryol Oblast, Russia": RUSSIA_OBLAST,
    "Penza Oblast, Russia": RUSSIA_OBLAST,
    "Pskov Oblast, Russia": RUSSIA_OBLAST,
    "Rostov Oblast, Russia": RUSSIA_OBLAST,
    "Ryazan Oblast, Russia": RUSSIA_OBLAST,
    "Sakhalin Oblast, Russia": RUSSIA_OBLAST,
    "Samara Oblast, Russia": RUSSIA_OBLAST,
    "Saratov Oblast, Russia": RUSSIA_OBLAST,
    "Smolensk Oblast, Russia": RUSSIA_OBLAST,
    "Sverdlovsk Oblast, Russia": RUSSIA_OBLAST,
    "Tambov Oblast, Russia": RUSSIA_OBLAST,
    "Tomsk Oblast, Russia": RUSSIA_OBLAST,
    "Tula Oblast, Russia": RUSSIA_OBLAST,
    "Tver Oblast, Russia": RUSSIA_OBLAST,
    "Tyumen Oblast, Russia": RUSSIA_OBLAST,
    "Ulyanovsk Oblast, Russia": RUSSIA_OBLAST,
    "Vladimir Oblast, Russia": RUSSIA_OBLAST,
    "Volgograd Oblast, Russia": RUSSIA_OBLAST,
    "Vologda Oblast, Russia": RUSSIA_OBLAST,
    "Voronezh Oblast, Russia": RUSSIA_OBLAST,
    "Yaroslavl Oblast, Russia": RUSSIA_OBLAST,
    # republics
    "Adygea, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Adygea, Russia": {"alias_of": "Adygea, Russia", "the": True},
    "Bashkortostan, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Bashkortostan, Russia": {"alias_of": "Bashkortostan, Russia", "the": True},
    "Bashkiria, Russia": {"alias_of": "Bashkortostan, Russia"},
    "Buryatia, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Buryatia, Russia": {"alias_of": "Buryatia, Russia", "the": True},
    "Dagestan, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Dagestan, Russia": {"alias_of": "Dagestan, Russia", "the": True},
    "Ingushetia, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Ingushetia, Russia": {"alias_of": "Ingushetia, Russia", "the": True},
    "Kalmykia, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Kalmykia, Russia": {"alias_of": "Kalmykia, Russia", "the": True},
    "Karelia, Russia": make_russia_federal_subject_spec("republic", None, "Republic of Karelia"),
    "Republic of Karelia, Russia": {"alias_of": "Karelia, Russia", "the": True},
    "Khakassia, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Khakassia, Russia": {"alias_of": "Khakassia, Russia", "the": True},
    "Mordovia, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Mordovia, Russia": {"alias_of": "Mordovia, Russia", "the": True},
    "North Ossetia-Alania, Russia": make_russia_federal_subject_spec("republic", None, "North Ossetia–Alania"),
    "Republic of North Ossetia-Alania, Russia": {"alias_of": "North Ossetia-Alania, Russia", "the": True},
    "North Ossetia, Russia": {"alias_of": "North Ossetia-Alania, Russia", "display": True},
    "Alania, Russia": {"alias_of": "North Ossetia-Alania, Russia", "display": True},
    "Tatarstan, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Republic of Tatarstan, Russia": {"alias_of": "Tatarstan, Russia", "the": True},
    "Altai Republic, Russia": RUSSIA_REPUBLIC_THE,
    "Chechnya, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Chechen Republic, Russia": {"alias_of": "Chechnya, Russia", "the": True},
    "Chuvashia, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Chuvash Republic, Russia": {"alias_of": "Chuvashia, Russia", "the": True},
    "Kabardino-Balkaria, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Kabardino-Balkariya, Russia": {"alias_of": "Kabardino-Balkaria, Russia", "display": True},
    "Kabardino-Balkarian Republic, Russia": {"alias_of": "Kabardino-Balkaria, Russia", "the": True},
    "Kabardino-Balkar Republic, Russia": {
        "alias_of": "Kabardino-Balkaria, Russia",
        "display": "Kabardino-Balkarian Republic, Russia",
        "the": True,
    },
    "Karachay-Cherkessia, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Karachay-Cherkess Republic, Russia": {"alias_of": "Karachay-Cherkessia, Russia"},
    "Komi, Russia": make_russia_federal_subject_spec("republic", None, "Komi Republic"),
    "Komi Republic, Russia": {"alias_of": "Komi, Russia", "the": True},
    "Mari El, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Mari El Republic, Russia": {"alias_of": "Mari El, Russia", "the": True},
    "Sakha, Russia": make_russia_federal_subject_spec("republic", None, "Sakha Republic"),
    "Sakha Republic, Russia": {"alias_of": "Sakha, Russia", "the": True},
    "Yakutia, Russia": {"alias_of": "Sakha, Russia"},
    "Yakutiya, Russia": {"alias_of": "Sakha, Russia", "display": "Yakutia, Russia"},
    "Republic of Yakutia (Sakha), Russia": {
        "alias_of": "Sakha, Russia",
        "display": "Sakha Republic, Russia",
        "the": True,
    },
    "Tuva, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Tyva, Russia": {"alias_of": "Tuva, Russia", "display": True},
    "Tuva Republic, Russia": {"alias_of": "Tuva, Russia", "the": True},
    "Tyva Republic, Russia": {"alias_of": "Tuva, Russia", "display": "Tuva Republic, Russia", "the": True},
    "Udmurtia, Russia": RUSSIA_REPUBLIC_NO_THE,
    "Udmurt Republic, Russia": {"alias_of": "Udmurtia, Russia", "the": True},
}


def russia_key_to_placename(key: str) -> tuple[str, str]:
    key_cleaned = re.sub(r",.*", "", key)
    full_placename = key_cleaned
    if key_cleaned == "Jewish Autonomous Oblast":
        return full_placename, full_placename
    for suffix in ["Krai", "Oblast"]:
        m = re.match(rf"^(.*) {suffix}$", key_cleaned)
        if m:
            elliptical_placename = m[1]
            return full_placename, elliptical_placename
    return full_placename, full_placename


def russia_placename_to_key(placename: str, russia_federal_subjects: dict[str, Any]) -> str:
    key = f"{placename}, Russia"
    if key in russia_federal_subjects:
        return key
    for suffix in ["Krai", "Oblast"]:
        suffixed_key = f"{placename} {suffix}, Russia"
        if suffixed_key in russia_federal_subjects:
            return suffixed_key
    return f"{placename}, Russia"


def construct_russia_federal_subject_keydesc(group: dict[str, Any], key: str, spec: dict[str, Any]) -> str:
    placename = re.sub(r",.*", "", key)
    linked_placename = group["construct_linked_placename"](spec, placename)
    placetype = spec["placetype"]
    if isinstance(placetype, Sequence) and not isinstance(placetype, str):
        placetype = placetype[0]
    return f"{linked_placename}, a federal subject ({placetype}) of Russia"


RUSSIA_GROUP: dict[str, Any] = {
    "key_to_placename": russia_key_to_placename,
    "placename_to_key": russia_placename_to_key,
    "default_container": "Russia",
    "default_keydesc": construct_russia_federal_subject_keydesc,
    "default_overriding_bare_label_parents": ["federal subjects of Russia", "+++"],
    "data": RUSSIA_FEDERAL_SUBJECTS,
}

SAUDI_ARABIA_PROVINCES = {
    "Riyadh Province, Saudi Arabia": {},
    "Mecca Province, Saudi Arabia": {},
    "Eastern Province, Saudi Arabia": {
        "no_auto_augment_container": True,
        "wp": "%l, %c",
    },
    "Medina Province, Saudi Arabia": {"wp": "%l (%c)"},
    "Aseer Province, Saudi Arabia": {"wp": "Asir"},
    "Asir Province, Saudi Arabia": {
        "alias_of": "Aseer Province, Saudi Arabia",
        "display": True,
    },
    "Jazan Province, Saudi Arabia": {},
    "Qassim Province, Saudi Arabia": {"wp": "Al-Qassim Province"},
    "Al-Qassim Province, Saudi Arabia": {
        "alias_of": "Qassim Province, Saudi Arabia",
        "display": True,
    },
    "Tabuk Province, Saudi Arabia": {},
    "Hail Province, Saudi Arabia": {"wp": "Ḥa'il Province"},
    "Ha'il Province, Saudi Arabia": {
        "alias_of": "Hail Province, Saudi Arabia",
        "display": True,
    },
    "Ḥa'il Province, Saudi Arabia": {
        "alias_of": "Hail Province, Saudi Arabia",
        "display": True,
    },
    "Al-Jouf Province, Saudi Arabia": {"wp": "Al-Jawf Province"},
    "Al-Jawf Province, Saudi Arabia": {
        "alias_of": "Al-Jouf Province, Saudi Arabia",
        "display": True,
    },
    "Najran Province, Saudi Arabia": {},
    "Northern Borders Province, Saudi Arabia": {},
    "Al-Bahah Province, Saudi Arabia": {},
}
SAUDI_ARABIA_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Saudi Arabia$", " Province$"),
    "placename_to_key": make_placename_to_key(", Saudi Arabia", " Province"),
    "default_container": "Saudi Arabia",
    "default_placetype": "province",
    "data": SAUDI_ARABIA_PROVINCES,
}

SOUTH_AFRICA_PROVINCES = {
    "Eastern Cape, South Africa": {"the": True},
    "Free State, South Africa": {"the": True, "wp": "%l (province)"},
    "Gauteng, South Africa": {},
    "KwaZulu-Natal, South Africa": {},
    "Limpopo, South Africa": {},
    "Mpumalanga, South Africa": {},
    "North West, South Africa": {"wp": "%l (South African province)"},
    "Northern Cape, South Africa": {"the": True},
    "Western Cape, South Africa": {"the": True},
}
SOUTH_AFRICA_GROUP: dict[str, Any] = {
    "default_container": "South Africa",
    "default_placetype": "province",
    "default_divs": "municipalities",
    "data": SOUTH_AFRICA_PROVINCES,
}

SOUTH_KOREA_PROVINCES = {
    "North Chungcheong Province, South Korea": {},
    "South Chungcheong Province, South Korea": {},
    "Gangwon Province, South Korea": {"wp": "%l, %c"},
    "Gyeonggi Province, South Korea": {},
    "North Gyeongsang Province, South Korea": {},
    "South Gyeongsang Province, South Korea": {},
    "North Jeolla Province, South Korea": {},
    "South Jeolla Province, South Korea": {},
    "Jeju Province, South Korea": {},
}
SOUTH_KOREA_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", South Korea$", " Province$"),
    "placename_to_key": make_placename_to_key(", South Korea", " Province"),
    "default_container": "South Korea",
    "default_placetype": "province",
    "data": SOUTH_KOREA_PROVINCES,
}

SPAIN_AUTONOMOUS_COMMUNITIES = {
    "Andalusia, Spain": {},
    "Aragon, Spain": {},
    "Asturias, Spain": {},
    "Balearic Islands, Spain": {"the": True},
    "Basque Country, Spain": {"the": True, "wp": "%l (autonomous community)"},
    "Canary Islands, Spain": {"the": True},
    "Cantabria, Spain": {},
    "Castile and León, Spain": {},
    "Castilla-La Mancha, Spain": {"wp": "Castilla–La Mancha"},
    "Catalonia, Spain": {},
    "Community of Madrid, Spain": {"the": True},
    "Extremadura, Spain": {},
    "Galicia, Spain": {"wp": "%l (Spain)"},
    "La Rioja, Spain": {},
    "Murcia, Spain": {"wp": "Region of %l"},
    "Navarre, Spain": {},
    "Valencia, Spain": {"wp": "Valencian Community"},
    "Valencian Community, Spain": {"alias_of": "Valencia, Spain", "the": True},
}
SPAIN_GROUP: dict[str, Any] = {
    "default_container": "Spain",
    "default_placetype": "autonomous community",
    "default_divs": ["municipalities", "comarcas"],
    "data": SPAIN_AUTONOMOUS_COMMUNITIES,
}

TAIWAN_COUNTIES = {
    "Changhua County, Taiwan": {},
    "Chiayi County, Taiwan": {},
    "Hsinchu County, Taiwan": {},
    "Hualien County, Taiwan": {},
    "Kinmen County, Taiwan": {"wp": "Kinmen"},
    "Lienchiang County, Taiwan": {"wp": "Matsu Islands"},
    "Miaoli County, Taiwan": {},
    "Nantou County, Taiwan": {},
    "Penghu County, Taiwan": {"wp": "Penghu"},
    "Pingtung County, Taiwan": {},
    "Taitung County, Taiwan": {},
    "Yilan County, Taiwan": {"wp": "%l, %c"},
    "Yunlin County, Taiwan": {},
}
TAIWAN_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Taiwan$", " County$"),
    "placename_to_key": make_placename_to_key(", Taiwan", " County"),
    "default_container": "Taiwan",
    "default_placetype": "county",
    "default_divs": ["districts", "townships"],
    "data": TAIWAN_COUNTIES,
}

THAILAND_PROVINCES: dict[str, Any] = {
    "Amnat Charoen Province, Thailand": {},
    "Ang Thong Province, Thailand": {},
    "Bueng Kan Province, Thailand": {},
    "Buriram Province, Thailand": {},
    "Chachoengsao Province, Thailand": {},
    "Chai Nat Province, Thailand": {},
    "Chaiyaphum Province, Thailand": {},
    "Chanthaburi Province, Thailand": {},
    "Chiang Mai Province, Thailand": {},
    "Chiang Rai Province, Thailand": {},
    "Chonburi Province, Thailand": {},
    "Chumphon Province, Thailand": {},
    "Kalasin Province, Thailand": {},
    "Kamphaeng Phet Province, Thailand": {},
    "Kanchanaburi Province, Thailand": {},
    "Khon Kaen Province, Thailand": {},
    "Krabi Province, Thailand": {},
    "Lampang Province, Thailand": {},
    "Lamphun Province, Thailand": {},
    "Loei Province, Thailand": {},
    "Lopburi Province, Thailand": {},
    "Mae Hong Son Province, Thailand": {},
    "Maha Sarakham Province, Thailand": {},
    "Mukdahan Province, Thailand": {},
    "Nakhon Nayok Province, Thailand": {},
    "Nakhon Pathom Province, Thailand": {},
    "Nakhon Phanom Province, Thailand": {},
    "Nakhon Ratchasima Province, Thailand": {},
    "Nakhon Sawon Province, Thailand": {},
    "Nakhon Si Thammarat Province, Thailand": {},
    "Nan Province, Thailand": {},
    "Narathiwat Province, Thailand": {},
    "Nong Bua Lamphu Province, Thailand": {},
    "Nong Khai Province, Thailand": {},
    "Nonthaburi Province, Thailand": {},
    "Pathum Thani Province, Thailand": {},
    "Pattani Province, Thailand": {},
    "Phang Nga Province, Thailand": {},
    "Phatthalung Province, Thailand": {},
    "Phayao Province, Thailand": {},
    "Phetchabun Province, Thailand": {},
    "Phetchaburi Province, Thailand": {},
    "Phichit Province, Thailand": {},
    "Phitsanulok Province, Thailand": {},
    "Phra Nakhon Si Ayutthaya Province, Thailand": {},
    "Phrae Province, Thailand": {},
    "Phuket Province, Thailand": {},
    "Prachinburi Province, Thailand": {},
    "Prachuap Khiri Khan Province, Thailand": {},
    "Ranong Province, Thailand": {},
    "Ratchaburi Province, Thailand": {},
    "Rayong Province, Thailand": {},
    "Roi Et Province, Thailand": {},
    "Sa Kaeo Province, Thailand": {},
    "Sakon Nakhon Province, Thailand": {},
    "Samut Prakan Province, Thailand": {},
    "Samut Sakhon Province, Thailand": {},
    "Samut Songkhram Province, Thailand": {},
    "Saraburi Province, Thailand": {},
    "Satun Province, Thailand": {},
    "Sing Buri Province, Thailand": {},
    "Sisaket Province, Thailand": {},
    "Songkhla Province, Thailand": {},
    "Sukhothai Province, Thailand": {},
    "Suphan Buri Province, Thailand": {},
    "Surat Thani Province, Thailand": {},
    "Surin Province, Thailand": {},
    "Tak Province, Thailand": {},
    "Trang Province, Thailand": {},
    "Trat Province, Thailand": {},
    "Ubon Ratchathani Province, Thailand": {},
    "Udon Thani Province, Thailand": {},
    "Uthai Thani Province, Thailand": {},
    "Uttaradit Province, Thailand": {},
    "Yala Province, Thailand": {},
    "Yasothon Province, Thailand": {},
}
THAILAND_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Thailand$", " Province$"),
    "placename_to_key": make_placename_to_key(", Thailand", " Province"),
    "default_container": "Thailand",
    "default_placetype": "province",
    "default_divs": "districts",
    "default_wp": "%e province",
    "data": THAILAND_PROVINCES,
}

TURKEY_PROVINCES = {
    "Adana Province, Turkey": {},
    "Adıyaman Province, Turkey": {},
    "Afyonkarahisar Province, Turkey": {},
    "Ağrı Province, Turkey": {},
    "Amasya Province, Turkey": {},
    "Ankara Province, Turkey": {},
    "Antalya Province, Turkey": {},
    "Artvin Province, Turkey": {},
    "Aydın Province, Turkey": {},
    "Balıkesir Province, Turkey": {},
    "Bilecik Province, Turkey": {},
    "Bingöl Province, Turkey": {},
    "Bitlis Province, Turkey": {},
    "Bolu Province, Turkey": {},
    "Burdur Province, Turkey": {},
    "Bursa Province, Turkey": {},
    "Çanakkale Province, Turkey": {},
    "Çankırı Province, Turkey": {},
    "Çorum Province, Turkey": {},
    "Denizli Province, Turkey": {},
    "Diyarbakır Province, Turkey": {},
    "Edirne Province, Turkey": {},
    "Elazığ Province, Turkey": {},
    "Elâzığ Province, Turkey": {
        "alias_of": "Elazığ Province, Turkey",
        "display": True,
    },
    "Erzincan Province, Turkey": {},
    "Erzurum Province, Turkey": {},
    "Eskişehir Province, Turkey": {},
    "Gaziantep Province, Turkey": {},
    "Giresun Province, Turkey": {},
    "Gümüşhane Province, Turkey": {},
    "Hakkâri Province, Turkey": {},
    "Hakkari Province, Turkey": {
        "alias_of": "Hakkâri Province, Turkey",
        "display": True,
    },
    "Hatay Province, Turkey": {},
    "Isparta Province, Turkey": {},
    "Mersin Province, Turkey": {},
    # "Istanbul Province, Turkey": {}, # intentionally omitted
    "İzmir Province, Turkey": {},
    "Izmir Province, Turkey": {
        "alias_of": "İzmir Province, Turkey",
        "display": True,
    },
    "Kars Province, Turkey": {},
    "Kastamonu Province, Turkey": {},
    "Kayseri Province, Turkey": {},
    "Kırklareli Province, Turkey": {},
    "Kırşehir Province, Turkey": {},
    "Kocaeli Province, Turkey": {},
    "Konya Province, Turkey": {},
    "Kütahya Province, Turkey": {},
    "Malatya Province, Turkey": {},
    "Manisa Province, Turkey": {},
    "Kahramanmaraş Province, Turkey": {},
    "Mardin Province, Turkey": {},
    "Muğla Province, Turkey": {},
    "Muş Province, Turkey": {},
    "Nevşehir Province, Turkey": {},
    "Niğde Province, Turkey": {},
    "Ordu Province, Turkey": {},
    "Rize Province, Turkey": {},
    "Sakarya Province, Turkey": {},
    "Samsun Province, Turkey": {},
    "Siirt Province, Turkey": {},
    "Sinop Province, Turkey": {},
    "Sivas Province, Turkey": {},
    "Tekirdağ Province, Turkey": {},
    "Tokat Province, Turkey": {},
    "Trabzon Province, Turkey": {},
    "Tunceli Province, Turkey": {},
    "Şanlıurfa Province, Turkey": {},
    "Uşak Province, Turkey": {},
    "Van Province, Turkey": {},
    "Yozgat Province, Turkey": {},
    "Zonguldak Province, Turkey": {},
    "Aksaray Province, Turkey": {},
    "Bayburt Province, Turkey": {},
    "Karaman Province, Turkey": {},
    "Kırıkkale Province, Turkey": {},
    "Batman Province, Turkey": {},
    "Şırnak Province, Turkey": {},
    "Bartın Province, Turkey": {},
    "Ardahan Province, Turkey": {},
    "Iğdır Province, Turkey": {},
    "Yalova Province, Turkey": {},
    "Karabük Province, Turkey": {},
    "Kilis Province, Turkey": {},
    "Osmaniye Province, Turkey": {},
    "Düzce Province, Turkey": {},
}
TURKEY_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Turkey$", " Province$"),
    "placename_to_key": make_placename_to_key(", Turkey", " Province"),
    "default_container": "Turkey",
    "default_placetype": "province",
    "default_divs": "districts",
    "data": TURKEY_PROVINCES,
}

UKRAINE_OBLASTS = {
    "Cherkasy Oblast, Ukraine": {},
    "Chernihiv Oblast, Ukraine": {},
    "Chernivtsi Oblast, Ukraine": {},
    "Dnipropetrovsk Oblast, Ukraine": {},
    "Donetsk Oblast, Ukraine": {},
    "Ivano-Frankivsk Oblast, Ukraine": {},
    "Kharkiv Oblast, Ukraine": {},
    "Kherson Oblast, Ukraine": {},
    "Khmelnytskyi Oblast, Ukraine": {},
    "Kirovohrad Oblast, Ukraine": {},
    "Kyiv Oblast, Ukraine": {},
    "Kiev Oblast, Ukraine": {
        "alias_of": "Kyiv Oblast, Ukraine",
        "display": True,
    },
    "Luhansk Oblast, Ukraine": {},
    "Lviv Oblast, Ukraine": {},
    "Mykolaiv Oblast, Ukraine": {},
    "Odesa Oblast, Ukraine": {},
    "Odessa Oblast, Ukraine": {
        "alias_of": "Odesa Oblast, Ukraine",
        "display": True,
    },
    "Poltava Oblast, Ukraine": {},
    "Rivne Oblast, Ukraine": {},
    "Sumy Oblast, Ukraine": {},
    "Ternopil Oblast, Ukraine": {},
    "Vinnytsia Oblast, Ukraine": {},
    "Volyn Oblast, Ukraine": {},
    "Zakarpattia Oblast, Ukraine": {},
    "Zaporizhzhia Oblast, Ukraine": {},
    "Zaporizhia Oblast, Ukraine": {
        "alias_of": "Zaporizhzhia Oblast, Ukraine",
        "display": True,
    },
    "Zhytomyr Oblast, Ukraine": {},
}
UKRAINE_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Ukraine$", " Oblast$"),
    "placename_to_key": make_placename_to_key(", Ukraine", " Oblast"),
    "default_container": "Ukraine",
    "default_placetype": "oblast",
    "default_divs": ["raions", "hromadas"],
    "data": UKRAINE_OBLASTS,
}

UNITED_KINGDOM_CONSTITUENT_COUNTRIES = {
    "England": {
        "divs": [
            "counties",
            "districts",
            {"type": "local government districts"},
            {
                "type": "local government districts with borough status",
                "cat_as": ["districts", "boroughs"],
            },
            {"type": "boroughs", "cat_as": ["districts", "boroughs"]},
            {"type": "civil parishes", "container_parent_type": False},
        ]
    },
    "Northern Ireland": {
        "placetype": ["constituent country", "province", "country"],
        "divs": ["counties", "districts"],
    },
    "Scotland": {
        "divs": [
            {"type": "council areas", "container_parent_type": False},
            "districts",
        ]
    },
    "Wales": {
        "divs": [
            "counties",
            {"type": "county boroughs", "container_parent_type": False},
            {"type": "communities", "container_parent_type": False},
            {"type": "Welsh communities", "cat_as": [{"type": "communities", "container_parent_type": False}]},
        ]
    },
}
UNITED_KINGDOM_GROUP: dict[str, Any] = {
    "placename_to_key": False,
    "default_container": "United Kingdom",
    "default_placetype": ["constituent country", "country"],
    "addl_divs": [
        "traditional counties",
        {"type": "historical counties", "cat_as": "traditional counties"},
    ],
    "default_no_container_cat": True,
    "data": UNITED_KINGDOM_CONSTITUENT_COUNTRIES,
}

ENGLAND_COUNTIES = {
    "Bedfordshire, England": {},
    "Berkshire, England": {},
    "Buckinghamshire, England": {},
    "Cambridgeshire, England": {},
    "Cheshire, England": {},
    "Cornwall, England": {},
    "Cumbria, England": {},
    "Derbyshire, England": {},
    "Devon, England": {},
    "Dorset, England": {},
    "County Durham, England": {},
    "East Sussex, England": {},
    "Essex, England": {},
    "Gloucestershire, England": {},
    "Greater London, England": {},
    "Greater Manchester, England": {},
    "Hampshire, England": {},
    "Herefordshire, England": {},
    "Hertfordshire, England": {},
    "Isle of Wight, England": {"the": True},
    "Kent, England": {},
    "Lancashire, England": {},
    "Leicestershire, England": {},
    "Lincolnshire, England": {},
    "Merseyside, England": {},
    "Norfolk, England": {},
    "Northamptonshire, England": {},
    "Northumberland, England": {},
    "North Yorkshire, England": {},
    "Nottinghamshire, England": {},
    "Oxfordshire, England": {},
    "Rutland, England": {},
    "Shropshire, England": {},
    "Somerset, England": {},
    "South Humberside, England": {},
    "South Yorkshire, England": {},
    "Staffordshire, England": {},
    "Suffolk, England": {},
    "Surrey, England": {},
    "Tyne and Wear, England": {},
    "Warwickshire, England": {},
    "West Midlands, England": {"the": True, "wp": "%l (county)"},
    "West Sussex, England": {},
    "West Yorkshire, England": {},
    "Wiltshire, England": {},
    "Worcestershire, England": {},
    "East Riding of Yorkshire, England": {"the": True},
}
ENGLAND_GROUP: dict[str, Any] = {
    "default_container": {"key": "England", "placetype": "constituent country"},
    "default_placetype": "county",
    "default_divs": [
        "districts",
        {"type": "local government districts", "cat_as": "districts"},
        {
            "type": "local government districts with borough status",
            "cat_as": ["districts", "boroughs"],
        },
        {"type": "boroughs", "cat_as": ["districts", "boroughs"]},
        "civil parishes",
    ],
    "data": ENGLAND_COUNTIES,
}


def make_irish_type_key_to_placename(container_pattern: str) -> Callable[[str], tuple[str, str]]:
    def key_to_placename(key: str) -> tuple[str, str]:
        full_placename = re.sub(container_pattern, "", key)
        # Remove Irish county/city prefix, e.g. "County Antrim" → "Antrim", "City of Derry" → "Derry"
        for prefix in ("County ", "City of "):
            if full_placename.startswith(prefix):
                elliptical_placename = full_placename[len(prefix) :]
                return full_placename, elliptical_placename
        return full_placename, full_placename

    return key_to_placename


def make_irish_type_placename_to_key(container_suffix: str) -> Callable[[str], str]:
    def placename_to_key(placename: str) -> str:
        # If it's not already prefixed, add "County " if not present
        if not placename.startswith(("County ", "City of ")):
            key = f"County {placename}{container_suffix}"
        else:
            key = f"{placename}{container_suffix}"
        return key

    return placename_to_key


NORTHERN_IRELAND_COUNTIES = {
    "County Antrim, Northern Ireland": {},
    "County Armagh, Northern Ireland": {},
    "City of Belfast, Northern Ireland": {"the": True, "is_city": True, "wp": "Belfast"},
    "County Down, Northern Ireland": {},
    "County Fermanagh, Northern Ireland": {},
    "County Londonderry, Northern Ireland": {},
    "City of Derry, Northern Ireland": {"the": True, "is_city": True, "wp": "Derry"},
    "County Tyrone, Northern Ireland": {},
}
NORTHERN_IRELAND_GROUP: dict[str, Any] = {
    "key_to_placename": make_irish_type_key_to_placename(", Northern Ireland$"),
    "placename_to_key": make_irish_type_placename_to_key(", Northern Ireland"),
    "default_container": {"key": "Northern Ireland", "placetype": "constituent country"},
    "default_placetype": "county",
    "data": NORTHERN_IRELAND_COUNTIES,
}

SCOTLAND_COUNCIL_AREAS = {
    "Aberdeenshire, Scotland": {},
    "Angus, Scotland": {"wp": "%l, %c"},
    "Argyll and Bute, Scotland": {},
    "City of Aberdeen, Scotland": {"the": True, "wp": "Aberdeen"},
    "Aberdeen": {"alias_of": "City of Aberdeen, Scotland"},
    "Aberdeen City": {"alias_of": "City of Aberdeen, Scotland"},
    "City of Dundee, Scotland": {"the": True, "wp": "Dundee"},
    "Dundee": {"alias_of": "City of Dundee, Scotland"},
    "Dundee City": {"alias_of": "City of Dundee, Scotland"},
    "City of Edinburgh, Scotland": {"the": True, "wp": "%l council area"},
    "Edinburgh": {"alias_of": "City of Edinburgh, Scotland"},
    "City of Glasgow, Scotland": {"the": True, "wp": "Glasgow"},
    "Glasgow": {"alias_of": "City of Glasgow, Scotland"},
    "Clackmannanshire, Scotland": {},
    "Dumfries and Galloway, Scotland": {},
    "East Ayrshire, Scotland": {},
    "East Dunbartonshire, Scotland": {},
    "East Lothian, Scotland": {},
    "East Renfrewshire, Scotland": {},
    "Falkirk, Scotland": {"wp": "%l council area"},
    "Fife, Scotland": {},
    "Highland, Scotland": {"wp": "%l council area"},
    "Inverclyde, Scotland": {},
    "Midlothian, Scotland": {},
    "Moray, Scotland": {},
    "North Ayrshire, Scotland": {},
    "North Lanarkshire, Scotland": {},
    "Orkney Islands, Scotland": {"the": True},
    "Perth and Kinross, Scotland": {},
    "Renfrewshire, Scotland": {},
    "Scottish Borders, Scotland": {"the": True},
    "Shetland Islands, Scotland": {"the": True},
    "South Ayrshire, Scotland": {},
    "South Lanarkshire, Scotland": {},
    "Stirling, Scotland": {"wp": "%l council area"},
    "West Dunbartonshire, Scotland": {},
    "West Lothian, Scotland": {},
    "Western Isles, Scotland": {"the": True, "wp": "Outer Hebrides"},
    "Na h-Eileanan Siar, Scotland": {"alias_of": "Western Isles, Scotland"},
}
SCOTLAND_GROUP: dict[str, Any] = {
    "default_container": {"key": "Scotland", "placetype": "constituent country"},
    "default_placetype": "council area",
    "data": SCOTLAND_COUNCIL_AREAS,
}

WALES_PRINCIPAL_AREAS = {
    "Blaenau Gwent, Wales": {},
    "Bridgend, Wales": {"wp": "%l County Borough"},
    "Caerphilly, Wales": {"wp": "%l County Borough"},
    "Carmarthenshire, Wales": {"placetype": "county"},
    "Ceredigion, Wales": {"placetype": "county"},
    "Conwy, Wales": {"wp": "%l County Borough"},
    "Denbighshire, Wales": {"placetype": "county"},
    "Flintshire, Wales": {"placetype": "county"},
    "Gwynedd, Wales": {"placetype": "county"},
    "Isle of Anglesey, Wales": {"the": True, "placetype": "county"},
    "Anglesey, Wales": {"alias_of": "Isle of Anglesey, Wales"},
    "Merthyr Tydfil, Wales": {"wp": "%l County Borough"},
    "Monmouthshire, Wales": {"placetype": "county"},
    "Neath Port Talbot, Wales": {},
    "Pembrokeshire, Wales": {"placetype": "county"},
    "Powys, Wales": {"placetype": "county"},
    "Rhondda Cynon Taf, Wales": {},
    "Torfaen, Wales": {},
    "Vale of Glamorgan, Wales": {"the": True},
    "Wrexham, Wales": {"wp": "%l County Borough"},
}
WALES_GROUP: dict[str, Any] = {
    "default_container": {"key": "Wales", "placetype": "constituent country"},
    "default_placetype": "county borough",
    "data": WALES_PRINCIPAL_AREAS,
}

UNITED_STATES_STATES = {
    "Alabama, USA": {},
    "Alaska, USA": {
        "divs": [
            {"type": "boroughs", "container_parent_type": "counties"},
            {"type": "borough seats", "container_parent_type": "county seats"},
        ]
    },
    "Arizona, USA": {},
    "Arkansas, USA": {},
    "California, USA": {},
    "Colorado, USA": {"divs": ["counties", "county seats", "municipalities"]},
    "Connecticut, USA": {"divs": ["counties", "county seats", "municipalities"]},
    "Delaware, USA": {},
    "Florida, USA": {},
    "Georgia, USA": {"wp": "%l (U.S. state)"},
    "Hawaii, USA": {"addl_parents": ["Polynesia"]},
    "Idaho, USA": {},
    "Illinois, USA": {},
    "Indiana, USA": {},
    "Iowa, USA": {},
    "Kansas, USA": {},
    "Kentucky, USA": {},
    "Louisiana, USA": {
        "divs": [
            {"type": "parishes", "container_parent_type": "counties"},
            {"type": "parish seats", "container_parent_type": "county seats"},
        ]
    },
    "Maine, USA": {},
    "Maryland, USA": {},
    "Massachusetts, USA": {},
    "Michigan, USA": {},
    "Minnesota, USA": {},
    "Mississippi, USA": {},
    "Missouri, USA": {},
    "Montana, USA": {},
    "Nebraska, USA": {},
    "Nevada, USA": {},
    "New Hampshire, USA": {},
    "New Jersey, USA": {
        "divs": [
            "counties",
            "county seats",
            {"type": "boroughs", "prep": "in"},
        ]
    },
    "New Mexico, USA": {},
    "New York, USA": {"wp": "%l (state)"},
    "North Carolina, USA": {},
    "North Dakota, USA": {},
    "Ohio, USA": {},
    "Oklahoma, USA": {},
    "Oregon, USA": {},
    "Pennsylvania, USA": {
        "divs": [
            "counties",
            "county seats",
            {"type": "boroughs", "prep": "in"},
        ]
    },
    "Rhode Island, USA": {},
    "South Carolina, USA": {},
    "South Dakota, USA": {},
    "Tennessee, USA": {},
    "Texas, USA": {},
    "Utah, USA": {},
    "Vermont, USA": {},
    "Virginia, USA": {},
    "Washington, USA": {"wp": "%l (state)"},
    "West Virginia, USA": {},
    "Wisconsin, USA": {},
    "Wyoming, USA": {},
}
UNITED_STATES_GROUP: dict[str, Any] = {
    "placename_to_key": make_placename_to_key(", USA"),
    "default_container": "United States",
    "default_placetype": "state",
    "default_divs": ["counties", "county seats"],
    "addl_divs": [
        {"type": "census-designated places", "prep": "in"},
        {"type": "unincorporated communities", "prep": "in"},
    ],
    "data": UNITED_STATES_STATES,
}

VIETNAM_PROVINCES = {
    # Northeast region
    "Bắc Giang Province, Vietnam": {},
    "Bắc Kạn Province, Vietnam": {},
    "Cao Bằng Province, Vietnam": {},
    "Hà Giang Province, Vietnam": {},
    "Lạng Sơn Province, Vietnam": {},
    "Phú Thọ Province, Vietnam": {},
    "Quảng Ninh Province, Vietnam": {},
    "Thái Nguyên Province, Vietnam": {},
    "Tuyên Quang Province, Vietnam": {},
    # Northwest region
    "Lào Cai Province, Vietnam": {},
    "Yên Bái Province, Vietnam": {},
    "Điện Biên Province, Vietnam": {},
    "Hoà Bình Province, Vietnam": {},
    "Hòa Bình Province, Vietnam": {"alias_of": "Hoà Bình Province, Vietnam", "display": True},
    "Lai Châu Province, Vietnam": {},
    "Sơn La Province, Vietnam": {},
    # Red River Delta region
    "Bắc Ninh Province, Vietnam": {},
    "Hà Nam Province, Vietnam": {},
    "Hải Dương Province, Vietnam": {},
    "Hưng Yên Province, Vietnam": {},
    "Nam Định Province, Vietnam": {},
    "Ninh Bình Province, Vietnam": {},
    "Thái Bình Province, Vietnam": {},
    "Vĩnh Phúc Province, Vietnam": {},
    # North Central Coast region
    "Hà Tĩnh Province, Vietnam": {},
    "Nghệ An Province, Vietnam": {},
    "Quảng Bình Province, Vietnam": {},
    "Quảng Trị Province, Vietnam": {},
    "Thanh Hoá Province, Vietnam": {},
    "Thanh Hóa Province, Vietnam": {"alias_of": "Thanh Hoá Province, Vietnam", "display": True},
    # Central Highlands region
    "Đắk Lắk Province, Vietnam": {},
    "Đăk Nông Province, Vietnam": {},
    "Gia Lai Province, Vietnam": {},
    "Kon Tum Province, Vietnam": {},
    "Lâm Đồng Province, Vietnam": {},
    # South Central Coast region
    "Bình Định Province, Vietnam": {},
    "Bình Thuận Province, Vietnam": {},
    "Khánh Hoà Province, Vietnam": {},
    "Khánh Hòa Province, Vietnam": {"alias_of": "Khánh Hoà Province, Vietnam", "display": True},
    "Ninh Thuận Province, Vietnam": {},
    "Phú Yên Province, Vietnam": {},
    "Quảng Nam Province, Vietnam": {},
    "Quảng Ngãi Province, Vietnam": {},
    # Southeast region
    "Bà Rịa–Vũng Tàu Province, Vietnam": {},
    "Bình Dương Province, Vietnam": {},
    "Bình Phước Province, Vietnam": {},
    "Đồng Nai Province, Vietnam": {},
    "Tây Ninh Province, Vietnam": {},
    # Mekong Delta region
    "An Giang Province, Vietnam": {},
    "Bạc Liêu Province, Vietnam": {},
    "Bến Tre Province, Vietnam": {},
    "Cà Mau Province, Vietnam": {},
    "Đồng Tháp Province, Vietnam": {},
    "Hậu Giang Province, Vietnam": {},
    "Kiên Giang Province, Vietnam": {},
    "Long An Province, Vietnam": {},
    "Sóc Trăng Province, Vietnam": {},
    "Tiền Giang Province, Vietnam": {},
    "Trà Vinh Province, Vietnam": {},
    "Vĩnh Long Province, Vietnam": {},
}
VIETNAM_GROUP: dict[str, Any] = {
    "key_to_placename": make_key_to_placename(", Vietnam$", " Province$"),
    "placename_to_key": make_placename_to_key(", Vietnam", " Province"),
    "default_container": "Vietnam",
    "default_placetype": "province",
    "default_wp": "%e province",
    "data": VIETNAM_PROVINCES,
}

AUSTRALIA_CITIES = {
    "Adelaide": {"container": "South Australia"},
    "Brisbane": {"container": "Queensland"},
    "Canberra": {"container": {"key": "Australian Capital Territory, Australia", "placetype": "territory"}},
    "Melbourne": {"container": "Victoria"},
    "Newcastle, New South Wales": {"container": "New South Wales", "wp": "%l, %c"},
    "Newcastle": {"alias_of": "Newcastle, New South Wales"},
    "Perth": {"container": "Western Australia"},
    "Sydney": {"container": "New South Wales"},
}
AUSTRALIA_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Australia", "state"),
    "default_placetype": "city",
    "data": AUSTRALIA_CITIES,
}

BRAZIL_CITIES = {
    "São Paulo": {"container": "São Paulo"},
    "Sao Paulo": {"alias_of": "São Paulo", "display": True},
    "Rio de Janeiro": {"container": "Rio de Janeiro"},
    "Belo Horizonte": {"container": "Minas Gerais"},
    "Recife": {"container": "Pernambuco"},
    "Porto Alegre": {"container": "Rio Grande do Sul"},
    "Brasília": {"container": "Distrito Federal"},
    "Brasilia": {"alias_of": "Brasília", "display": True},
    "Fortaleza": {"container": "Ceará"},
    "Salvador": {"container": "Bahia", "wp": "%l, %c", "commonscat": "%l (%c)"},
    "Curitiba": {"container": "Paraná"},
    "Campinas": {"container": "São Paulo"},
    "Goiânia": {"container": "Goiás"},
    "Goiania": {"alias_of": "Goiânia", "display": True},
    "Manaus": {"container": "Amazonas"},
    "Belém": {"container": "Pará"},
    "Belem": {"alias_of": "Belém", "display": True},
    "Vitória": {"container": "Espírito Santo", "wp": "%l, %c"},
    "Vitoria": {"alias_of": "Vitória", "display": True},
    "Santos": {"container": "São Paulo", "wp": "%l, %c"},
    "São Luís": {"container": "Maranhão", "wp": "%l, %c"},
    "Sao Luis": {"alias_of": "São Luís", "display": True},
    "Natal": {"container": "Rio Grande do Norte", "wp": "%l, %c"},
    "Florianópolis": {"container": "Santa Catarina"},
    "Florianopolis": {"alias_of": "Florianópolis", "display": True},
    "Maceió": {"container": "Alagoas"},
    "Maceio": {"alias_of": "Maceió", "display": True},
    "João Pessoa": {"container": "Paraíba", "wp": "%l, %c"},
    "Joao Pessoa": {"alias_of": "João Pessoa", "display": True},
    "São José dos Campos": {"container": "São Paulo"},
    "Sao Jose dos Campos": {"alias_of": "São José dos Campos", "display": True},
    "Londrina": {"container": "Paraná"},
    "Teresina": {"container": "Piauí"},
}
BRAZIL_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Brazil", "state"),
    "default_placetype": "city",
    "data": BRAZIL_CITIES,
}

CANADA_CITIES = {
    "Toronto": {"container": "Ontario"},
    "Montreal": {"container": "Quebec"},
    "Vancouver": {"container": "British Columbia"},
    "Calgary": {"container": "Alberta"},
    "Edmonton": {"container": "Alberta"},
    "Ottawa": {"container": "Ontario"},
    "Quebec City": {"container": "Quebec"},
    "Winnipeg": {"container": "Manitoba"},
    "Hamilton": {"container": "Ontario", "wp": "%l, %c"},
    "Kitchener": {"container": "Ontario", "wp": "%l, %c"},
}
CANADA_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Canada", "province"),
    "default_placetype": "city",
    "data": CANADA_CITIES,
}

FRANCE_CITIES = {
    "Paris": {"container": "Île-de-France"},
    "Lyon": {"container": "Auvergne-Rhône-Alpes"},
    "Lyons": {"alias_of": "Lyon", "display": True},
    "Marseille": {"container": "Provence-Alpes-Côte d'Azur"},
    "Marseilles": {"alias_of": "Marseille", "display": True},
    "Lille": {"container": "Hauts-de-France"},
    "Bordeaux": {"container": "Nouvelle-Aquitaine"},
    "Toulouse": {"container": "Occitania"},
    "Nice": {"container": "Provence-Alpes-Côte d'Azur"},
    "Nantes": {"container": "Pays de la Loire"},
    "Strasbourg": {"container": "Grand Est"},
    "Rennes": {"container": "Brittany"},
}
FRANCE_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", France", "region"),
    "default_placetype": "city",
    "data": FRANCE_CITIES,
}

GERMANY_CITIES = {
    "Cologne": {"container": "North Rhine-Westphalia"},
    "Köln": {"alias_of": "Cologne", "display": True},
    "Düsseldorf": {"container": "North Rhine-Westphalia"},
    "Dusseldorf": {"alias_of": "Düsseldorf", "display": True},
    "Dortmund": {"container": "North Rhine-Westphalia"},
    "Essen": {"container": "North Rhine-Westphalia"},
    "Duisberg": {"container": "North Rhine-Westphalia"},
    "Berlin": {},
    "Frankfurt": {"container": "Hesse"},
    "Frankfurt am Main": {"alias_of": "Frankfurt"},
    "Hamburg": {},
    "Munich": {"container": "Bavaria"},
    "Stuttgart": {"container": "Baden-Württemberg"},
    "Mannheim": {"container": "Baden-Württemberg"},
    "Nuremberg": {"container": "Bavaria"},
    "Hanover": {"container": "Lower Saxony"},
    "Bielefeld": {"container": "North Rhine-Westphalia"},
    "Leipzig": {"container": "Saxony"},
    "Aachen": {"container": "North Rhine-Westphalia"},
    "Aix-la-Chapelle": {"alias_of": "Aachen"},
    "Bremen": {},
}
GERMANY_CITIES_GROUP: dict[str, Any] = {
    "default_container": "Germany",
    "canonicalize_key_container": make_canonicalize_key_container(", Germany", "state"),
    "default_placetype": "city",
    "data": GERMANY_CITIES,
}

INDIA_CITIES = {
    "Delhi": {"container": {"key": "Delhi, India", "placetype": "union territory"}},
    "Mumbai": {"container": "Maharashtra"},
    "Kolkata": {"container": "West Bengal"},
    "Bangalore": {"container": "Karnataka", "wp": "Bengaluru"},
    "Bengaluru": {"alias_of": "Bangalore"},
    "Chennai": {"container": "Tamil Nadu"},
    "Hyderabad": {"container": "Telangana"},
    "Ahmedabad": {"container": "Gujarat"},
    "Pune": {"container": "Maharashtra"},
    "Surat": {"container": "Gujarat"},
    "Lucknow": {"container": "Uttar Pradesh"},
    "Jaipur": {"container": "Rajasthan"},
    "Kanpur": {"container": "Uttar Pradesh"},
    "Indore": {"container": "Madhya Pradesh"},
    "Nagpur": {"container": "Maharashtra"},
    "Patna": {"container": "Bihar"},
    "Varanasi": {"container": "Uttar Pradesh"},
    "Kozhikode": {"container": "Kerala"},
    "Thiruvananthapuram": {"container": "Kerala"},
    "Agra": {"container": "Uttar Pradesh"},
    "Bhopal": {"container": "Madhya Pradesh"},
    "Coimbatore": {"container": "Tamil Nadu"},
    "Allahabad": {"container": "Uttar Pradesh", "wp": "Prayagraj"},
    "Prayagraj": {"alias_of": "Allahabad"},
    "Kochi": {"container": "Kerala"},
    "Ludhiana": {"container": "Punjab"},
    "Vadodara": {"container": "Gujarat"},
    "Chandigarh": {"container": {"key": "Chandigarh, India", "placetype": "union territory"}},
    "Madurai": {"container": "Tamil Nadu"},
    "Meerut": {"container": "Uttar Pradesh"},
    "Visakhapatnam": {"container": "Andhra Pradesh"},
    "Jamshedpur": {"container": "Jharkhand"},
    "Malappuram": {"container": "Kerala"},
    "Nashik": {"container": "Maharashtra"},
    "Asansol": {"container": "West Bengal"},
    "Aligarh": {"container": "Uttar Pradesh"},
    "Ranchi": {"container": "Jharkhand"},
    "Thrissur": {"container": "Kerala"},
    "Kollam": {"container": "Kerala"},
    "Jabalpur": {"container": "Madhya Pradesh"},
    "Dhanbad": {"container": "Jharkhand"},
    "Jodhpur": {"container": "Rajasthan"},
    "Aurangabad": {"container": "Maharashtra"},
    "Chhatrapati Sambhajinagar": {"alias_of": "Aurangabad"},
    "Rajkot": {"container": "Gujarat"},
    "Gwalior": {"container": "Madhya Pradesh"},
    "Raipur": {"container": "Chhattisgarh"},
    "Gorakhpur": {"container": "Uttar Pradesh"},
    "Kannur": {"container": "Kerala"},
    "Bareilly": {"container": "Uttar Pradesh"},
    "Guwahati": {"container": "Assam"},
    "Moradabad": {"container": "Uttar Pradesh"},
    "Amritsar": {"container": "Punjab"},
    "Mysore": {"container": "Karnataka"},
    "Bhilai": {"container": "Chhattisgarh"},
    "Durg-Bhilainagar": {"alias_of": "Bhilai"},
    "Durg-Bhilai": {"alias_of": "Bhilai"},
    "Durg": {"alias_of": "Bhilai"},
    "Bhilainagar": {"alias_of": "Bhilai"},
    "Vijayawada": {"container": "Andhra Pradesh"},
    "Srinagar": {"container": {"key": "Jammu and Kashmir, India", "placetype": "union territory"}},
    "Salem": {"container": "Tamil Nadu", "wp": "%l, %c"},
    "Kota": {"container": "Rajasthan"},
    "Jalandhar": {"container": "Punjab"},
    "Saharanpur": {"container": "Uttar Pradesh"},
    "Dehradun": {"container": "Uttarakhand"},
    "Tiruchirappalli": {"container": "Tamil Nadu"},
    "Bhubaneswar": {"container": "Odisha"},
    "Jammu": {"container": {"key": "Jammu and Kashmir, India", "placetype": "union territory"}},
    "Solapur": {"container": "Maharashtra"},
    "Hubli-Dharwad": {"container": "Karnataka", "wp": "Hubli–Dharwad"},
    "Hubli": {"alias_of": "Hubli-Dharwad"},
    "Dharwad": {"alias_of": "Hubli-Dharwad"},
    "Puducherry": {"container": {"key": "Puducherry, India", "placetype": "union territory"}},
    "Pondicherry": {"alias_of": "Puducherry", "display": True},
    "Ghaziabad": {"container": "Uttar Pradesh"},
    "Faridabad": {"container": "Haryana"},
    "Thane": {"container": "Maharashtra"},
    "Kalyan-Dombivli": {"container": "Maharashtra"},
    "Kalyan-Dombivali": {"alias_of": "Kalyan-Dombivli", "display": True},
    "Kalyan": {"alias_of": "Kalyan-Dombivli"},
    "Dombivli": {"alias_of": "Kalyan-Dombivli"},
    "Dombivali": {"alias_of": "Kalyan-Dombivli"},
    "Vasai-Virar": {"container": "Maharashtra"},
    "Vasai": {"alias_of": "Vasai-Virar"},
    "Virar": {"alias_of": "Vasai-Virar"},
    "Navi Mumbai": {"container": "Maharashtra"},
    "Howrah": {"container": "West Bengal"},
    "Pimpri-Chinchwad": {"container": "Maharashtra"},
    "Pimpri Chinchwad": {"alias_of": "Pimpri-Chinchwad", "display": True},
}
INDIA_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", India", "state"),
    "default_placetype": "city",
    "data": INDIA_CITIES,
}

INDONESIA_CITIES = {
    "Jakarta": {
        "container": "Special Capital Region of Jakarta",
        "divs": [{"type": "subdistricts", "container_parent_type": False}],
    },
    "Surabaya": {"container": "East Java"},
    "Bekasi": {"container": "West Java"},
    "Bandung": {"container": "West Java"},
    "Medan": {"container": "North Sumatra"},
    "Depok": {"container": "West Java"},
    "Tangerang": {"container": "Banten"},
    "Palembang": {"container": "South Sumatra"},
    "Semarang": {"container": "Central Java"},
    "Makassar": {"container": "South Sulawesi"},
    "South Tangerang": {"container": "Banten"},
    "Batam": {"container": "Riau Islands"},
    "Bogor": {"container": "West Java"},
    "Pekanbaru": {"container": "Riau"},
    "Bandar Lampung": {"container": "Lampung"},
    "Padang": {"container": "West Sumatra"},
    "Samarinda": {"container": "East Kalimantan"},
    "Malang": {"container": "East Java"},
    "Yogyakarta": {"container": "Special Region of Yogyakarta"},
    "Denpasar": {"container": "Bali"},
    "Cirebon": {"container": "West Java"},
    "Surakarta": {"container": "Central Java"},
    "Banjarmasin": {"container": "South Kalimantan"},
    "Tasikmalaya": {"container": "West Java"},
}
INDONESIA_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Indonesia", "province"),
    "default_placetype": "city",
    "data": INDONESIA_CITIES,
}

ITALY_CITIES = {
    "Milan": {"container": "Lombardy"},
    "Naples": {"container": "Campania"},
    "Rome": {"container": "Lazio"},
    "Turin": {"container": "Piedmont"},
    "Venice": {"container": "Veneto"},
    "Florence": {"container": "Tuscany"},
    "Bari": {"container": "Apulia"},
    "Palermo": {"container": "Sicily"},
    "Catania": {"container": "Sicily"},
    "Brescia": {"container": "Lombardy"},
    "Genoa": {"container": "Liguria"},
}
ITALY_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Italy", "region"),
    "default_placetype": "city",
    "data": ITALY_CITIES,
}

JAPAN_CITIES = {
    "Tokyo": {
        "keydesc": "[[Tokyo]] Metropolis, the [[capital city]] and a [[prefecture]] of [[Japan]] (which is a country in [[Asia]])",
        "placetype": ["city", "prefecture"],
        "divs": [
            {"type": "special wards", "container_parent_type": False},
            {"type": "cities", "prep": "in"},
        ],
    },
    "Yokohama": {"container": "Kanagawa"},
    "Osaka": {"container": "Osaka"},
    "Nagoya": {"container": "Aichi"},
    "Sapporo": {"container": "Hokkaido"},
    "Fukuoka": {"container": "Fukuoka"},
    "Kobe": {"container": "Hyōgo"},
    "Kyoto": {"container": "Kyoto"},
    "Kawasaki": {"container": "Kanagawa", "wp": "%l, Kanagawa"},
    "Saitama": {"container": "Saitama", "wp": "%l (city)", "commonscat": "%l, %c"},
    "Hiroshima": {"container": "Hiroshima"},
    "Sendai": {"container": "Miyagi"},
    "Kitakyushu": {"container": "Fukuoka"},
    "Chiba": {"container": "Chiba", "wp": "%l (city)", "commonscat": "%l, %c"},
    "Sakai": {"container": "Osaka"},
    "Niigata": {"container": "Niigata", "wp": "%l (city)", "commonscat": "%l, %c"},
    "Hamamatsu": {"container": "Shizuoka"},
    "Shizuoka": {"container": "Shizuoka", "wp": "%l (city)", "commonscat": "%l, %c"},
    "Sagamihara": {"container": "Kanagawa"},
    "Okayama": {"container": "Okayama"},
    "Kumamoto": {"container": "Kumamoto"},
    "Kagoshima": {"container": "Kagoshima"},
    "Utsunomiya": {"container": "Tochigi"},
}
JAPAN_CITIES_GROUP: dict[str, Any] = {
    "default_container": "Japan",
    "canonicalize_key_container": make_canonicalize_key_container(" Prefecture, Japan", "prefecture"),
    "default_placetype": "city",
    "data": JAPAN_CITIES,
}

MEXICO_CITIES = {
    "Mexico City": {},
    "Monterrey": {"container": "Nuevo León"},
    "Guadalajara": {"container": "Jalisco"},
    "Puebla": {"container": "Puebla", "wp": "%l (city)"},
    "Toluca": {"container": "State of Mexico"},
    "Tijuana": {"container": "Baja California"},
    "León, Guanajuato": {"container": "Guanajuato", "wp": "%l, %c"},
    "León": {"alias_of": "León, Guanajuato"},
    "Leon": {"alias_of": "León, Guanajuato", "display": True},
    "Querétaro": {"container": "Querétaro", "wp": "%l (city)"},
    "Queretaro": {"alias_of": "Querétaro", "display": True},
    "Ciudad Juárez": {"container": "Chihuahua"},
    "Juárez": {"alias_of": "Ciudad Juárez"},
    "Juarez": {"alias_of": "Ciudad Juárez", "display": "Juárez"},
    "Torreón": {"container": "Coahuila"},
    "Torreon": {"alias_of": "Torreón", "display": True},
    "Mérida, Yucatán": {"container": "Yucatán", "wp": "%l, %c"},
    "Mérida": {"alias_of": "Mérida, Yucatán"},
    "Merida": {"alias_of": "Mérida, Yucatán", "display": True},
    "San Luis Potosí": {"container": "San Luis Potosí", "wp": "%l (city)"},
    "San Luis Potosi": {"alias_of": "San Luis Potosí", "display": True},
    "Aguascalientes": {"container": "Aguascalientes", "wp": "%l (city)"},
    "Mexicali": {"container": "Baja California"},
}
MEXICO_CITIES_GROUP: dict[str, Any] = {
    "default_container": "Mexico",
    "canonicalize_key_container": make_canonicalize_key_container(", Mexico", "state"),
    "default_placetype": "city",
    "data": MEXICO_CITIES,
}

NIGERIA_CITIES = {
    "Lagos": {"container": "Lagos"},
    "Kano": {"container": "Kano", "wp": "%l (city)"},
    "Ibadan": {"container": "Oyo"},
    "Abuja": {"container": {"key": "Federal Capital Territory, Nigeria", "placetype": "federal territory"}},
    "Port Harcourt": {"container": "Rivers"},
    "Kaduna": {"container": "Kaduna"},
    "Benin City": {"container": "Edo"},
    "Aba": {"container": "Abia", "wp": "%l, Nigeria"},
    "Onitsha": {"container": "Anambra"},
    "Maiduguri": {"container": "Borno"},
    "Ilorin": {"container": "Kwara"},
    "Sokoto": {"container": "Sokoto", "wp": "%l (city)"},
    "Jos": {"container": "Plateau"},
    "Zaria": {"container": "Kaduna"},
    "Enugu": {"container": "Enugu", "wp": "%l (city)"},
}
NIGERIA_CITIES_GROUP: dict[str, Any] = {
    "default_container": "Nigeria",
    "canonicalize_key_container": make_canonicalize_key_container(" State, Nigeria", "state"),
    "default_placetype": "city",
    "data": NIGERIA_CITIES,
}

PAKISTAN_CITIES = {
    "Karachi": {"container": "Sindh"},
    "Lahore": {"container": "Punjab"},
    "Rawalpindi": {"container": "Punjab"},
    "Islamabad": {"container": {"key": "Islamabad Capital Territory, Pakistan", "placetype": "federal territory"}},
    "Faisalabad": {"container": "Punjab"},
    "Gujranwala": {"container": "Punjab"},
    "Hyderabad, Pakistan": {"container": "Sindh", "wp": "%l, %c"},
    "Hyderabad": {"alias_of": "Hyderabad, Pakistan"},
    "Multan": {"container": "Punjab"},
    "Peshawar": {"container": "Khyber Pakhtunkhwa"},
    "Quetta": {"container": "Balochistan"},
    "Sargodha": {"container": "Punjab"},
    "Sialkot": {"container": "Punjab"},
}
PAKISTAN_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Pakistan", "province"),
    "default_placetype": "city",
    "data": PAKISTAN_CITIES,
}

PHILIPPINES_CITIES = {
    "Quezon City": {"container": {"key": "Metro Manila, Philippines", "placetype": "region"}},
    "Quezon": {"alias_of": "Quezon City"},
    "Manila": {"container": {"key": "Metro Manila, Philippines", "placetype": "region"}},
    "Davao City": {"container": "Davao del Sur"},
    "Davao": {"alias_of": "Davao City"},
    "Caloocan": {"container": {"key": "Metro Manila, Philippines", "placetype": "region"}},
    "Zamboanga City": {"container": "Zamboanga del Sur"},
    "Zamboanga": {"alias_of": "Zamboanga City"},
    "Cebu City": {"container": "Cebu"},
    "Cebu": {"alias_of": "Cebu City"},
    "Antipolo": {"container": "Rizal"},
    "Cagayan de Oro": {"container": "Misamis Oriental"},
    "Dasmariñas": {"container": "Cavite"},
    "Dasmarinas": {"alias_of": "Dasmariñas", "display": True},
    "General Santos": {"container": "South Cotabato"},
    "San Jose del Monte": {"container": "Bulacan"},
    "Bacolod": {"container": "Negros Occidental"},
    "Calamba": {"container": "Laguna", "wp": "%l, %c"},
    "Angeles": {"container": "Pampanga", "wp": "Angeles City"},
    "Angeles City": {"alias_of": "Angeles"},
    "Iloilo City": {"container": "Iloilo"},
    "Iloilo": {"alias_of": "Iloilo City"},
}
PHILIPPINES_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Philippines", "province"),
    "default_placetype": "city",
    "data": PHILIPPINES_CITIES,
}

RUSSIA_CITIES = {
    "Moscow": {},
    "Saint Petersburg": {},
    "Novosibirsk": {"container": "Novosibirsk Oblast"},
    "Yekaterinburg": {"container": "Sverdlovsk Oblast"},
    "Nizhny Novgorod": {"container": "Nizhny Novgorod Oblast"},
    "Kazan": {"container": {"key": "Tatarstan, Russia", "placetype": "republic"}},
    "Chelyabinsk": {"container": "Chelyabinsk Oblast"},
    "Rostov-on-Don": {"container": "Rostov Oblast"},
    "Rostov-na-Donu": {"alias_of": "Rostov-on-Don", "display": True},
    "Krasnodar": {"container": {"key": "Krasnodar Krai, Russia", "placetype": "krai"}},
    "Samara": {"container": "Samara Oblast"},
    "Krasnoyarsk": {"container": {"key": "Krasnoyarsk Krai, Russia", "placetype": "krai"}},
    "Ufa": {"container": {"key": "Bashkortostan, Russia", "placetype": "republic"}},
    "Saratov": {"container": "Saratov Oblast"},
    "Omsk": {"container": "Omsk Oblast"},
    "Voronezh": {"container": "Voronezh Oblast"},
    "Volgograd": {"container": "Volgograd Oblast"},
    "Perm": {"container": {"key": "Perm Krai, Russia", "placetype": "krai"}, "wp": "%l, Russia"},
}
RUSSIA_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Russia", "oblast"),
    "default_container": "Russia",
    "default_placetype": "city",
    "data": RUSSIA_CITIES,
}

SAUDI_ARABIA_CITIES = {
    "Riyadh": {"container": "Riyadh"},
    "Jeddah": {"container": "Mecca"},
    "Jedda": {"alias_of": "Jeddah", "display": True},
    "Jiddah": {"alias_of": "Jeddah", "display": True},
    "Jidda": {"alias_of": "Jeddah", "display": True},
    "Dammam": {"container": "Eastern"},
    "Mecca": {"container": "Mecca"},
    "Makkah": {"alias_of": "Mecca", "display": True},
    "Medina": {"container": "Medina"},
    "Hofuf": {"container": "Eastern"},
    "Khamis Mushait": {"container": "Aseer"},
    "Khamis Mushayt": {"alias_of": "Khamis Mushait", "display": True},
}
SAUDI_ARABIA_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(" Province, Saudi Arabia", "province"),
    "default_placetype": "city",
    "data": SAUDI_ARABIA_CITIES,
}

SOUTH_KOREA_CITIES: dict[str, Any] = {
    "Seoul": {},
    "Busan": {},
    "Incheon": {},
    "Daegu": {},
    "Daejeon": {},
    "Gwangju": {},
    "Ulsan": {},
}
SOUTH_KOREA_CITIES_GROUP: dict[str, Any] = {
    "default_container": "South Korea",
    "canonicalize_key_container": make_canonicalize_key_container(" County, South Korea", "province"),
    "default_placetype": "city",
    "data": SOUTH_KOREA_CITIES,
}

SPAIN_CITIES = {
    "Madrid": {"container": "Community of Madrid"},
    "Barcelona": {"container": "Catalonia"},
    "Valencia": {"container": "Valencia"},
    "Seville": {"container": "Andalusia"},
    "Bilbao": {"container": "Basque Country"},
}
SPAIN_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", Spain", "autonomous community"),
    "default_placetype": "city",
    "data": SPAIN_CITIES,
}

TAIWAN_CITIES = {
    "New Taipei City": {},
    "New Taipei": {"alias_of": "New Taipei City", "display": True},
    "Taichung": {},
    "Kaohsiung": {"wp": "%l, Taiwan"},
    "Taipei": {},
    "Taoyuan": {},
    "Tainan": {},
    "Chiayi": {"placetype": "city"},
    "Hsinchu": {"placetype": "city"},
    "Keelung": {"placetype": "city"},
}
TAIWAN_CITIES_GROUP: dict[str, Any] = {
    "placename_to_key": False,  # don't add ", Taiwan" to make the key
    "canonicalize_key_container": make_canonicalize_key_container(", Taiwan", "county"),
    "default_container": "Taiwan",
    "default_placetype": ["special municipality", "municipality", "city"],
    "default_is_city": True,
    "default_divs": ["districts"],
    "data": TAIWAN_CITIES,
}


UNITED_KINGDOM_CITIES = {
    "London": {"container": "Greater London"},
    "Manchester": {"container": "Greater Manchester"},
    "Birmingham": {"container": "West Midlands"},
    "Liverpool": {"container": "Merseyside"},
    "Glasgow": {"container": {"key": "City of Glasgow, Scotland", "placetype": "council area"}},
    "Leeds": {"container": "West Yorkshire"},
    "Newcastle upon Tyne": {"container": "Tyne and Wear"},
    "Newcastle": {"alias_of": "Newcastle upon Tyne"},
    "Bristol": {"container": {"key": "England", "placetype": "constituent country"}},
    "Cardiff": {"container": {"key": "Wales", "placetype": "constituent country"}},
    "Portsmouth": {"container": "Hampshire"},
    "Edinburgh": {"container": {"key": "City of Edinburgh, Scotland", "placetype": "council area"}},
    "Swansea": {"container": {"key": "Wales", "placetype": "constituent country"}},
    "Newport": {"container": {"key": "Wales", "placetype": "constituent country"}, "wp": "Newport, Wales"},
}
UNITED_KINGDOM_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(", England", "county"),
    "default_placetype": "city",
    "data": UNITED_KINGDOM_CITIES,
}

UNITED_STATES_CITIES = {
    "New York City": {
        "container": "New York",
        "wp": "%l",
        "divs": [{"type": "boroughs", "container_parent_type": False}],
    },
    "New York": {"alias_of": "New York City"},
    "Newark": {"container": "New Jersey"},
    "Los Angeles": {"container": "California", "wp": "%l"},
    "Long Beach": {"container": "California"},
    "Riverside": {"container": "California"},
    "Chicago": {"container": "Illinois", "wp": "%l"},
    "Washington, D.C.": {"wp": "%l"},
    "Washington, DC": {"alias_of": "Washington, D.C.", "display": True},
    "Washington D.C.": {"alias_of": "Washington, D.C.", "display": True},
    "Washington DC": {"alias_of": "Washington, D.C.", "display": True},
    "Washington": {"alias_of": "Washington, D.C."},
    "Baltimore": {"container": "Maryland", "wp": "%l"},
    "San Jose, California": {"container": "California"},
    "San Jose": {"alias_of": "San Jose, California"},
    "San Francisco": {"container": "California", "wp": "%l"},
    "Oakland": {"container": "California"},
    "Boston": {"container": "Massachusetts", "wp": "%l"},
    "Providence": {"container": "Rhode Island"},
    "Dallas": {"container": "Texas", "wp": "%l"},
    "Fort Worth": {"container": "Texas"},
    "Philadelphia": {"container": "Pennsylvania", "wp": "%l"},
    "Houston": {"container": "Texas", "wp": "%l"},
    "Miami": {"container": "Florida", "wp": "%l"},
    "Atlanta": {"container": "Georgia", "wp": "%l"},
    "Detroit": {"container": "Michigan", "wp": "%l"},
    "Phoenix": {"container": "Arizona", "wp": "%l"},
    "Mesa": {"container": "Arizona"},
    "Seattle": {"container": "Washington", "wp": "%l"},
    "Orlando": {"container": "Florida"},
    "Minneapolis": {"container": "Minnesota", "wp": "%l"},
    "Cleveland": {"container": "Ohio", "wp": "%l"},
    "Denver": {"container": "Colorado", "wp": "%l"},
    "San Diego": {"container": "California", "wp": "%l"},
    "Portland": {"container": "Oregon"},
    "Tampa": {"container": "Florida"},
    "St. Louis": {"container": "Missouri", "wp": "%l"},
    "Saint Louis": {"alias_of": "St. Louis", "display": True},
    "Charlotte": {"container": "North Carolina"},
    "Sacramento": {"container": "California"},
    "Pittsburgh": {"container": "Pennsylvania", "wp": "%l"},
    "Salt Lake City": {"container": "Utah", "wp": "%l"},
    "San Antonio": {"container": "Texas", "wp": "%l"},
    "Columbus": {"container": "Ohio"},
    "Kansas City": {"container": "Missouri", "wp": "%l metropolitan area"},
    "Indianapolis": {"container": "Indiana", "wp": "%l"},
    "Las Vegas": {"container": "Nevada", "wp": "%l"},
    "Cincinnati": {"container": "Ohio", "wp": "%l"},
    "Austin": {"container": "Texas"},
    "Milwaukee": {"container": "Wisconsin", "wp": "%l"},
    "Raleigh": {"container": "North Carolina"},
    "Nashville": {"container": "Tennessee"},
    "Virginia Beach": {"container": "Virginia"},
    "Norfolk": {"container": "Virginia"},
    "Greensboro": {"container": "North Carolina"},
    "Winston-Salem": {"container": "North Carolina"},
    "Jacksonville": {"container": "Florida"},
    "New Orleans": {"container": "Louisiana", "wp": "%l"},
    "Louisville": {"container": "Kentucky"},
    "Greenville": {"container": "South Carolina"},
    "Hartford": {"container": "Connecticut"},
    "Oklahoma City": {"container": "Oklahoma", "wp": "%l"},
    "Grand Rapids": {"container": "Michigan"},
    "Memphis": {"container": "Tennessee"},
    "Birmingham, Alabama": {"container": "Alabama"},
    "Birmingham": {"alias_of": "Birmingham, Alabama"},
    "Fresno": {"container": "California"},
    "Richmond": {"container": "Virginia"},
    "Harrisburg": {"container": "Pennsylvania"},
    "Buffalo": {"container": "New York"},
    "El Paso": {"container": "Texas"},
    "Albuquerque": {"container": "New Mexico"},
    "Tucson": {"container": "Arizona"},
    "Colorado Springs": {"container": "Colorado"},
    "Omaha": {"container": "Nebraska"},
    "Tulsa": {"container": "Oklahoma"},
}
UNITED_STATES_CITIES_GROUP: dict[str, Any] = {
    "default_container": "United States",
    "canonicalize_key_container": make_canonicalize_key_container(", USA", "state"),
    "default_placetype": "city",
    "default_wp": "%l, %c",
    "data": UNITED_STATES_CITIES,
}

NEW_YORK_BOROUGHS = {
    "Bronx": {"the": True, "wp": "The Bronx"},
    "Brooklyn": {},
    "Manhattan": {},
    "Queens": {},
    "Staten Island": {},
}
NEW_YORK_BOROUGHS_GROUP: dict[str, Any] = {
    "default_container": {"key": "New York City", "placetype": "city"},
    "default_placetype": "borough",
    "default_is_city": True,
    "data": NEW_YORK_BOROUGHS,
}

VIETNAM_CITIES = {
    "Ho Chi Minh City": {},
    "Saigon": {"alias_of": "Ho Chi Minh City"},
    "Hanoi": {},
    "Da Nang": {},
    "Danang": {"alias_of": "Da Nang", "display": True},
    "Haiphong": {},
    "Hai Phong": {"alias_of": "Haiphong", "display": True},
    "Bien Hoa": {"placetype": "city", "container": "Đồng Nai", "wp": "Biên Hòa"},
    "Biên Hòa": {"alias_of": "Bien Hoa", "display": True},
    "Biên Hoà": {"alias_of": "Bien Hoa", "display": True},
    "Can Tho": {"wp": "Cần Thơ"},
    "Cần Thơ": {"alias_of": "Can Tho", "display": True},
    "Hue": {"wp": "Huế"},
    "Huế": {"alias_of": "Hue", "display": True},
}
VIETNAM_CITIES_GROUP: dict[str, Any] = {
    "placename_to_key": False,  # don't add ", Vietnam" to make the key
    "default_container": "Vietnam",
    "canonicalize_key_container": make_canonicalize_key_container(" Province, Vietnam", "province"),
    "default_placetype": ["municipality", "city"],
    "default_is_city": True,
    "data": VIETNAM_CITIES,
}

MISC_CITIES = {
    # Africa
    "Algiers": {"container": "Algeria"},
    "Oran": {"container": "Algeria"},
    "Luanda": {"container": "Angola"},
    "Benguela": {"container": "Angola"},
    "Cotonou": {"container": "Benin"},
    "Ouagadougou": {"container": "Burkina Faso"},
    "Bobo-Dioulasso": {"container": "Burkina Faso"},
    "Bujumbura": {"container": "Burundi"},
    "Yaoundé": {"container": "Cameroon"},
    "Yaounde": {"alias_of": "Yaoundé", "display": True},
    "Douala": {"container": "Cameroon"},
    "Bangui": {"container": "Central African Republic"},
    "N'Djamena": {"container": "Chad"},
    "Ndjamena": {"alias_of": "N'Djamena", "display": True},
    "Kinshasa": {"container": "Democratic Republic of the Congo"},
    "Lubumbashi": {"container": "Democratic Republic of the Congo"},
    "Mbuji-Mayi": {"container": "Democratic Republic of the Congo"},
    "Kananga": {"container": "Democratic Republic of the Congo"},
    "Kisangani": {"container": "Democratic Republic of the Congo"},
    "Bukavu": {"container": "Democratic Republic of the Congo"},
    "Goma": {"container": "Democratic Republic of the Congo"},
    "Tshikapa": {"container": "Democratic Republic of the Congo"},
    "Cairo": {"container": "Egypt"},
    "Alexandria": {"container": "Egypt"},
    "Giza": {"container": "Egypt"},
    "Shubra El Kheima": {"container": "Egypt"},
    "Asmara": {"container": "Eritrea"},
    "Asmera": {"alias_of": "Asmara", "display": True},
    "Addis Ababa": {"container": "Ethiopia"},
    "Banjul": {"container": "Gambia"},
    "Accra": {"container": "Ghana"},
    "Kumasi": {"container": "Ghana"},
    "Conakry": {"container": "Guinea"},
    "Abidjan": {"container": "Ivory Coast"},
    "Nairobi": {"container": "Kenya"},
    "Mombasa": {"container": "Kenya"},
    "Monrovia": {"container": "Liberia"},
    "Tripoli": {"container": "Libya", "wp": "%l, %c"},
    "Antananarivo": {"container": "Madagascar"},
    "Lilongwe": {"container": "Malawi"},
    "Bamako": {"container": "Mali"},
    "Nouakchott": {"container": "Mauritania"},
    "Casablanca": {"container": {"key": "Casablanca-Settat, Morocco", "placetype": "region"}},
    "Rabat": {"container": {"key": "Rabat-Sale-Kenitra, Morocco", "placetype": "region"}},
    "Tangier": {"container": {"key": "Tangier-Tetouan-Al Hoceima, Morocco", "placetype": "region"}},
    "Tanger": {"alias_of": "Tangier", "display": True},
    "Tangiers": {"alias_of": "Tangier", "display": True},
    "Fez": {"container": {"key": "Fez-Meknes, Morocco", "placetype": "region"}, "wp": "%l, Morocco"},
    "Fes": {"alias_of": "Fez", "display": True},
    "Fès": {"alias_of": "Fez", "display": True},
    "Agadir": {"container": {"key": "Souss-Massa, Morocco", "placetype": "region"}},
    "Marrakesh": {"container": {"key": "Marrakesh-Safi, Morocco", "placetype": "region"}},
    "Marrakech": {"alias_of": "Marrakesh", "display": True},
    "Maputo": {"container": "Mozambique"},
    "Niamey": {"container": "Niger"},
    "Brazzaville": {"container": "Republic of the Congo"},
    "Pointe-Noire": {"container": "Republic of the Congo"},
    "Kigali": {"container": "Rwanda"},
    "Dakar": {"container": "Senegal"},
    "Touba": {"container": "Senegal"},
    "Freetown": {"container": "Sierra Leone"},
    "Mogadishu": {"container": "Somalia"},
    "Johannesburg": {"container": {"key": "Gauteng, South Africa", "placetype": "province"}},
    "Cape Town": {"container": {"key": "Western Cape, South Africa", "placetype": "province"}},
    "Durban": {"container": {"key": "KwaZulu-Natal, South Africa", "placetype": "province"}},
    "Pretoria": {"container": {"key": "Gauteng, South Africa", "placetype": "province"}},
    "Port Elizabeth": {"container": {"key": "Eastern Cape, South Africa", "placetype": "province"}, "wp": "Gqeberha"},
    "Gqeberha": {"alias_of": "Port Elizabeth"},
    "Khartoum": {"container": "Sudan"},
    "Dar es Salaam": {"container": "Tanzania"},
    "Mwanza": {"container": "Tanzania"},
    "Mwanza City": {"alias_of": "Mwanza", "display": True},
    "Arusha": {"container": "Tanzania"},
    "Zanzibar": {"container": "Tanzania"},
    "Lomé": {"container": "Togo"},
    "Lome": {"alias_of": "Lomé", "display": True},
    "Tunis": {"container": "Tunisia"},
    "Sousse": {"container": "Tunisia"},
    "Soussa": {"alias_of": "Sousse", "display": True},
    "Kampala": {"container": "Uganda"},
    "Lusaka": {"container": "Zambia"},
    "Harare": {"container": "Zimbabwe"},
    # Asia
    "Kabul": {"container": "Afghanistan"},
    "Baku": {"container": "Azerbaijan"},
    "Manama": {"container": "Bahrain"},
    "Dhaka": {"container": {"key": "Dhaka Division, Bangladesh", "placetype": "division"}},
    "Dacca": {"alias_of": "Dhaka", "display": True},
    "Chittagong": {"container": {"key": "Chittagong Division, Bangladesh", "placetype": "division"}},
    "Gazipur": {"container": {"key": "Dhaka Division, Bangladesh", "placetype": "division"}},
    "Khulna": {"container": {"key": "Khulna Division, Bangladesh", "placetype": "division"}},
    "Phnom Penh": {"container": "Cambodia"},
    "Tehran": {"container": {"key": "Tehran Province, Iran", "placetype": "province"}},
    "Teheran": {"alias_of": "Tehran", "display": True},
    "Mashhad": {"container": {"key": "Razavi Khorasan Province, Iran", "placetype": "province"}},
    "Mashad": {"alias_of": "Mashhad", "display": True},
    "Meshhed": {"alias_of": "Mashhad", "display": True},
    "Meshed": {"alias_of": "Mashhad", "display": True},
    "Isfahan": {"container": {"key": "Isfahan Province, Iran", "placetype": "province"}},
    "Esfahan": {"alias_of": "Isfahan", "display": True},
    "Tabriz": {"container": {"key": "East Azerbaijan Province, Iran", "placetype": "province"}},
    "Shiraz": {"container": {"key": "Fars Province, Iran", "placetype": "province"}},
    "Ahvaz": {"container": {"key": "Khuzestan Province, Iran", "placetype": "province"}},
    "Qom": {"container": {"key": "Qom Province, Iran", "placetype": "province"}},
    "Kermanshah": {"container": {"key": "Kermanshah Province, Iran", "placetype": "province"}},
    "Baghdad": {"container": "Iraq"},
    "Basra": {"container": "Iraq"},
    "Mosul": {"container": "Iraq"},
    "Erbil": {"container": "Iraq"},
    "Kirkuk": {"container": "Iraq"},
    "Najaf": {"container": "Iraq"},
    "Tel Aviv": {"container": "Israel"},
    "Jerusalem": {"container": {"key": "Asia", "placetype": "continent"}},
    "Amman": {"container": "Jordan"},
    "Irbid": {"container": "Jordan"},
    "Almaty": {"container": "Kazakhstan"},
    "Alma-Ata": {"alias_of": "Almaty"},
    "Astana": {"container": "Kazakhstan"},
    "Shymkent": {"container": "Kazakhstan"},
    "Kuwait City": {"container": "Kuwait"},
    "Bishkek": {"container": "Kyrgyzstan"},
    "Beirut": {"container": "Lebanon"},
    "Kuala Lumpur": {"container": "Malaysia"},
    "George Town, Malaysia": {"container": {"key": "Penang, Malaysia", "placetype": "state"}, "wp": "%l, %c"},
    "George Town": {"alias_of": "George Town, Malaysia"},
    "Ulaanbaatar": {"container": "Mongolia"},
    "Ulan Bator": {"alias_of": "Ulaanbaatar", "display": True},
    "Yangon": {"container": "Myanmar"},
    "Rangoon": {"alias_of": "Yangon", "display": True},
    "Mandalay": {"container": "Myanmar"},
    "Kathmandu": {"container": "Nepal"},
    "Pyongyang": {"container": "North Korea"},
    "Muscat": {"container": "Oman"},
    "Gaza": {"container": "Palestine", "wp": "Gaza City"},
    "Gaza City": {"alias_of": "Gaza"},
    "Doha": {"container": "Qatar"},
    "Colombo": {"container": "Sri Lanka"},
    "Damascus": {"container": "Syria"},
    "Aleppo": {"container": "Syria"},
    "Dushanbe": {"container": "Tajikistan"},
    "Bangkok": {"container": "Thailand"},
    "Chiang Mai": {"container": {"key": "Chiang Mai Province, Thailand", "placetype": "province"}},
    "Chonburi": {"container": {"key": "Chonburi Province, Thailand", "placetype": "province"}},
    "Istanbul": {"placetype": ["city", "province"], "divs": ["districts"], "container": "Turkey"},
    "İstanbul": {"alias_of": "Istanbul", "display": True},
    "Ankara": {"container": {"key": "Ankara Province, Turkey", "placetype": "province"}},
    "Izmir": {"container": {"key": "İzmir Province, Turkey", "placetype": "province"}, "wp": "İzmir"},
    "İzmir": {"alias_of": "Izmir", "display": True},
    "Bursa": {"container": {"key": "Bursa Province, Turkey", "placetype": "province"}},
    "Adana": {"container": {"key": "Adana Province, Turkey", "placetype": "province"}},
    "Gaziantep": {"container": {"key": "Gaziantep Province, Turkey", "placetype": "province"}},
    "Antalya": {"container": {"key": "Antalya Province, Turkey", "placetype": "province"}},
    "Konya": {"container": {"key": "Konya Province, Turkey", "placetype": "province"}},
    "Diyarbakır": {"container": {"key": "Diyarbakır Province, Turkey", "placetype": "province"}},
    "Diyarbakir": {"alias_of": "Diyarbakır"},
    "Mersin": {"container": {"key": "Mersin Province, Turkey", "placetype": "province"}},
    "Ashgabat": {"container": "Turkmenistan"},
    "Dubai": {"container": "United Arab Emirates"},
    "Abu Dhabi": {"container": "United Arab Emirates"},
    "Sharjah": {"container": "United Arab Emirates"},
    "Tashkent": {"container": "Uzbekistan"},
    "Sanaa": {"container": "Yemen"},
    "Sana'a": {"alias_of": "Sanaa", "display": True},
    "Aden": {"container": "Yemen"},
    # Europe, Caucasus, etc.
    "Yerevan": {"container": "Armenia"},
    "Vienna": {"container": "Austria"},
    "Minsk": {"container": "Belarus"},
    "Brussels": {"container": "Belgium"},
    "Antwerp": {"container": "Belgium"},
    "Sofia": {"container": "Bulgaria"},
    "Zagreb": {"container": "Croatia"},
    "Prague": {"container": "Czech Republic"},
    "Brno": {"container": "Czech Republic"},
    "Olomouc": {"container": "Czech Republic"},
    "Copenhagen": {"container": "Denmark"},
    "Helsinki": {"container": {"key": "Uusimaa, Finland", "placetype": "region"}},
    "Tbilisi": {"container": "Georgia"},
    "Athens": {"container": "Greece"},
    "Thessaloniki": {"container": "Greece"},
    "Budapest": {"container": "Hungary"},
    "Dublin": {"container": {"key": "County Dublin, Ireland", "placetype": "county"}},
    "Riga": {"container": "Latvia"},
    "Amsterdam": {"container": {"key": "North Holland, Netherlands", "placetype": "province"}},
    "Rotterdam": {"container": {"key": "South Holland, Netherlands", "placetype": "province"}},
    "The Hague": {"container": {"key": "South Holland, Netherlands", "placetype": "province"}},
    "Auckland": {"container": {"key": "Auckland, New Zealand", "placetype": "region"}},
    "Oslo": {"container": {"key": "Oslo, Norway", "placetype": "county"}},
    "Warsaw": {"container": {"key": "Masovian Voivodeship, Poland", "placetype": "voivodeship"}},
    "Katowice": {"container": {"key": "Silesian Voivodeship, Poland", "placetype": "voivodeship"}},
    "Krakow": {"container": {"key": "Lesser Poland Voivodeship, Poland", "placetype": "voivodeship"}, "wp": "Kraków"},
    "Kraków": {"alias_of": "Krakow", "display": True},
    "Cracow": {"alias_of": "Krakow", "display": True},
    "Gdańsk": {"container": {"key": "Pomeranian Voivodeship, Poland", "placetype": "voivodeship"}},
    "Gdansk": {"alias_of": "Gdańsk", "display": True},
    "Poznań": {"container": {"key": "Greater Poland Voivodeship, Poland", "placetype": "voivodeship"}},
    "Poznan": {"alias_of": "Poznań", "display": True},
    "Lodz": {"container": {"key": "Lodz Voivodeship, Poland", "placetype": "voivodeship"}, "wp": "Łódź"},
    "Łódź": {"alias_of": "Lodz", "display": True},
    "Lisbon": {"container": {"key": "Lisbon District, Portugal", "placetype": "district"}},
    "Porto": {"container": {"key": "Porto District, Portugal", "placetype": "district"}},
    "Oporto": {"alias_of": "Porto", "display": True},
    "Bucharest": {"container": "Romania"},
    "Belgrade": {"container": "Serbia"},
    "Stockholm": {"container": "Sweden"},
    "Zurich": {"container": "Switzerland"},
    "Zürich": {"alias_of": "Zurich", "display": True},
    "Kyiv": {"container": "Ukraine"},
    "Kiev": {"alias_of": "Kyiv"},
    "Kharkiv": {"container": {"key": "Kharkiv Oblast, Ukraine", "placetype": "oblast"}},
    "Odessa": {"container": {"key": "Odesa Oblast, Ukraine", "placetype": "oblast"}, "wp": "Odesa"},
    "Odesa": {"alias_of": "Odessa"},
    # Americas
    "Buenos Aires": {"container": "Argentina"},
    "Córdoba, Argentina": {"container": "Argentina", "wp": "%l, %c"},
    "Córdoba": {"alias_of": "Córdoba, Argentina"},
    "Cordoba": {"alias_of": "Córdoba, Argentina", "display": "Córdoba"},
    "Rosario": {"container": "Argentina", "wp": "%l, Santa Fe"},
    "Mendoza": {"container": "Argentina", "wp": "%l, %c"},
    "San Miguel de Tucumán": {"container": "Argentina"},
    "Tucumán": {"alias_of": "San Miguel de Tucumán"},
    "Tucuman": {"alias_of": "San Miguel de Tucumán", "display": "Tucumán"},
    "Santa Cruz de la Sierra": {"container": "Bolivia"},
    "Santa Cruz": {"alias_of": "Santa Cruz de la Sierra"},
    "La Paz": {"container": "Bolivia"},
    "El Alto": {"container": "Bolivia"},
    "Cochabamba": {"container": "Bolivia"},
    "Santiago": {"container": "Chile"},
    "Valparaíso": {"container": "Chile"},
    "Valparaiso": {"alias_of": "Valparaíso"},
    "Bogotá": {"container": "Colombia"},
    "Bogota": {"alias_of": "Bogotá", "display": True},
    "Medellín": {"container": "Colombia"},
    "Medellin": {"alias_of": "Medellín", "display": True},
    "Cali": {"container": "Colombia"},
    "Barranquilla": {"container": "Colombia"},
    "Bucaramanga": {"container": "Colombia"},
    "Cartagena, Colombia": {"container": "Colombia", "wp": "%l, %c"},
    "Cartagena": {"alias_of": "Cartagena, Colombia"},
    "Cúcuta": {"container": "Colombia"},
    "Cucuta": {"alias_of": "Cúcuta", "display": True},
    "San José, Costa Rica": {"container": "Costa Rica", "wp": "%l, %c"},
    "San José": {"alias_of": "San José, Costa Rica"},
    "San Jose": {"alias_of": "San José, Costa Rica"},
    "Havana": {"container": "Cuba"},
    "Santo Domingo": {"container": "Dominican Republic"},
    "Guayaquil": {"container": "Ecuador"},
    "Quito": {"container": "Ecuador"},
    "San Salvador": {"container": "El Salvador"},
    "Guatemala City": {"container": "Guatemala"},
    "Port-au-Prince": {"container": "Haiti"},
    "San Pedro Sula": {"container": "Honduras"},
    "Tegucigalpa": {"container": "Honduras"},
    "Managua": {"container": "Nicaragua"},
    "Panama City": {"container": "Panama"},
    "Asunción": {"container": "Paraguay"},
    "Lima": {"container": "Peru"},
    "Arequipa": {"container": "Peru"},
    "San Juan": {"container": {"key": "Puerto Rico", "placetype": "commonwealth"}, "wp": "%l, %c"},
    "Montevideo": {"container": "Uruguay"},
    "Caracas": {"container": "Venezuela"},
    "Maracaibo": {"container": "Venezuela"},
    "Valencia, Venezuela": {"container": "Venezuela", "wp": "%l, %c"},
    "Valencia": {"alias_of": "Valencia, Venezuela"},
    "Maracay": {"container": "Venezuela"},
    "Barquisimeto": {"container": "Venezuela"},
}
MISC_CITIES_GROUP: dict[str, Any] = {
    "canonicalize_key_container": make_canonicalize_key_container(None, "country"),
    "default_placetype": "city",
    "data": MISC_CITIES,
}

LOCATIONS = (
    CONTINENTS_GROUP,
    COUNTRIES_GROUP,
    COUNTRY_LIKE_ENTITIES_GROUP,
    FORMER_COUNTRIES_GROUP,
    AUSTRALIA_GROUP,
    AUSTRIA_GROUP,
    BANGLADESH_GROUP,
    BRAZIL_GROUP,
    CANADA_GROUP,
    CHINA_GROUP,
    CHINA_PREFECTURE_LEVEL_CITIES_GROUP,
    CHINA_PREFECTURE_LEVEL_CITIES_GROUP_2,
    FINLAND_GROUP,
    FRANCE_GROUP,
    FRANCE_DEPARTMENTS_GROUP,
    GERMANY_GROUP,
    GREECE_GROUP,
    INDIA_GROUP,
    INDONESIA_GROUP,
    IRAN_GROUP,
    IRELAND_GROUP,
    ITALY_GROUP,
    JAPAN_GROUP,
    LAOS_GROUP,
    LEBANON_GROUP,
    MALAYSIA_GROUP,
    MALTA_GROUP,
    MEXICO_GROUP,
    MOLDOVA_GROUP,
    MOROCCO_GROUP,
    NETHERLANDS_GROUP,
    NEW_ZEALAND_GROUP,
    NIGERIA_GROUP,
    NORTH_KOREA_GROUP,
    NORWAY_GROUP,
    PAKISTAN_GROUP,
    PHILIPPINES_GROUP,
    POLAND_GROUP,
    PORTUGAL_GROUP,
    ROMANIA_GROUP,
    RUSSIA_GROUP,
    SAUDI_ARABIA_GROUP,
    SOUTH_AFRICA_GROUP,
    SOUTH_KOREA_GROUP,
    SPAIN_GROUP,
    TAIWAN_GROUP,
    THAILAND_GROUP,
    TURKEY_GROUP,
    UKRAINE_GROUP,
    UNITED_KINGDOM_GROUP,
    UNITED_STATES_GROUP,
    ENGLAND_GROUP,
    NORTHERN_IRELAND_GROUP,
    SCOTLAND_GROUP,
    WALES_GROUP,
    VIETNAM_GROUP,
    AUSTRALIA_CITIES_GROUP,
    BRAZIL_CITIES_GROUP,
    CANADA_CITIES_GROUP,
    FRANCE_CITIES_GROUP,
    GERMANY_CITIES_GROUP,
    INDIA_CITIES_GROUP,
    INDONESIA_CITIES_GROUP,
    ITALY_CITIES_GROUP,
    JAPAN_CITIES_GROUP,
    MEXICO_CITIES_GROUP,
    NIGERIA_CITIES_GROUP,
    PAKISTAN_CITIES_GROUP,
    PHILIPPINES_CITIES_GROUP,
    RUSSIA_CITIES_GROUP,
    SAUDI_ARABIA_CITIES_GROUP,
    SOUTH_KOREA_CITIES_GROUP,
    SPAIN_CITIES_GROUP,
    TAIWAN_CITIES_GROUP,
    UNITED_KINGDOM_CITIES_GROUP,
    UNITED_STATES_CITIES_GROUP,
    NEW_YORK_BOROUGHS_GROUP,
    VIETNAM_CITIES_GROUP,
    MISC_CITIES_GROUP,
)


def list_or_element_contains(list_or_element: Any, item: Any) -> bool:
    if isinstance(list_or_element, list):
        return item in list_or_element
    return list_or_element == item


def key_to_placename(group: dict[str, Any], key: str) -> tuple[str, str]:
    ktp = group.get("key_to_placename")
    if ktp is False:
        return key, key
    if ktp:
        full_placename, elliptical_placename = ktp(key)
        return full_placename, elliptical_placename
    key = key.split(",")[0]
    return key, key


def placename_to_key(group: dict[str, Any], placename: str) -> str:
    ptk = group.get("placename_to_key")
    if ptk is False:
        return placename
    if ptk:
        return ptk(placename)
    if group.get("default_placetype") == "city":
        return placename
    defcon = group.get("default_container")
    if not defcon:
        return placename
    if isinstance(defcon, str):
        return f"{placename}, {defcon}"
    if isinstance(defcon, dict) and defcon.get("placetype") in {"country", "constituent country"}:
        return f"{placename}, {defcon['key']}"
    return placename


def initialize_spec(group: dict[str, Any], key: str, spec: dict[str, Any]) -> None:
    if spec.get("initialized"):
        return
    container = spec.get("container")
    containers = None
    container_from_default = False
    if not container:
        container = group.get("default_container")
        container_from_default = True
    if container:
        if isinstance(container, str) or (isinstance(container, dict) and container.get("key")):
            container = [container]
        containers = []
        for cont in container:
            if isinstance(cont, str):
                if group.get("canonicalize_key_container") and not container_from_default:
                    cont = group["canonicalize_key_container"](cont)
                else:
                    cont = {"key": cont, "placetype": "country"}
            containers.append(cont)
    spec["containers"] = containers
    spec.pop("container", None)

    def value_with_default(val, default_val):
        return default_val if val is None else val

    def set_or_default(prop: str):
        spec[prop] = value_with_default(spec.get(prop), group.get(f"default_{prop}"))

    set_or_default("placetype")
    set_or_default("divs")
    spec["addl_divs"] = group.get("addl_divs")
    for prop in [
        "keydesc",
        "fulldesc",
        "addl_parents",
        "overriding_bare_label_parents",
        "bare_category_parent_type",
        "wp",
        "wpcat",
        "commonscat",
        "british_spelling",
        "the",
        "no_container_cat",
        "no_container_parent",
        "no_generic_place_cat",
        "no_check_holonym_mismatch",
        "no_auto_augment_container",
        "no_include_container_in_desc",
        "is_city",
        "is_former_place",
    ]:
        set_or_default(prop)
    spec["is_city"] = value_with_default(spec.get("is_city"), group.get("default_placetype") == "city")
    spec["initialized"] = True


def find_matching_key_in_group(
    group: dict[str, Any], placetypes: Any, key: str, alias_resolution: str
) -> tuple[str, dict[str, Any]] | None:
    spec = group["data"].get(key)
    if not spec:
        return None

    def check_correct_placetype(placetype: Any) -> bool:
        if isinstance(placetype, list):
            return any(list_or_element_contains(placetypes, pt) for pt in placetype)
        return list_or_element_contains(placetypes, placetype)

    if spec.get("alias_of"):
        resolved_key = spec["alias_of"]
        resolved_spec = group["data"].get(resolved_key)
        if alias_resolution in {"none", "display"}:
            placetype = (
                spec.get("placetype")
                or (resolved_spec and resolved_spec.get("placetype"))
                or group.get("default_placetype")
            )
            if not check_correct_placetype(placetype):
                return None
            if alias_resolution == "display":
                if spec.get("display") is True:
                    key = resolved_key
                elif spec.get("display"):
                    key = spec["display"]
            return key, spec
        key = resolved_key
        spec = resolved_spec
    placetype = spec.get("placetype") or group.get("default_placetype")
    if not check_correct_placetype(placetype):
        return None
    initialize_spec(group, key, spec)
    return key, spec


def find_matching_placename_in_group(
    group: dict[str, Any], placetypes: Any, placename: str, alias_resolution: str
) -> tuple[str, dict[str, Any]] | None:
    key = placename_to_key(group, placename)
    return find_matching_key_in_group(group, placetypes, key, alias_resolution)


def find_canonical_key(key: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
    found_locations: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for group in LOCATIONS:
        spec = group["data"].get(key)
        if not spec:
            continue
        if spec.get("alias_of"):
            continue
        found_locations.append((group, spec))
    if not found_locations:
        return None
    group, spec = found_locations[0]
    initialize_spec(group, key, spec)
    return group, spec


def iterate_matching_location(data: dict[str, Any]) -> Iterator[tuple[dict[str, Any], str, dict[str, Any]]]:
    i = 0
    n = len(LOCATIONS)
    while i < n:
        group = LOCATIONS[i]
        i += 1
        if data.get("placename"):
            result = find_matching_placename_in_group(
                group, data["placetypes"], data["placename"], data["alias_resolution"]
            )
        else:
            result = find_matching_key_in_group(group, data["placetypes"], data["key"], data["alias_resolution"])
        if result:
            key, spec = result
            yield group, key, spec


def get_matching_location(data: dict[str, Any]) -> tuple[dict[str, Any], str, dict[str, Any]] | None:
    all_found: list[tuple[dict[str, Any], str, dict[str, Any]]] = list(iterate_matching_location(data))
    return all_found[0] if all_found else None


def iterate_containers(group: dict[str, Any], key: str, spec: dict[str, Any]) -> Iterator[list[dict[str, Any]]]:
    keys_seen = {key: True}
    iterations = 0
    last_iteration_containers = [{"group": group, "key": key, "spec": spec}]
    while True:
        iterations += 1
        next_iteration_containers: list[dict[str, Any]] = []
        for location in last_iteration_containers:
            containers = location["spec"].get("containers")
            if containers:
                for container in containers:
                    result = get_matching_location(
                        {
                            "placetypes": container["placetype"],
                            "key": container["key"],
                        }
                    )
                    if result:
                        container_group, container_key, container_spec = result
                        if not keys_seen.get(container_key):
                            next_iteration_containers.append(
                                {
                                    "group": container_group,
                                    "key": container_key,
                                    "spec": container_spec,
                                }
                            )
                            keys_seen[container_key] = True
        if not next_iteration_containers:
            break
        last_iteration_containers = next_iteration_containers
        yield next_iteration_containers


def construct_linked_placename(spec: dict[str, Any], placename: str, display_form: str | None = None) -> str:
    if display_form and placename != display_form:
        linked_placename = f"[[{placename}|{display_form}]]"
    else:
        linked_placename = f"[[{placename}]]"
    if spec.get("the"):
        linked_placename = f"the {linked_placename}"
    return linked_placename
