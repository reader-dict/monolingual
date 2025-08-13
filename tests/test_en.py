from collections.abc import Callable

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "ab",
            ["/æb/"],
            [],
            [
                "Abbreviation of <b>abscess</b>.",
                "From the spelling books and the fact that it was the first of the letter combinations.",
            ],
            {
                "Adverb": ["<i>Abbreviation of</i> <b>about</b>"],
                "Noun": [
                    "<i>(informal)</i> <i>Clipping of</i> <b>abdominal muscle</b> <small>[Mid 20<sup>th</sup> century.]</small>",
                    "<i>(slang)</i> An abscess caused by injecting an illegal drug, usually heroin.",
                    "<i>Abbreviation of</i> <b>abortion</b>",
                    "<i>(US)</i> The early stages of; the beginning process; the start.",
                ],
                "Preposition": ["<i>Abbreviation of</i> <b>about</b>"],
                "Symbol": ["(<i>international standards</i>) <i>ISO 639-1 language code for</i> <b>Abkhaz</b>."],
                "Verb": ["<i>(climbing, informal)</i> To abseil.", "<i>Abbreviation of</i> <b>abort</b>"],
            },
            [],
        ),
        (
            "Acanthis",
            [],
            ["f"],
            ["See Acanthis (mythology) on Wikipedia."],
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
                "Learned borrowing from Latin <i>cum</i> (“with”).",
                'Variant of <b>come</b>, attested (in the basic sense "come, move from further to nearer, arrive") since Old English. The sexual sense of <i>come</i> is attested since the 1650s. In this sense and spelling, attested from 1970s.',
            ],
            {
                "Adjective": ["<i>Clipping of</i> <b>cumulative</b>"],
                "Noun": [
                    "<i>(colloquial, often vulgar)</i> Semen.",
                    "<i>(colloquial, often vulgar)</i> Female ejaculatory discharge.",
                    "<i>(colloquial, often vulgar)</i> An ejaculation.",
                    "<i>Abbreviation of</i> <b>cubic metre</b>",
                ],
                "Preposition": [
                    "<i>Used in indicating a thing or person which has two or more roles, functions, or natures, or which has changed from one to another.</i>"
                ],
                "Verb": [
                    "<i>(slang, often vulgar)</i> To have an orgasm, to feel the sensation of an orgasm.",
                    "<i>(slang, often vulgar)</i> To ejaculate.",
                    "<i>Eye dialect spelling of</i> <b>come</b> (“move from further to nearer; arrive”)",
                ],
            },
            [],
        ),
        (
            "efficient",
            ["/əˈfɪʃənt/", "/ɪˈfɪʃənt/"],
            [],
            [
                "1398, “making,” from Old French, from Latin <i>efficientem</i>, nominative <i>efficiēns</i>, participle of <i>efficere</i> (“work out, accomplish”) (see <b>effect</b>). Meaning “productive, skilled” is from 1787. <i>Efficiency apartment</i> is first recorded 1930, American English."
            ],
            {
                "Adjective": [
                    "making good, thorough, or careful use of resources; not consuming extra. Especially, making good use of time or energy",
                    "expressing the proportion of consumed energy that was successfully used in a process; the ratio of useful output to total input",
                    "causing effects, producing results; bringing into being; initiating change (rare except in philosophical and legal expression <i>efficient cause</i> = causative factor or agent)",
                    "<i>(proscribed, old use)</i> effective, efficacious",
                ],
                "Noun": ["<i>(obsolete)</i> a cause; something that causes an effect"],
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
                "From <i>it</i>&nbsp;+&nbsp;<i>-’s</i> (possessive marker).",
            ],
            {
                "Contraction": [
                    "<i>Contraction of</i> <b>it is</b>",
                    "<i>Contraction of</i> <b>it has</b>",
                    "<i>Contraction of</i> <b>it was</b>",
                    "<i>(dialectal)</i> There's, there is; there're, there are.",
                ],
                "Determiner": ["<i>Obsolete form of</i> <b>its</b>", "<i>Misspelling of</i> <b>its</b>"],
            },
            [],
        ),
        (
            "Mars",
            ["/maɹs/", "/mɑ˞s/", "/ˈmɑɹz/", "/ˈmɑːz/"],
            [],
            [
                "From Middle English <i>Mars</i>, from Latin <i>Mārs</i> (“god of war”), from older Latin (older than 75 <small>B.C.E.</small>) <i>Māvors</i>.",
                "After Franklin Clarence Mars, who founded the company that produces these chocolate bars. His surname is possibly a variant of <b>Marrs</b>, itself from <b>Marr</b> with post-medieval excrescent <i>-s</i>.",
                "From Ukrainian <i>Марс</i>.",
            ],
            {
                "Noun": [
                    "<i>(heraldry, rare)</i> Gules (red), in the postmedieval practice of blazoning the tinctures of certain sovereigns' (especially British monarchs') coats as planets.",
                    "<i>(obsolete, alchemy, chemistry)</i> Iron.",
                    "<i>Alternative form of</i> <b>Mas</b>",
                ],
                "Proper Noun": [
                    "<i>(astronomy)</i> The fourth planet in the solar system. Symbol: <b>♂</b>",
                    "<i>(Roman mythology)</i> The Roman god of war.",
                    "<i>(poetic)</i> War; a personification of war.",
                    "<i>Short for</i> <b>Mars bar</b>, a brand of chocolate bar with caramel and nougat filling.",
                    "A village in Semenivka, Novhorod-Siverskyi, Chernihiv, Ukraine",
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
                "From Middle French <i>portemanteau</i> (“coat stand”), from <i>porte</i> (“carries”, third-person singular present indicative of <i>porter</i> (“to carry”))&nbsp;+&nbsp;<i>manteau</i> (“coat”).",
                "First used by Lewis Carroll in <i>Through the Looking-Glass</i> to describe the words he coined in “Jabberwocky”.",
            ],
            {
                "Adjective": [
                    "<i>(attributive, linguistics)</i> Made by combining two (or more) words, stories, etc., in the manner of a linguistic portmanteau."
                ],
                "Noun": [
                    "A large travelling case usually made of leather, and opening into two equal sections.",
                    "<i>(Australia, dated)</i> A schoolbag.",
                    "<i>(archaic)</i> A hook on which to hang clothing.",
                    "<i>(linguistics)</i> A word formed by putting two words together and thereby their meaning e.g. shrinkflation.",
                    "A portmanteau film.",
                ],
                "Verb": ["<i>(transitive)</i> To create a portmanteau word."],
            },
            [],
        ),
        (
            "someone",
            ["/ˈsʌmwʌn/"],
            [],
            [
                "From Middle English <i>sum on</i>, <i>sum one</i>, <i>sum oon</i>, equivalent to <i>some</i>&nbsp;+&nbsp;<i>one</i>.",
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
            [
                "From Middle English <i>scourge</i> (“a lash, whip, scourge; affliction, calamity; person who causes affliction or calamity; shoot of a vine”), and then either:",
                "From Middle English <i>scourgen</i> (“to whip, scourge; to afflict; to punish”), and then either:",
            ],
            {
                "Noun": [
                    "<i>(weaponry, chiefly historical)</i> A whip, often made of leather and having multiple tails; a lash.",
                    "<i>(figurative)</i>",
                    (
                        "A person or thing regarded as an agent of divine punishment.",
                        "A source of persistent (and often widespread) pain and suffering or trouble, such as a cruel ruler, disease, pestilence, or war.",
                    ),
                ],
                "Verb": [
                    "To strike (a person, an animal, etc.) with a scourge <i>(noun )</i> or whip; to flog, to whip.",
                    "To drive, or force (a person, an animal, etc.) to move, with or as if with a scourge or whip.",
                    "<i>(figurative)</i>",
                    (
                        "To punish (a person, an animal, etc.); to chastise.",
                        "To cause (someone or something) persistent (and often widespread) pain and suffering or trouble; to afflict, to torment.",
                        "<i>(Scotland, agriculture)</i> Of a crop or a farmer: to deplete the fertility of (land or soil).",
                    ),
                ],
            },
            [],
        ),
        (
            "the",
            ["/ði/", "/ðə/", "/ðɪ/", "/ˈðiː/", "/ˈðʌ/"],
            [],
            [
                "From Middle English <i>þe</i>, from Old English <i>þē</i> <i>m</i> (“the, that”, demonstrative pronoun), a late variant of <i>sē</i>, the <i>s-</i> (which occurred in the masculine and feminine nominative singular only) having been replaced by the <i>þ-</i> from the oblique stem.",
                "Originally neutral nominative, in Middle English it superseded all previous Old English nominative forms (<i>sē</i> <i>m</i>, <i>sēo</i> <i>f</i>, <i>þæt</i> <i>n</i>, <i>þā</i> <i>pl</i>); <i>sē</i> is from Proto-West Germanic <i>*siz</i>, from Proto-Germanic <i>*sa</i>, ultimately from Proto-Indo-European <i>*só</i>.",
                "Cognate with Saterland Frisian <i>die</i> (“the”), West Frisian <i>de</i> (“the”), Dutch <i>de</i> (“the”), German Low German <i>de</i> (“the”), German <i>der</i> (“the”), Danish <i>de</i> (“the”), Swedish <i>de</i> (“the”), Icelandic <i>sá</i> (“that”) within Germanic and with Sanskrit <i>स</i> (<i>sá</i>, “the, that”), Ancient Greek <i>ὁ</i> (“the”), Tocharian B <i>se</i> (“this”) among other Indo-European languages.",
                'From Middle English <i>the</i>, <i>thy</i>, <i>thi</i>, from Old English <i>þē̆</i>, probably a neuter instrumental form ("by that, thereby")—alongside the more common <i>þȳ</i> and <i>þon</i>—of the demonstrative pronoun <i>sē</i> ("that"). Compare Dutch <i>des <i>te</i></i> ("the, the more"), German <i>des<i>to</i></i> ("the, all the more"), Norwegian <i>for<i>di</i></i> and Norwegian <i>av di</i> ("because"), Icelandic <i>því</i> (“the; because”), Faroese <i>tí</i>, Swedish <i>ty</i>.',
            ],
            {
                "Adverb": [
                    "<i>With a comparative or with <b>more</b> and a verb phrase, establishes a correlation with one or more other such comparatives.</i>",
                    "<i>With a comparative, and often with <b>for it</b>, indicates a result more like said comparative. This can be negated with <b>none</b>.</i>",
                    "<i>(with a superlative adjective)</i> Beyond all others.",
                ],
                "Article": [
                    "<i>Used before a noun phrase, including a simple noun</i>",
                    (
                        "<i>The definite grammatical article that implies necessarily that the noun phrase it immediately precedes is definitely identifiable</i>",
                        (
                            "<i>because it has already been mentioned, is to be completely specified in the same sentence, or very shortly thereafter.</i> <small>[from 10th c.]</small>",
                            "<i>because it is presumed to be definitely known in context or from shared knowledge</i>",
                        ),
                        "<i>When stressed, indicates that it describes something which is considered to be best or exclusively worthy of attention.</i> <small>[from 18th c.]</small>",
                        "<i>Used before a noun phrase beginning with superlative or comparative adjective or an ordinal number, indicating that the noun refers to a single item.</i>",
                        "<i>Introducing a singular term to be taken generically: preceding a name of something standing for a whole class.</i> <small>[from 9th c.]</small>",
                        "<i>Used with the plural of a surname to indicate the entire family.</i>",
                    ),
                    "<i>Used with an adjective</i>",
                    (
                        "<i>Added to a superlative or an ordinal number to make it into a substantive.</i> <small>[from 9th c.]</small>",
                        "<i>Used before an adjective, indicating all things (especially persons) described by that adjective.</i> <small>[from 9th c.]</small>",
                        "<i>Used before a demonym to refer to people of a given country collectively.</i>",
                    ),
                ],
                "Noun": ["A topology name."],
                "Preposition": ["For each; per."],
                "Pronoun": ["<i>Obsolete form of</i> <b>thee</b>"],
            },
            [],
        ),
        (
            "um",
            ["/ʌm/"],
            [],
            ["Onomatopoeic."],
            {
                "Interjection": [
                    "<i>Expression of hesitation, uncertainty or space filler in conversation</i>.",
                    "<i>(chiefly US)</i> <i>Dated spelling of</i> <b>mmm</b>",
                    "<i>(US)</i> <i>An expression to forcefully call attention to something wrong.</i>",
                    "<i>(UK, childish)</i> An expression of shocked disapproval used by a child who witnesses forbidden behavior.",
                ],
                "Particle": [
                    "<i>(dated, sometimes humorous, often offensive)</i> <i>An undifferentiated determiner or article; a miscellaneous linking word, or filler with nonspecific meaning; representation of broken English stereotypically or comically attributed to Native Americans.</i>"
                ],
                "Symbol": ["micrometer; variant of μm used when the character μ is unavailable"],
                "Verb": ["<i>(intransitive)</i> To make the <i>um</i> sound to express uncertainty or hesitancy."],
            },
            [],
        ),
        (
            "us",
            ["/əs/", "/əz/", "/ʊs/", "/ʌs/", "/ʌz/"],
            [],
            [
                "From Middle English <i>us</i>, from Old English <i>ūs</i> (“us”, dative personal pronoun), from Proto-Germanic <i>*uns</i> (“us”), from Proto-Indo-European <i>*ne-</i>, <i>*nō-</i>, <i>*n-ge-</i>, <i>*n̥smé</i> (“us”). The compensatory lengthening was lost in Middle English due to the word being unstressed while being used. Cognate with Saterland Frisian <i>uus</i> (“us”), West Frisian <i>us</i>, <i>ús</i> (“us”), Low German <i>us</i> (“us”), Dutch <i>ons</i> (“us”), German <i>uns</i> (“us”), Danish <i>os</i> (“us”), Latin <i>nōs</i> (“we, us”).",
                "Derived from the similarity between the letter u and the Greek letter µ.",
            ],
            {
                "Determiner": ["The speakers/writers, or the speaker/writer and at least one other person."],
                "Noun": ["<i>(rare)</i> <i>Alternative form of</i> <b>u's</b>."],
                "Pronoun": [
                    "<i>(personal)</i> Me and at least one other person; the objective case of <b>we</b>.",
                    "<i>(Commonwealth, colloquial, chiefly with <b>give</b>)</i> Me.",
                    "<i>(Northern England)</i> Our.",
                    "<i>(Northumbria)</i> Me (in all contexts).",
                ],
                "Symbol": ["<i>Alternative spelling of</i> <b>µs</b>: microsecond"],
            },
            [],
        ),
        (
            "water",
            [
                "/ˈwoːtə/",
                "/ˈwætə/",
                "/ˈwɑtəɹ/",
                "/ˈwɒtə/",
                "/ˈwɒtəɹ/",
                "/ˈwɔtə/",
                "/ˈwɔtər/",
                "/ˈwɔtəɹ/",
                "/ˈwɔɹtəɹ/",
                "/ˈwɔːtə/",
                "/ˈwɔːtəɹ/",
                "/ˈwʊtəɹ/",
            ],
            [],
            [
                "From Middle English <i>water</i>, from Old English <i>wæter</i> (“water”), from Proto-West Germanic <i>*watar</i>, from Proto-Germanic <i>*watōr</i> (“water”), from Proto-Indo-European <i>*wódr̥</i> (“water”).",
                "Cognate with cf, North Frisian <i>weeter</i> (“water”), Saterland Frisian <i>Woater</i> (“water”), West Frisian <i>wetter</i> (“water”), Dutch <i>water</i> (“water”), Low German <i>Water</i> (“water”), German <i>Wasser</i>, Old Norse <i>vatn</i> (Swedish <i>vatten</i> (“water”), Danish <i>vand</i> (“water”), Norwegian Bokmål <i>vann</i> (“water”), Norwegian Nynorsk and Icelandic <i>vatn</i> (“water”), Old Irish <i>coin fodorne</i> (“otters”, literally “water-dogs”), Latin <i>unda</i> (“wave”), Lithuanian <i>vanduõ</i> (“water”), Russian <i>вода́</i> (<i>vodá</i>, “water”), Albanian <i>ujë</i> (“water”), Ancient Greek <i>ὕδωρ</i> (“water”), Armenian <i>գետ</i> (“river”), Sanskrit <i>उदन्</i> (<i>udán</i>, “wave, water”), Hittite <i>𒉿𒀀𒋻</i> (<i>wa-a-tar</i>).",
                "From Middle English <i>wateren</i>, from Old English <i>wæterian</i>, from Proto-Germanic <i>*watrōną</i>, <i>*watrijaną</i>, from Proto-Germanic <i>*watōr</i> (“water”), from Proto-Indo-European <i>*wódr̥</i> (“water”).",
                "Cognate with Scots <i>watter</i> (“water”), Saterland Frisian <i>woaterje</i> (“to water”), West Frisian <i>wetterje</i> (“to water”), Dutch <i>wateren</i> (“to water”), German Low German <i>watern</i> (“to water”), German <i>wässern</i> (“to water”), Danish <i>vande</i> (“to water”), Swedish <i>vattna</i> (“to water”), Icelandic <i>vatna</i> (“to water”).",
            ],
            {
                "Noun": [
                    "<i>(uncountable)</i> A substance (of molecular formula H<sub>2</sub>O) found at room temperature and pressure as a clear liquid; it is present naturally as rain, and found in rivers, lakes and seas; its solid form is ice and its gaseous form is steam.",
                    (
                        "<i>(uncountable, in particular)</i> The liquid form of this substance: liquid H<sub>2</sub>O.",
                        "<i>(countable)</i> A serving of liquid water.",
                    ),
                    "<i>(alchemy, philosophy)</i> The aforementioned liquid, considered one of the Classical elements or basic elements of alchemy.",
                    "<i>(uncountable or in the plural)</i> Water in a body; an area of open water.",
                    "<i>(poetic, archaic or dialectal)</i> A body of water, almost always a river, sometimes a lake or reservoir, especially in the names given to such bodies.",
                    "A combination of water and other substance(s).",
                    (
                        "<i>(sometimes countable)</i> Mineral water.",
                        "<i>(countable, often in the plural)</i> Spa water.",
                        "<i>(pharmacy)</i> A solution in water of a gaseous or readily volatile substance.",
                        "Urine. <small>[from 15th c.]</small>",
                        "Amniotic fluid or the amniotic sac containing it. (<i>Used only in the plural in the UK but often also in the singular in North America.</i>)",
                        "<i>(colloquial, medicine)</i> Fluids in the body, especially when causing swelling.",
                    ),
                    "<i>(business, often attributive)</i> The water supply, as a service or utility.",
                    "<i>(figuratively, in the plural or in the singular)</i> A state of affairs; conditions; usually with an adjective indicating an adverse condition.",
                    "<i>(colloquial, figuratively)</i> A person's intuition.",
                    "<i>(uncountable, dated, finance)</i> Excess valuation of securities.",
                    "A particular quality or appearance suggestive of water:",
                    (
                        "The limpidity and lustre of a precious stone, especially a diamond.",
                        "A wavy, lustrous pattern or decoration such as is imparted to linen, silk, metals, etc.",
                    ),
                ],
                "Verb": [
                    "<i>(transitive)</i> To pour water into the soil surrounding (plants).",
                    "<i>(transitive)</i> To wet or supply with water; to moisten; to overflow with water; to irrigate.",
                    "<i>(transitive)</i> To provide (animals) with water for drinking.",
                    "<i>(intransitive)</i> To get or take in water.",
                    "<i>(transitive, colloquial)</i> To urinate onto.",
                    "<i>(transitive)</i> To dilute.",
                    "<i>(transitive, dated, finance)</i> To overvalue (securities), especially through deceptive accounting.",
                    "<i>(intransitive)</i> To fill with or secrete water or similar liquid.",
                    "<i>(transitive)</i> To wet and calender, as cloth, so as to impart to it a lustrous appearance in wavy lines; to diversify with wavelike lines.",
                ],
            },
            [],
        ),
        (
            "word",
            ["/wəɹd/", "/wɜːd/", "/wɝd/"],
            [],
            [
                "From Middle English <i>word</i>, from Old English <i>word</i>, from Proto-West Germanic <i>*word</i>, from Proto-Germanic <i>*wurdą</i>, from Proto-Indo-European <i>*wr̥dʰh₁om</i>. Doublet of <i>verb</i> and <i>verve</i>; further related to <b>vrata</b>.",
                "Variant of <i>worth</i> (“to become, turn into, grow, get”), from Middle English <i>worthen</i>, from Old English <i>weorþan</i> (“to turn into, become, grow”), from Proto-West Germanic <i>*werþan</i>, from Proto-Germanic <i>*werþaną</i> (“to turn, turn into, become”). More at worth § Verb.",
            ],
            {
                "Interjection": [
                    '<i>(slang)</i> Truth, indeed, that is the truth! The shortened form of the statement "My word is my bond."',
                    "<i>(slang, emphatic, stereotypically, African-American Vernacular)</i> An abbreviated form of <b>word up</b>; a statement of the acknowledgment of fact with a hint of nonchalant approval.",
                ],
                "Noun": [
                    "<i>(semantics)</i> The smallest unit of language that has a particular meaning and can be expressed by itself; the smallest discrete, meaningful unit of language. (<i>contrast <i>morpheme</i>.</i>)",
                    (
                        "The smallest discrete unit of spoken language with a particular meaning, composed of one or more phonemes and one or more morphemes",
                        "The smallest discrete unit of written language with a particular meaning, composed of one or more letters or symbols and one or more morphemes",
                        "A discrete, meaningful unit of language approved by an authority or native speaker (<i>compare non-word</i>).",
                    ),
                    "Something like such a unit of language:",
                    (
                        "A sequence of letters, characters, or sounds, considered as a discrete entity, though it does not necessarily belong to a language or have a meaning.",
                        "<i>(telegraphy)</i> A unit of text equivalent to five characters and one space. <small>[from 19th c.]</small>",
                        "<i>(computing)</i> A fixed-size group of bits handled as a unit by a machine and which can be stored in or retrieved from a typical register (so that it has the same size as such a register). <small>[from 20th c.]</small>",
                        "<i>(computer science)</i> A finite string that is not a command or operator. <small>[from 20th or 21st c.]</small>",
                        "<i>(group theory)</i> A group element, expressed as a product of group elements.",
                    ),
                    "The fact or act of speaking, as opposed to taking action. <small>[from 9th c]</small>.",
                    "<i>(now rare outside certain phrases)</i> Something that someone said; a comment, utterance; speech. <small>[from 10th c.]</small>",
                    "<i>(obsolete outside certain phrases)</i> A watchword or rallying cry, a verbal signal (even when consisting of multiple words).",
                    "<i>(obsolete)</i> A proverb or motto.",
                    "<i>(uncountable)</i> News; tidings. <small>[from 10th c.]</small>",
                    "An order; a request or instruction; an expression of will. <small>[from 10th c.]</small>",
                    "A promise; an oath or guarantee. <small>[from 10th c.]</small>",
                    "A brief discussion or conversation. <small>[from 15th c.]</small>",
                    "<i>(meiosis)</i> A minor reprimand.",
                    "<i>(in the plural)</i> <i>See</i> <b>words</b>.",
                    "<i>(theology, sometimes <b>Word</b>)</i> Communication from God; the message of the Christian gospel; the Bible, Scripture. <small>[from 10th c.]</small>",
                    "<i>(theology, sometimes <b>Word</b>)</i> Logos, Christ. <small>[from 8th c.]</small>",
                ],
                "Verb": [
                    "<i>(transitive)</i> To say or write (something) using particular words; to phrase (something).",
                    "<i>(transitive, obsolete)</i> To flatter with words, to cajole.",
                    "<i>(transitive)</i> To ply or overpower with words.",
                    "<i>(transitive, rare)</i> To conjure with a word.",
                    "<i>(intransitive, archaic)</i> To speak, to use words; to converse, to discourse.",
                    "<i>Alternative form of</i> <b>worth</b> (“to become”).",
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
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants


@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{1|influenza}}", "Influenza"),
        ("{{abbr of|en|abortion}}", "<i>Abbreviation of</i> <b>abortion</b>"),
        ("{{abbreviation of|en|abortion}}", "<i>Abbreviation of</i> <b>abortion</b>"),
        ("{{alt case|en|angstrom}}", "<i>Alternative letter-case form of</i> <b>angstrom</b>"),
        ("{{alternative spelling of|en|µs}}", "<i>Alternative spelling of</i> <b>µs</b>"),
        ("{{ar-form|IV}}", "Form IV"),
        ("{{ar-form|IV|verb form}}", "verb form IV"),
        ("{{C.|20}}", "20th c."),
        ("{{C.|21|st}}", "21st c."),
        (
            "{{caret notation of|null}}",
            "<i>(computing) The ASCII control character</i> <b>null</b> <i>in caret notation</i>.",
        ),
        ("{{clipping of|en|yuppie}}", "<i>Clipping of</i> <b>yuppie</b>"),
        ("{{code|js|=(65535).toString(16) === 'ffff'}}", "<code>(65535).toString(16) === 'ffff'</code>"),
        ("{{color panel|E34234}}", "[RGB E34234]"),
        ("{{color panel|vermilion|E34234}}", "vermilion: [RGB E34234]"),
        ("{{defdate|from 15th c.}}", "<small>[from 15th c.]</small>"),
        ("{{eye dialect of|en|is}}", "<i>Eye dialect spelling of</i> <b>is</b>"),
        ("{{gloss|liquid H<sub>2</sub>O}}", "(liquid H<sub>2</sub>O)"),
        ("{{glossary|inflected}}", "inflected"),
        ("{{glossary|inflected|Inflected}}", "Inflected"),
        ("{{initialism of|en|Inuit Qaujimajatuqangit|nodot=1}}", "<i>Initialism of</i> <b>Inuit Qaujimajatuqangit</b>"),
        ("{{IPAfont|ʌ}}", "ʌ"),
        ("{{lit|eagle killer}}", "Literally, “eagle killer”"),
        ("{{mono|#!}}", '<span style="font-family:monospace">#!</span>'),
        ("{{monospace|#!}}", '<span style="font-family:monospace">#!</span>'),
        ("{{n-g|Definite grammatical}}", "<i>Definite grammatical</i>"),
        ("{{ngd|Definite grammatical}}", "<i>Definite grammatical</i>"),
        ("{{nobr|1=[ ...=C=C=C=... ]}}", '<span style="white-space:nowrap">[...=C=C=C=...</span>'),
        ("{{non-gloss definition|Definite grammatical}}", "<i>Definite grammatical</i>"),
        ("{{non-gloss definition|1=Definite grammatical}}", "<i>Definite grammatical</i>"),
        ("{{nowrap|1=[ ...=C=C=C=... ]}}", '<span style="white-space:nowrap">[...=C=C=C=...</span>'),
        ("{{q|formal|used only in the plural}}", "(<i>formal</i>, <i>used only in the plural</i>)"),
        ("{{qual|Used only in the plural in the UK}}", "(<i>Used only in the plural in the UK</i>)"),
        ("{{qualifier|Used only in the plural in the UK}}", "(<i>Used only in the plural in the UK</i>)"),
        ("{{sense|man of beastly nature}}", "(<i>man of beastly nature</i>) :"),
        ("{{smc|ah}}", "<span style='font-variant:small-caps'>ah</span>"),
        ("{{sub|KI}}", "<sub>KI</sub>"),
        ("{{sup|KI}}", "<sup>KI</sup>"),
        ("{{synonym of|en|drip tip}}", "<i>Synonym of</i> <b>drip tip</b>"),
        ("{{taxfmt|Gadus macrocephalus|species|ver=170710}}", "<i>Gadus macrocephalus</i>"),
        ("{{taxlink|Gadus macrocephalus|species|ver=170710}}", "<i>Gadus macrocephalus</i>"),
        ("{{uder|en|fro|jargon}}", "Old French <i>jargon</i>"),
    ],
)
def test_process_templates(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "en") == expected
