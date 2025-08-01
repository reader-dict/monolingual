"""
Source: https://en.wiktionary.org/w/index.php?title=Module:place&oldid=85658430
"""

import re
from collections import defaultdict
from typing import Any

from ....user_functions import capitalize
from .placetypes import remove_links_and_html, resolve_placename_display_aliases, resolve_placetype_aliases

ALL_FORM_OF_DIRECTIVES: dict[str, dict[str, Any]] = {
    "former name of": {"text": "+", "type_prefix": "FORMER_NAME_OF"},
    "fmr of": {"alias_of": "former name of"},
    "ancient name of": {"text": "+", "type_prefix": "FORMER_NAME_OF"},
    "official name of": {"text": "+", "type_prefix": "OFFICIAL_NAME_OF"},
    "former official name of": {"text": "+", "type_prefix": "FORMER_OFFICIAL_NAME_OF"},
    "long form of": {"text": "+", "type_prefix": "LONG_FORM_OF"},
    "former long form of": {"text": "+", "type_prefix": "FORMER_LONG_FORM_OF"},
    "nickname for": {"text": "+", "type_prefix": "NICKNAME_FOR"},
    "official nickname for": {"text": "+", "type_prefix": "OFFICIAL_NICKNAME_FOR"},
    "former nickname for": {"text": "+", "type_prefix": "FORMER_NICKNAME_FOR"},
    "derogatory name for": {
        "text": "derogatory name for",
        "type_prefix": "DEROGATORY_NAME_FOR",
    },
    "synonym of": {"text": "+"},
    "syn of": {"alias_of": "synonym of"},
    "abbreviation of": {
        "text": "abbreviation of",
        "type_prefix": "ABBREVIATION_OF",
        "default_foreign": True,
    },
    "abbr of": {"alias_of": "abbreviation of"},
    "abbrev of": {"alias_of": "abbreviation of"},
    "initialism of": {
        "text": "initialism of",
        "type_prefix": "ABBREVIATION_OF",
        "default_foreign": True,
    },
    "init of": {"alias_of": "initialism of"},
    "acronym of": {
        "text": "acronym of",
        "type_prefix": "ABBREVIATION_OF",
        "default_foreign": True,
    },
    "syllabic abbreviation of": {
        "text": "syllabic abbreviation of",
        "type_prefix": "ABBREVIATION_OF",
        "default_foreign": True,
    },
    "sylabbr of": {"alias_of": "syllabic abbreviation of"},
    "sylabbrev of": {"alias_of": "syllabic abbreviation of"},
    "ellipsis of": {
        "text": "ellipsis of",
        "type_prefix": "ELLIPSIS_OF",
        "default_foreign": True,
    },
    "ellip of": {"alias_of": "ellipsis of"},
    "clipping of": {
        "text": "clipping of",
        "type_prefix": "CLIPPING_OF",
        "default_foreign": True,
    },
    "clip of": {"alias_of": "clipping of"},
    "alternative form of": {"text": "+", "default_foreign": True},
    "alt form": {"alias_of": "alternative form of"},
    "alternative spelling of": {"text": "+", "default_foreign": True},
    "alt spell": {"alias_of": "alternative spelling of"},
    "alt sp": {"alias_of": "alternative spelling of"},
    "dated form of": {
        "text": "dated form of",
        "type_prefix": "DATED_FORM_OF",
        "default_foreign": True,
    },
    "dated form": {"alias_of": "dated form of"},
    "dated spelling of": {
        "text": "dated spelling of",
        "type_prefix": "DATED_FORM_OF",
        "default_foreign": True,
    },
    "dated spell": {"alias_of": "dated spelling of"},
    "dated sp": {"alias_of": "dated spelling of"},
    "archaic form of": {
        "text": "archaic form of",
        "type_prefix": "ARCHAIC_FORM_OF",
        "default_foreign": True,
    },
    "arch form": {"alias_of": "archaic form of"},
    "archaic spelling of": {
        "text": "archaic spelling of",
        "type_prefix": "ARCHAIC_FORM_OF",
        "default_foreign": True,
    },
    "arch spell": {"alias_of": "archaic spelling of"},
    "arch sp": {"alias_of": "archaic spelling of"},
    "obsolete form of": {
        "text": "obsolete form of",
        "type_prefix": "OBSOLETE_FORM_OF",
        "default_foreign": True,
    },
    "obs form": {"alias_of": "obsolete form of"},
    "obsolete spelling of": {
        "text": "obsolete spelling of",
        "type_prefix": "OBSOLETE_FORM_OF",
        "default_foreign": True,
    },
    "obs spell": {"alias_of": "obsolete spelling of"},
    "obs sp": {"alias_of": "obsolete spelling of"},
}


