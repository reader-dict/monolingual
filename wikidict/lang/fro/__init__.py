"""Old French language."""

from .. import fr

section_patterns = fr.section_patterns
head_sections = tuple(section.replace("fr", "fro") for section in fr.head_sections)
sections = tuple(section.replace("fr", "fro") for section in fr.sections)
variant_titles = tuple(section.replace("fr", "fro") for section in fr.variant_titles)
variant_templates = tuple(section.replace("fr", "fro") for section in fr.variant_templates)

float_separator = fr.float_separator
thousands_separator = fr.thousands_separator
definitions_to_ignore = fr.definitions_to_ignore
templates_ignored = fr.templates_ignored
templates_italic = fr.templates_italic
templates_multi = fr.templates_multi
templates_other = fr.templates_other
etyl_section = fr.etyl_section
find_genders = fr.find_genders
find_pronunciations = fr.find_pronunciations
last_template_handler = fr.last_template_handler
adjust_wikicode = fr.adjust_wikicode

# https://fr.wiktionary.org/wiki/Wiktionnaire:Page_au_hasard
random_word_url = "http://tools.wmflabs.org/anagrimes/hasard.php?langue=fro"
