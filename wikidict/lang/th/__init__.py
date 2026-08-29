"""Thai language."""

random_word_url = (
    "https://th.wiktionary.org/wiki/%E0%B8%9E%E0%B8%B4%E0%B9%80%E0%B8%A8%E0%B8%A9:%E0%B8%AA%E0%B8%B8%E0%B9%88%E0%B8%A1"
)

module_trans = "มอดูล"
template_trans = "แม่แบบ"

float_separator = ","
thousands_separator = " "

section_sublevels = (3, 4)
head_sections = (
    "ภาษาไทย",  # Thai
    "ภาษาร่วม",  # Translingual
)
etyl_section = ("รากศัพท์", *[f"รากศัพท์ {idx}" for idx in range(1, 10)])
sections = (
    *etyl_section,
    # https://th.wiktionary.org/w/index.php?title=%E0%B8%A1%E0%B8%AD%E0%B8%94%E0%B8%B9%E0%B8%A5:headword/data&oldid=5757802
    "คำย่อ",  # abbreviations
    "อักษรย่อรวมพยางค์",  # acronyms
    "คำคุณศัพท์",  # adjectives
    "คำกริยาวิเศษณ์",  # adverbs
    "หน่วยคำเติม",  # affixes
    "คำกำกับนาม",  # articles
    "หน่วยคำเติมคร่อม",  # circumfixes
    "คำลักษณนาม",  # classifiers
    "ชมาโว",  # cmavo
    "ชเมเน",  # cmene
    "คำสันธาน",  # conjunctions
    "คำลักษณนาม",  # counters = classifiers
    "ตัวกำหนด",  # determiners
    "ทวิอักษร",  # digraphs
    "ฟูฮิฝลา",  # fu'ivla
    "กิสมู",  # gismu
    # "อักษรจีน", # Han characters
    "ฮั้นถื่อ",  # Han tu
    "ฮันจา",  # hanja
    "ฮั่นจื้อ",  # hanzi
    "สำนวน",  # idioms
    "อาคม",  # infixes
    "อักษรย่อ",  # initialisms
    "เครื่องหมายซ้ำ",  # iteration marks
    "หน่วยคำเติมเชื่อม",  # interfixes
    "คำอุทาน",  # interjections
    "คานะ",  # kana
    "คันจิ",  # kanji
    # "ตัวอักษร", # letters
    "ตัวอักษรควบ",  # ligatures
    "ลุฌโว",  # lujvo
    "หน่วยคำ",  # morphemes
    "คำนาม",  # nouns
    "จำนวน",  # numbers
    "ตัวเลข",  # numeral symbols
    "เลข",  # numerals
    "คำอนุภาค",  # particles
    # "วลี", # phrases
    "คำปัจฉบท",  # postpositions
    "วลีปัจฉบท",  # postpositional phrases
    "อุปสรรค",  # prefixes
    "วลีบุพบท",  # prepositional phrases
    "คำบุพบท",  # prepositions
    "คำกริยาเติมหน้า",  # preverbs
    "คำสรรพนาม",  # pronouns
    "คำวิสามานยนาม",  # proper nouns
    "สุภาษิต",  # proverbs
    "เครื่องหมายวรรคตอน",  # punctuation marks
    "ราก",  # roots
    "ต้นเค้าศัพท์",  # stems
    "ปัจจัย",  # suffixes
    "พยางค์",  # syllables
    "สัญลักษณ์",  # symbols
    "คำกริยา",  # verbs
)