def get_seat_text(overall_place_spec: dict[str, Any]) -> str:
    placetype = overall_place_spec["descs"][0]["placetypes"][0]
    if placetype in {"county", "counties"}:
        return "county seat"
    elif placetype in {"parish", "parishes"}:
        return "parish seat"
    elif placetype in {"borough", "boroughs"}:
        return "borough seat"
    else:
        return "seat"


EXTRA_INFO_ARGS: list[dict[str, Any]] = [
    {"arg": "modern", "text": "+", "conjunction": "or", "display_even_when_dropped": True},
    {"arg": "now", "text": "now,", "conjunction": "or", "display_even_when_dropped": True},
    {"arg": "full", "text": "in full,", "conjunction": "or", "display_even_when_dropped": True},
    {"arg": "short", "text": "short form", "conjunction": "or"},
    {"arg": "abbr", "text": "abbreviation", "conjunction": "or"},
    {"arg": "former", "text": "formerly,"},
    {"arg": "official", "text": "official name", "match_sentence_style": True, "auto_plural": True, "with_colon": True},
    {"arg": "capital", "text": "+", "match_sentence_style": True, "auto_plural": True, "with_colon": True},
    {"arg": "largest city", "text": "+", "match_sentence_style": True, "auto_plural": True, "with_colon": True},
    {
        "arg": "caplc",
        "text": "capital and largest city",
        "match_sentence_style": True,
        "auto_plural": False,
        "with_colon": True,
    },
    {"arg": "seat", "text": get_seat_text, "match_sentence_style": True, "auto_plural": True, "with_colon": True},
    {"arg": "shire town", "text": "+", "match_sentence_style": True, "auto_plural": True, "with_colon": True},
    {"arg": "headquarters", "text": "+", "match_sentence_style": True, "auto_plural": False, "with_colon": True},
    {
        "arg": "center",
        "text": "administrative center",
        "match_sentence_style": True,
        "auto_plural": False,
        "with_colon": True,
    },
    {
        "arg": "centre",
        "text": "administrative centre",
        "match_sentence_style": True,
        "auto_plural": False,
        "with_colon": True,
    },
]


def split_holonym(raw: str) -> list[dict[str, Any]]:
    # Preprocess for display suppression and comma suppression
    no_display_match = re.match(r"^(!)(.*)$", raw)
    no_display = bool(no_display_match)
    combined_holonym = no_display_match[2] if no_display_match else raw
    suppress_comma_match = re.match(r"^(\*)(.*)$", combined_holonym)
    suppress_comma = bool(suppress_comma_match)
    combined_holonym = suppress_comma_match[2] if suppress_comma_match else combined_holonym

    holonym_parts = combined_holonym.split("/")
    if len(holonym_parts) == 1:
        # Only one part, return as single holonym
        return [{"display_placename": combined_holonym, "no_display": no_display, "suppress_comma": suppress_comma}]

    # Rejoin further slashes for placename
    placetype = holonym_parts[0]
    placename = "/".join(holonym_parts[1:])

    # Check for modifiers after holonym placetype
    split_holonym_placetype = placetype.split(":", 1)
    placetype = split_holonym_placetype[0]
    affix_type = None
    saw_the = False
    for modifier in split_holonym_placetype[1:]:
        if modifier == "also":
            pass
        elif modifier == "the":
            saw_the = True
        elif modifier in {"pref", "Pref", "suf", "Suf", "noaff"}:
            affix_type = modifier

    placetype = resolve_placetype_aliases(placetype)
    holonyms = placename.split(",")
    pluralize_affix = len(holonyms) > 1
    affix_holonym_index = 1 if affix_type in {"pref", "Pref"} else 0 if affix_type == "noaff" else len(holonyms)
    for i, placename in enumerate(holonyms):
        # Check for langcode prefix, don't trip on Wikipedia links
        langcode_match = re.match(r"^([^\[\]]-):(.*)$", placename)
        langcode = None
        if langcode_match:
            langcode, placename = langcode_match
        placename = resolve_placename_display_aliases(placetype, placename)
        holonyms[i] = {
            "placetype": placetype,
            "display_placename": placename,
            "unlinked_placename": remove_links_and_html(placename),
            "langcode": langcode,
            "affix_type": affix_type if i + 1 == affix_holonym_index else None,
            "pluralize_affix": pluralize_affix if i + 1 == affix_holonym_index else False,
            "suppress_affix": i + 1 != affix_holonym_index,
            "no_display": no_display,
            "suppress_comma": suppress_comma,
            "force_the": saw_the if i == 0 else False,
        }
    return holonyms


