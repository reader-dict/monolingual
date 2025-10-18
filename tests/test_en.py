from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("en")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "ab",
            ["/æb/"],
            [],
            [
                "Clipping of English <i><b>Ab</b>khaz</i> or Russian <i>абха́з</i> (<b>ab</b>xáz).",
                "Abbreviation of <i>abscess</i>.",
                "From the spelling books and the fact that it was the first of the letter combinations.",
            ],
            {
                "Adverb": ["Abbreviation of <i>about</i>."],
                "Noun": [
                    "(<i>informal</i>) Clipping of <i>abdominal muscle</i> &lsqb;mid 20<sup>th</sup> century&rsqb;.",
                    "(<i>slang</i>) An abscess caused by injecting an illegal drug, usually heroin.",
                    "Abbreviation of <i>abortion</i>.",
                    "(<i>US</i>) The early stages of; the beginning process; the start.",
                ],
                "Preposition": ["Abbreviation of <i>about</i>."],
                "Symbol": ["(<i>international standards</i>) <i>ISO 639-1 language code for </i><b>Abkhaz</b><i>.</i>"],
                "Verb": ["(climbing,&#32;informal) To abseil.", "Abbreviation of <i>abort</i>."],
            },
            [],
        ),
        (
            "Acanthis",
            [],
            ["f"],
            ["See <b>Acanthis (mythology)</b> on Wikipedia."],
            {
                "Proper Noun": [
                    "A taxonomic genus within the family Fringillidae&nbsp;– redpolls, of northern woodlands, formerly included in <i>Carduelis</i>."
                ]
            },
            [],
        ),
        (
            "cum",
            ["/kʊm/", "/kʌm/"],
            [],
            [
                "Clipping of English <i><b>Cum</b>eral</i>.",
                "Learned borrowing from Latin <i>cum</i> (“with”).",
                'Variant of <i>come</i>, attested (in the basic sense "come, move from further to nearer, arrive") since Old English. The sexual sense of <i>come</i> is attested since the 1650s. In this sense and spelling, attested from 1970s.',
            ],
            {
                "Adjective": ["Clipping of <i>cumulative</i>."],
                "Noun": [
                    "(colloquial,&#32;often&#32;vulgar) Semen.",
                    "(colloquial,&#32;often&#32;vulgar) Female ejaculatory discharge.",
                    "(colloquial,&#32;often&#32;vulgar) An ejaculation.",
                    "Abbreviation of <i>cubic metre</i>.",
                ],
                "Preposition": [
                    "Used in indicating a thing or person which has two or more roles, functions, or natures, or which has changed from one to another.",
                ],
                "Symbol": [
                    "(international standards,&#32;obsolete) <i>Former&#x20;ISO 639-3 language code for </i><b>Cumeral</b><i>.</i>"
                ],
                "Verb": [
                    "(slang,&#32;often&#32;vulgar) To have an orgasm, to feel the sensation of an orgasm.",
                    "(slang,&#32;often&#32;vulgar) To ejaculate.",
                    "Eye dialect spelling of <i>come</i> (“move from further to nearer; arrive”).",
                ],
            },
            [],
        ),
        (
            "efficient",
            ["/əˈfɪʃənt/", "/ɪˈfɪʃənt/"],
            [],
            [
                "1398, “making,” from Old French, from Latin <i>efficientem</i>, nominative <i>efficiēns</i>, participle of <i>efficere</i> (“work out, accomplish”) (see <i>effect</i>). Meaning “productive, skilled” is from 1787. <i>Efficiency apartment</i> is first recorded 1930, American English."
            ],
            {
                "Adjective": [
                    "Making good, thorough, or careful use of resources; not consuming extra. Especially, making good use of time or energy.",
                    "Expressing the proportion of consumed energy that was successfully used in a process; the ratio of useful output to total input.",
                    "Causing effects, producing results; bringing into being; initiating change (rare except in philosophical and legal expression <i>efficient cause</i> = causative factor or agent).",
                    "(proscribed,&#32;old use) effective, efficacious",
                ],
                "Noun": ["(<i>obsolete</i>) A cause; something that causes an effect."],
            },
            [],
        ),
        (
            "humans",
            [],
            [],
            [],
            {},
            ["human"],
        ),
        (
            "it's",
            ["/ɪts/"],
            [],
            [
                "Contraction of ‘it is’, ‘it has’ or 'it was'.",
                "From <i>it</i> +&lrm; <i>-’s</i> (possessive marker).",
            ],
            {
                "Contraction": [
                    "Contraction of <i>it is</i>.",
                    "Contraction of <i>it has</i>.",
                    "(<i>proscribed</i>) Contraction of <i>it was</i>",
                    "(<i>dialectal</i>) There's, there is; there're, there are.",
                ],
                "Determiner": ["Obsolete form of <i>its</i>.", "Misspelling of <i>its</i>."],
            },
            [],
        ),
        (
            "Mars",
            ["/maɹs/", "/mɑ˞s/", "/ˈmɑɹz/", "/ˈmɑːz/"],
            [],
            [
                "From Middle English&#32;<i>Mars</i>, from Latin&#32;<i>Mārs</i>&#32;(“god of war”), from older Latin (older than 75 <small>BCE</small>) <i>Māvors</i>.",
                "Possibly a variant of <i>Marrs</i>, itself from <i>Marr</i> with post-medieval excrescent <i>-s</i>.",
                "The Mars bar was named after Franklin Clarence Mars, who founded the company that produces these chocolate bars.",
                "From Ukrainian <i>Марс</i> (Mars).",
            ],
            {
                "Noun": [
                    "(heraldry,&#32;rare) Gules (red), in the postmedieval practice of blazoning the tinctures of certain sovereigns' (especially British monarchs') coats as planets.",
                    "(obsolete,&#32;alchemy,&#32;chemistry) Iron.",
                    "Alternative form of <i>Mas</i>.",
                ],
                "Proper Noun": [
                    "(<i>astronomy</i>) The fourth planet in the solar system. Symbol: <b>♂</b>",
                    "(<i>Roman mythology</i>) The Roman god of war.",
                    "(<i>poetic</i>) War; a personification of war.",
                    "A surname.",
                    "A brand of chocolate bar with caramel and nougat filling.",
                    "A village in Semenivka urban hromada, Novhorod-Siverskyi Raion, Chernihiv Oblast, Ukraine.",
                ],
            },
            [],
        ),
        ("memoized", [], [], [], {}, ["memoize"]),
        (
            "portmanteau",
            ["/pɔːtˈmæn.təʊ/", "/pɔːɹtˈmæntoʊ/", "/ˌpɔːɹtmænˈtoʊ/"],
            [],
            [
                "From Middle French <i>portemanteau</i> (“coat stand”), from <i>porte</i> (“carries”, third-person singular present indicative of <i>porter</i> (“to carry”)) +&lrm; <i>manteau</i> (“coat”), literally “[that which] carries coat”.",
                "First used by Lewis Carroll in <i>Through the Looking-Glass</i> to describe the words he coined in “Jabberwocky”.",
            ],
            {
                "Adjective": [
                    "(attributive,&#32;linguistics) Made by combining two (or more) words, stories, etc., in the manner of a linguistic portmanteau."
                ],
                "Noun": [
                    "A large travelling case usually made of leather, and opening into two equal sections.",
                    "(Australia,&#32;dated) A schoolbag.",
                    "(<i>archaic</i>) A hook on which to hang clothing.",
                    "(<i>linguistics</i>) A word formed by putting two words together and thereby their meaning e.g. shrinkflation.",
                    "A portmanteau film.",
                ],
                "Verb": ["(<i>transitive</i>) To create a portmanteau word."],
            },
            [],
        ),
        (
            "someone",
            ["/ˈsʌmwʌn/"],
            [],
            [
                "From Middle English <i>sum on</i>, <i>sum one</i>, <i>sum oon</i>, equivalent to <i>some</i> +&lrm; <i>one</i>.",
            ],
            {
                "Noun": ["A partially specified but unnamed person.", "An important person."],
                "Pronoun": ["One or some person of unspecified or indefinite identity."],
            },
            [],
        ),
        (
            "scourge",
            ["/skɜɹd͡ʒ/", "/skɜːd͡ʒ/"],
            [],
            [],
            {
                "Noun": [
                    "(weaponry,&#32;chiefly&#32;historical) A whip, often made of leather and having multiple tails; a lash.",
                    "(<i>figurative</i>)",
                    (
                        "A person or thing regarded as an agent of divine punishment.",
                        "A source of persistent (and often widespread) pain and suffering or trouble, such as a cruel ruler, disease, pestilence, or war.",
                    ),
                ]
            },
            [],
        ),
        (
            "the",
            ["/ði/", "/ðiː/", "/ðə/"],
            [],
            [
                "From Middle English <i>þe</i>, from Old English <i>þē</i>&nbsp;m (“the, that”, demonstrative pronoun), a late variant of <i>sē</i>, the <i>s-</i> (which occurred in the masculine and feminine nominative singular only) having been replaced by the <i>þ-</i> from the oblique stem.",
                "replaced words, cognates",
                "Originally neutral nominative, in Middle English it superseded all previous Old English nominative forms (<i>sē</i>&nbsp;m, <i>sēo</i>&nbsp;f, <i>þæt</i>&nbsp;n, <i>þā</i>&nbsp;pl); <i>sē</i> is from Proto-West Germanic <i>&#42;siz</i>, from Proto-Germanic <i>&#42;sa</i>, ultimately from Proto-Indo-European <i>&#42;só</i>.",
                "Cognate with Saterland Frisian <i>die</i> (“the”), West Frisian <i>de</i> (“the”), Dutch <i>de</i> (“the”), German Low German <i>de</i> (“the”), German <i>der</i> (“the”), Danish <i>de</i> (“the”), Swedish <i>de</i> (“the”), Icelandic <i>sá</i> (“that”) within Germanic and with Sanskrit <i>स</i> (sá, “the, that”), Ancient Greek <i>ὁ</i> (ho, “the”), Tocharian B <i>se</i> (“this”) among other Indo-European languages.",
                'From Middle English <i>the</i>, <i>thy</i>, <i>thi</i>, from Old English <i>þē̆</i>, probably a neuter instrumental form ("by that, thereby")—alongside the more common <i>þȳ</i> and <i>þon</i>—of the demonstrative pronoun <i>sē</i> ("that"). Compare Dutch <i>des <i>te</i></i> ("the, the more"), German <i>des<i>to</i></i> ("the, all the more"), Norwegian <i>for<i>di</i></i> and Norwegian <i>av di</i> ("because"), Icelandic <i>því</i> (“the; because”), Faroese <i>tí</i>, Swedish <i>ty</i>.',
            ],
            {
                "Adverb": [
                    "With a comparative or with <i>more</i> and a verb phrase, establishes a correlation with one or more other such comparatives.",
                    "With a comparative, and often with <i>for it</i>, indicates a result more like said comparative. This can be negated with <i>none</i>.",
                    "(<i>with a superlative adjective</i>) Beyond all others.",
                ],
                "Article": [
                    "Used before a noun phrase, including a simple noun",
                    (
                        "The definite grammatical article that shows that the noun phrase that immediately follows it is definitely identifiable...",
                        (
                            "...because it has already been mentioned, is to be completely specified in the same sentence, or very shortly thereafter. &lsqb;from 10th c.&rsqb;",
                            "...because it is presumed to be definitely known in context or from shared knowledge.",
                        ),
                        "When stressed, indicates that it describes something which is considered to be best or exclusively worthy of attention. &lsqb;from 18th c.&rsqb;",
                        "Used before a noun phrase beginning with superlative or comparative adjective or an ordinal number, indicating that the noun refers to a single item.",
                        "Introducing a singular term to be taken generically&#58; preceding a name of something standing for a whole class. &lsqb;from 9th c.&rsqb;",
                        "Used with the plural of a surname to indicate the entire family.",
                    ),
                    "Used with an adjective",
                    (
                        "Added to a superlative or an ordinal number to make it into a substantive. &lsqb;from 9th c.&rsqb;",
                        "Used before an adjective, indicating all things (especially persons) described by that adjective. &lsqb;from 9th c.&rsqb;",
                        "Used before a demonym ending in <i>-ish</i> or <i>-ese</i> to refer to people of a given country collectively.",
                    ),
                ],
                "Preposition": ["For each; per."],
                "Pronoun": ["Obsolete form of <i>thee</i>."],
                "Symbol": [
                    "(<i>international standards</i>) <i>ISO 639-3 language code for </i><b>Chitwania Tharu</b><i>.</i>"
                ],
            },
            [],
        ),
        (
            "um",
            ["/ʌm/"],
            [],
            [
                "From <i>u-</i> (“micro-”) +&lrm; <i>m</i> (“metre”).",
                "Onomatopoeic.",
                "Variant form of <i>-um</i>.",
            ],
            {
                "Interjection": [
                    "Expression of hesitation, uncertainty or space filler in conversation.",
                    "(<i>chiefly&#32;US</i>) Dated spelling of <i>mmm</i>.",
                    "An expression to forcefully call attention to something wrong.",
                    "(<i>childish</i>) An expression of shocked disapproval used by a child who witnesses forbidden behavior.",
                ],
                "Noun": ['An occurrence of the interjection "um".'],
                "Particle": [
                    "(dated,&#32;sometimes&#32;humorous,&#32;often&#32;offensive) An undifferentiated determiner or article&#59; a miscellaneous linking word, or filler with nonspecific meaning&#59; representation of broken English stereotypically or comically attributed to Native Americans."
                ],
                "Symbol": ["(metrology,&#32;informal,&#32;proscribed) Alternative form of <i>μm</i>."],
                "Verb": ["(<i>intransitive</i>) To make the <i>um</i> sound to express uncertainty or hesitancy."],
            },
            [],
        ),
        (
            "us",
            ["/əs/", "/əz/", "/ɪz/", "/ʊs/", "/ʌs/", "/ʌz/"],
            [],
            [
                "From <i>u-</i> (“micro-”) +&lrm; <i>s</i> (“second”).",
                "Etymology treeMiddle English <i>us</i>English <i><b>us</b></i>",
                "From Middle English <i>us</i>, from Old English <i>ūs</i> (“us”, dative personal pronoun), from Proto-West Germanic <i>&#42;uns</i>, from Proto-Germanic <i>&#42;uns</i> (“us”), from Proto-Indo-European <i>&#42;n̥swé</i>, alteration of <i>&#42;n̥smé</i> (“us”). The compensatory lengthening was lost in Middle English due to the word being unstressed when used. Cognate with Saterland Frisian <i>uus</i> (“us”), West Frisian <i>us</i>, <i>ús</i> (“us”), Low German <i>uns</i>, <i>us</i> (“us”), Dutch <i>ons</i> (“us”), German <i>uns</i> (“us”), Danish <i>os</i> (“us”), Latin <i>nōs</i> (“we, us”).",
                "From <i>u-</i> (“micro-, 10<sup>-6</sup>”) +&lrm; <i>s</i> (“second”).",
            ],
            {
                "Determiner": [
                    "Designates the speaker(s)&#47;writer(s) as constituting or belonging to the stated category of people (objective case).",
                    "(<i>proscribed</i>) Designates the speaker(s)&#47;writer(s) as constituting or belonging to the stated category of people (subjective case).",
                    "(Northern England,&#32;Nottinghamshire) Our.",
                ],
                "Noun": ["(<i>rare</i>) Alternative form of <i>u's</i>."],
                "Pronoun": [
                    "Me and at least one other person, excluding the person(s) being addressed. (exclusive <i>us</i>.)",
                    "Me and at least one other person, including the person(s) being addressed. (inclusive <i>us</i>.)",
                    'We, used in the same circumstances where "me" would be used instead of "I", e.g. for the pronoun in isolation or as the complement of the copula&#58;',
                    "Any entity that the speaker is a part of or identifies with, such as place of employment or education, nation, region, language, etc.",
                    "People in general.",
                    "(<i>colloquial</i>) The person(s) being addressed.",
                    "(<i>colloquial</i>) Used to imply connection between the speaker's experiences or activities and a group of listeners.",
                    "(Commonwealth,&#32;colloquial,&#32;chiefly with certain verbs such as <i>give</i>, <i>get</i>, <i>fetch</i>, etc.) Me.",
                    "(<i>Northumbria</i>) Me (in all contexts).",
                ],
                "Symbol": [
                    "(metrology,&#32;informal,&#32;proscribed) Alternative form of <i>μs</i>.",
                    "Alternative spelling of <i>μs</i>: microsecond.",
                ],
            },
            [],
        ),
        (
            "water",
            [
                "/-ɑ/",
                "/wʊʔə/",
                "/ˈwoː.tə/",
                "/ˈwæ.tə/",
                "/ˈwɐː.t̪əɹ/",
                "/ˈwɑ.təɹ/",
                "/ˈwɒ.tə/",
                "/ˈwɒ.təɹ/",
                "/ˈwɔ.tə/",
                "/ˈwɔ.tər/",
                "/ˈwɔ.təɹ/",
                "/ˈwɔɹ.təɹ/",
                "/ˈwɔː.tə/",
                "/ˈwɔː.təɹ/",
                "/ˈwʊ.təɹ/",
            ],
            [],
            [
                "Etymology treeMiddle English <i>water</i>English <i><b>water</b></i>",
                "From Middle English <i>water</i>, from Old English <i>wæter</i> (“water”), from Proto-West Germanic <i>&#42;watar</i>, from Proto-Germanic <i>&#42;watōr</i> (“water”), from Proto-Indo-European <i>&#42;wódr̥</i> (“water”).",
                "Cognates",
                "Cognate with Scots <i>watter</i> (“water”), Yola <i>wadher</i>, <i>waudher</i> (“water”), North Frisian <i>weeder</i>, <i>Weeter</i>, <i>wååder</i> (“water”), Saterland Frisian <i>Woater</i> (“water”), West Frisian <i>wetter</i> (“water”), Cimbrian <i>bassar</i>, <i>bazzar</i> (“water”), Dutch <i>water</i> (“water”), Dutch Low Saxon <i>water</i>, <i>wotter</i> (“water”), German <i>Wasser</i> (“water”), German Low German <i>Water</i>, <i>Woter</i> (“water”), Gottscheerish <i>boßər</i>, <i>bàsser</i> (“water”), Limburgish <i>Waater</i>, <i>water</i> (“water”), Luxembourgish <i>Waasser</i> (“water”), Mòcheno <i>bòsser</i> (“water”), Vilamovian <i>woser</i> (“water”), West Flemish <i>woater</i> (“water”), Yiddish <i>וואַסער</i> (vaser, “water”), Danish <i>vand</i> (“water”), Elfdalian <i>wattn</i> (“water”), Faroese, Icelandic, Norwegian Nynorsk <i>vatn</i> (“water”), Norwegian Bokmål <i>vann</i> (“water”), Swedish <i>vatten</i> (“water”), Gothic <i>𐍅𐌰𐍄𐍉</i> (watō, “water”), Old Irish <i>coin fodorne</i> (“otters”, literally “water-dogs”), Latin <i>unda</i> (“wave”), Lithuanian <i>vanduõ</i> (“water”), Russian <i>вода́</i> (vodá, “water”), Albanian <i>ujë</i> (“water”), Ancient Greek <i>ὕδωρ</i> (húdōr, “water”), Armenian <i>գետ</i> (get, “river”), Sanskrit <i>उदन्</i> (udán, “wave, water”), Hittite <i>𒉿𒀀𒋻</i> (wa-a-tar).",
                "From Middle English <i>wateren</i>, from Old English <i>wæterian</i>, from Proto-Germanic <i>&#42;watrōną</i>, <i>&#42;watrijaną</i>, from Proto-Germanic <i>&#42;watōr</i> (“water”), from Proto-Indo-European <i>&#42;wódr̥</i> (“water”).",
                "Cognate with Scots <i>watter</i> (“water”), Saterland Frisian <i>woaterje</i> (“to water”), West Frisian <i>wetterje</i> (“to water”), Dutch <i>wateren</i> (“to water”), German Low German <i>watern</i> (“to water”), German <i>wässern</i> (“to water”), Danish <i>vande</i> (“to water”), Swedish <i>vattna</i> (“to water”), Icelandic <i>vatna</i> (“to water”).",
            ],
            {
                "Noun": [
                    "(<i>uncountable</i>) A inorganic compound (of molecular formula H<sub>2</sub>O) found at room temperature and pressure as a clear liquid; it is present naturally as rain, and found in rivers, lakes and seas; its solid form is ice and its gaseous form is steam.",
                    (
                        "(uncountable,&#32;in particular) The liquid form of this substance: liquid H<sub>2</sub>O.",
                        "(<i>countable</i>) A serving of liquid water.",
                    ),
                    "(alchemy,&#32;philosophy) The aforementioned liquid, considered one of the Classical elements or basic elements of alchemy.",
                    "(<i>uncountable&#32;or&#32;in the plural</i>) Water in a body; an area of open water.",
                    "(poetic,&#32;archaic&#32;or&#32;dialectal) A body of water, almost always a river, sometimes a lake or reservoir, especially in the names given to such bodies.",
                    "A combination of water and other substance(s).",
                    (
                        "(<i>sometimes&#32;countable</i>) Mineral water.",
                        "(countable,&#32;often&#32;in the plural) Spa water.",
                        "(<i>pharmacy</i>) A solution in water of a gaseous or readily volatile substance.",
                        "Urine. &lsqb;from 15th c.&rsqb;",
                        "Amniotic fluid or the amniotic sac containing it. (<i>Used only in the plural in the UK but often also in the singular in North America.</i>)",
                        "(colloquial,&#32;medicine) Fluids in the body, especially when causing swelling.",
                    ),
                    "(business,&#32;often&#32;attributive) The water supply, as a service or utility.",
                    "(figuratively,&#32;in the plural&#32;or&#32;in the singular) A state of affairs; conditions; usually with an adjective indicating an adverse condition.",
                    "(colloquial,&#32;figuratively) A person's intuition.",
                    "(uncountable,&#32;dated,&#32;finance) Excess valuation of securities.",
                    "A particular quality or appearance suggestive of water:",
                    (
                        "The limpidity and lustre of a precious stone, especially a diamond.",
                        "A wavy, lustrous pattern or decoration such as is imparted to linen, silk, metals, etc.",
                    ),
                ],
                "Verb": [
                    "(<i>transitive</i>) To pour water into the soil surrounding (plants).",
                    "(<i>transitive</i>) To wet or supply with water; to moisten; to overflow with water; to irrigate.",
                    "(<i>transitive</i>) To provide (animals) with water for drinking.",
                    "(<i>intransitive</i>) To get or take in water.",
                    "(transitive,&#32;colloquial) To urinate onto.",
                    "(<i>transitive</i>) To dilute.",
                    "(transitive,&#32;dated,&#32;finance) To overvalue (securities), especially through deceptive accounting.",
                    "(<i>intransitive</i>) To fill with or secrete water or similar liquid.",
                    "(<i>transitive</i>) To wet and calender, as cloth, so as to impart to it a lustrous appearance in wavy lines; to diversify with wavelike lines.",
                ],
            },
            [],
        ),
        (
            "word",
            ["/weːd/", "/wøːd/", "/wəɹd/", "/wɛːd/", "/wɜɹd/", "/wɜːd/", "/wʌrd/"],
            [],
            [
                "From Middle English <i>word</i>, from Old English <i>word</i>, from Proto-West Germanic <i>&#42;word</i>, from Proto-Germanic <i>&#42;wurdą</i>, from Proto-Indo-European <i>&#42;wr̥dʰh₁om</i>. Doublet of <i>verb</i> and <i>verve</i>; further related to <i>vrata</i>.",
                "Variant of <i>worth</i> (“to become, turn into, grow, get”), from Middle English <i>worthen</i>, from Old English <i>weorþan</i> (“to turn into, become, grow”), from Proto-West Germanic <i>&#42;werþan</i>, from Proto-Germanic <i>&#42;werþaną</i> (“to turn, turn into, become”). More at worth §\xa0Verb.",
            ],
            {
                "Interjection": [
                    '(<i>slang</i>) Truth, indeed, that is the truth! The shortened form of the statement "My word is my bond."',
                    "(slang,&#32;emphatic,&#32;stereotypically&#32;African-American Vernacular) An abbreviated form of <i>word up</i>&#59; a statement of the acknowledgment of fact with a hint of nonchalant approval.",
                ],
                "Noun": [
                    "(<i>semantics</i>) The smallest unit of language that has a particular meaning and can be expressed by itself; the smallest discrete, meaningful unit of language. (contrast <i>morpheme</i>.)",
                    (
                        "The smallest discrete unit of spoken language with a particular meaning, composed of one or more phonemes and one or more morphemes",
                        "The smallest discrete unit of written language with a particular meaning, composed of one or more letters or symbols and one or more morphemes",
                        "A discrete, meaningful unit of language approved by an authority or native speaker (<i>compare non-word</i>).",
                    ),
                    "Something like such a unit of language:",
                    (
                        "A sequence of letters, characters, or sounds, considered as a discrete entity, though it does not necessarily belong to a language or have a meaning.",
                        "(<i>telegraphy</i>) A unit of text equivalent to five characters and one space. &lsqb;from 19th c.&rsqb;",
                        "(<i>computing</i>) A fixed-size group of bits handled as a unit by a machine and which can be stored in or retrieved from a typical register (so that it has the same size as such a register). &lsqb;from 20th c.&rsqb;",
                        "(<i>computing</i>) With regards to Intel or Intel-compatible hardware and/or in the context of Windows programming, a group of exactly 16 bits regardless of the actual processor capabilities; a fossilized unit referring to the small word size of historical CPUs. &lsqb;from 20th c.&rsqb;",
                        "(<i>computer science</i>) A finite string that is not a command or operator. &lsqb;from 20th c.&rsqb;",
                        "(<i>group theory</i>) A group element, expressed as a product of group elements.",
                    ),
                    "The fact or act of speaking, as opposed to taking action. &lsqb;from 9th c&rsqb;.",
                    "(<i>now&#32;rare&#32;outside certain phrases</i>) Something that someone said; a comment, utterance; speech. &lsqb;from 10th c.&rsqb;",
                    "(<i>obsolete&#32;outside certain phrases</i>) A watchword or rallying cry, a verbal signal (even when consisting of multiple words).",
                    "(<i>obsolete</i>) A proverb or motto.",
                    "(<i>uncountable</i>) News; tidings. &lsqb;from 10th c.&rsqb;",
                    "An order; a request or instruction; an expression of will. &lsqb;from 10th c.&rsqb;",
                    "A promise; an oath or guarantee. &lsqb;from 10th c.&rsqb;",
                    "A brief discussion or conversation. &lsqb;from 15th c.&rsqb;",
                    "(<i>meiosis</i>) A minor reprimand.",
                    "(<i>in the plural</i>) <i>See</i> <b>words</b>.",
                    "(theology,&#32;sometimes <b>Word</b>) Communication from God; the message of the Christian gospel; the Bible, Scripture. &lsqb;from 10th c.&rsqb;",
                    "(theology,&#32;sometimes <b>Word</b>) Logos, Christ. &lsqb;from 8th c.&rsqb;",
                ],
                "Verb": [
                    "(<i>transitive</i>) To say or write (something) using particular words; to phrase (something).",
                    "(transitive,&#32;obsolete) To flatter with words, to cajole.",
                    "(<i>transitive</i>) To ply or overpower with words.",
                    "(transitive,&#32;rare) To conjure with a word.",
                    "(intransitive,&#32;archaic) To speak, to use words; to converse, to discourse.",
                    "Alternative form of <i>worth</i> (“to become”).",
                ],
            },
            [],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    genders: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "en")
    details = parse_word(word, code, "en", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