def parse_term_with_inline_modifiers(term: str, paramname: str, default_lang: Any) -> dict[str, Any]:
    def generate_obj(raw_term: str, parse_err=None) -> dict[str, Any]:
        obj = parameter_utilities.generate_obj_maybe_parsing_lang_prefix(
            {
                "term": raw_term,
                "parse_err": parse_err,
                "parse_lang_prefix": True,
            }
        )
        obj["lang"] = obj.get("lang") or default_lang
        return obj

    return parse_interface.parse_inline_modifiers(
        term,
        {
            "paramname": paramname,
            "param_mods": get_param_mods,
            "generate_obj": generate_obj,
            "splitchar": ",",
            "outer_container": {},
        },
    )


def parse_form_of_directive(arg: str, lang: Any, form_of_overridden_args: dict[str, Any] | None) -> dict[str, Any]:
    if not (m := re.match(r"^@([a-z -]+):(.*)$", arg)):
        list(ALL_FORM_OF_DIRECTIVES.keys())
        return {}

    form_of_directive, raw_terms = m[1], m[2]
    spec = ALL_FORM_OF_DIRECTIVES[form_of_directive]
    canonical_directive = form_of_directive
    default_foreign = spec.get("default_foreign")
    directive_param = f"@{form_of_directive}"
    if form_of_overridden_args and canonical_directive in form_of_overridden_args:
        raw_terms = form_of_overridden_args[canonical_directive]["new_value"]
        new_directive = form_of_overridden_args[canonical_directive]["new_directive"]
        new_spec = ALL_FORM_OF_DIRECTIVES[new_directive]
        if new_directive != canonical_directive:
            directive_param += f" (replaced with @{new_directive})"
            canonical_directive = new_directive
            spec = new_spec
        default_foreign = True
    terms = parse_term_with_inline_modifiers(raw_terms, directive_param, lang if default_foreign else "en")
    return {
        "directive": canonical_directive,
        "terms": terms["terms"],
        "conj": terms["conj"],
        "spec": spec,
    }


def parse_new_style_place_desc(
    text: str, lang: Any, form_of_directives: list[Any], form_of_overridden_args: dict[str, Any] | None
) -> dict[str, Any]:
    placetypes: list[str] = []
    segments = re.split(r"<<(.-)>>", text)
    retval = {"holonyms": [], "order": []}
    form_of_directives_already_present = bool(
        form_of_directives and form_of_directives[0] if form_of_directives else False
    )
    for i, segment in enumerate(segments, start=1):
        if i % 2 == 1:
            insert(retval["order"], {"type": "raw", "value": segment})
        elif "@" in segment:
            form_of_directive = parse_form_of_directive(segment, lang, form_of_overridden_args)
            form_of_directive["pretext"] = retval["order"][0]["value"]
            retval["order"][0] = None
            insert(form_of_directives, form_of_directive)
        elif "/" in segment:
            holonyms = en_utilities.split_holonym(segment)
            for j, holonym in enumerate(holonyms, start=1):
                if j > 1:
                    if not holonym.get("no_display"):
                        if j == len(holonyms):
                            insert(retval["order"], {"type": "raw", "value": " and "})
                        else:
                            insert(retval["order"], {"type": "raw", "value": ", "})
                    holonym["needs_article"] = True
                insert(retval["holonyms"], holonym)
                if not holonym.get("no_display"):
                    insert(retval["order"], {"type": "holonym", "value": len(retval["holonyms"])})
                place_placetypes.key_holonym_into_place_desc(retval, holonym)
        else:
            m = re.match(r"^(..-):(.+)$", segment)
            treat_as, display = m.groups() if m else (None, None)
            if treat_as:
                segment = treat_as
            else:
                display = segment
            only_qualifiers = all(
                place_placetypes.placetype_qualifiers.get(seg) is not None for seg in split(segment, " ", True)
            )
            insert(placetypes, {"placetype": segment, "only_qualifiers": only_qualifiers})
            if only_qualifiers:
                insert(retval["order"], {"type": "qualifier", "value": display})
            else:
                insert(retval["order"], {"type": "placetype", "value": display})
    if not form_of_directives_already_present and form_of_directives and form_of_directives[0]:
        form_of_directives[-1]["posttext"] = ""
    final_placetypes = []
    for i, placetype in enumerate(placetypes, start=1):
        if i > 1 and placetypes[i - 2]["only_qualifiers"]:
            final_placetypes[-1] = final_placetypes[-1] + " " + placetypes[i - 1]["placetype"]
        else:
            insert(final_placetypes, placetypes[i - 1]["placetype"])
    retval["placetypes"] = final_placetypes
    return retval


def get_translations(transl: list[str], ids: list[str]) -> str:
    ret = []
    for i, t in enumerate(transl):
        arg_transls = t.split(",")
        arg_ids = ids[i] if ids and i < len(ids) else None
        if arg_ids:
            arg_ids = arg_ids.split(",")
        ret.extend(
            arg_ids[j] if arg_ids and j < len(arg_ids) else arg_transl for j, arg_transl in enumerate(arg_transls)
        )
    return ", ".join(ret)


def get_display_form(data: dict[str, Any]) -> str:
    overall_place_spec = data["overall_place_spec"]
    ucfirst = data.get("ucfirst", False)
    sentence_style = data.get("sentence_style", False)
    drop_extra_info = data.get("drop_extra_info", False)
    extra_info_overridden_set = data.get("extra_info_overridden_set")
    from_tcl = data.get("from_tcl")
    args = overall_place_spec["args"]
    parts = []

    def ins(txt: str):
        parts.append(txt)

    if overall_place_spec.get("directives") and overall_place_spec["directives"][0]:
        for i, directive_terms in enumerate(overall_place_spec["directives"], start=1):
            ins(directive_terms.get("pretext", ""))
            if directive_terms.get("pretext", "") != "":
                ucfirst = False
            ins(en_utilities.format_form_of_directive(overall_place_spec, directive_terms, ucfirst, from_tcl))
            ucfirst = False
            if i == len(overall_place_spec["directives"]) and directive_terms.get("posttext"):
                ins(directive_terms["posttext"])
    if args.get("def") == "-":
        return " ".join(parts)
    if args.get("def"):
        if "<<" in args["def"]:
            def_desc = parse_new_style_place_desc(args["def"], args[1])
            ins(en_utilities.format_new_style_place_desc_for_display({}, def_desc, False))
        else:
            ins(args["def"])
    else:
        include_article = True
        for n, desc in enumerate(overall_place_spec["descs"], start=1):
            if desc.get("order"):
                ins(en_utilities.format_new_style_place_desc_for_display(args, desc, n == 1))
            else:
                ins(en_utilities.format_old_style_place_desc_for_display(args, desc, n, include_article, ucfirst))
            if desc.get("joiner"):
                ins(desc["joiner"])
            include_article = desc.get("include_following_article", include_article)
            ucfirst = False
    addl = args.get("addl")
    if addl:
        data.get("posttext", "")
        if addl.startswith(";") or addl.startswith(":"):
            ins(addl)
        elif addl.startswith("_"):
            ins(f" {addl[1:]}")
        else:
            ins(f", {addl}")
    for extra_info_terms in overall_place_spec["extra_info"]:
        if (
            not drop_extra_info
            or extra_info_terms["spec"].get("display_even_when_dropped")
            or (extra_info_overridden_set and extra_info_overridden_set.get(extra_info_terms["spec"]["arg"]))
        ):
            ins(en_utilities.format_extra_info(overall_place_spec, extra_info_terms, sentence_style))
    return " ".join(parts)


def get_def(data: defaultdict) -> str:
    overall_place_spec = data["overall_place_spec"]
    from_tcl = data["from_tcl"]
    drop_extra_info = data["drop_extra_info"]
    extra_info_overridden_set = data["extra_info_overridden_set"]
    translation_follows = data["translation_follows"]
    sentence_style = overall_place_spec["lang"].getCode() == "en"
    if data["t"]:
        gloss = get_display_form(
            {
                "overall_place_spec": overall_place_spec,
                "ucfirst": False,
                "sentence_style": False,
                "drop_extra_info": drop_extra_info,
                "extra_info_overridden_set": extra_info_overridden_set,
                "from_tcl": from_tcl,
            }
        )
        if from_tcl and not data["tcl_nolc"]:
            gloss = capitalize(gloss)
        if translation_follows:
            return (gloss if gloss == "" else f"{gloss}: ") + get_translations(data["t"], data.get("tid", []))
        else:
            return get_translations(data["t"], data.get("tid", [])) + (gloss or f" ({gloss})")
    else:
        ucfirst = sentence_style and not data["nocap"]
        return get_display_form(
            {
                "overall_place_spec": overall_place_spec,
                "ucfirst": ucfirst,
                "sentence_style": sentence_style,
                "drop_extra_info": drop_extra_info,
                "extra_info_overridden_set": extra_info_overridden_set,
                "from_tcl": from_tcl,
            }
        )
