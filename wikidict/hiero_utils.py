import re

from .hiero import wh_files, wh_hiero, wh_phonemes, wh_prefabs


class HieroTokenizer:
    delimiters: list[str] = []
    tokenDelimiters: list[str] = []

    singleChars: list[str] = []

    text: str = ""
    blocks: list[list[str]] = []

    currentBlock: list[str]
    token: str = ""

    def __init__(self, text: str):
        self.text = text
        self.initStatic()

    def initStatic(self) -> None:
        self.delimiters = [" ", "-", "\t", "\n", "\r"]
        self.tokenDelimiters = ["*", ":", "(", ")"]
        self.singleChars = ["!"]

    # Split text into blocks, then split blocks into items
    def tokenize(self) -> list[list[str]]:
        self.blocks = []
        self.currentBlock = []
        self.token = ""

        # remove HTML comments
        text = re.sub(r"<!--(?:.+-->)?", "", self.text)

        for i in range(len(text)):
            char = text[i]
            if char in self.delimiters:
                self.newBlock()
            elif char in self.singleChars:
                self.singleCharBlock(char)
            elif char == ".":
                self.dot()
            elif char in self.tokenDelimiters:
                self.newToken(token=char)
            else:
                self.char(char)

        # flush stuff being processed
        self.newBlock()

        return self.blocks

    # Handles a block delimiter
    def newBlock(self) -> None:
        self.newToken()
        if self.currentBlock:
            self.blocks.append(self.currentBlock)
            self.currentBlock = []

    # Flushes current token, optionally adds another one
    # @param string|bool token token to add or false
    def newToken(self, *, token: str = "") -> None:
        if self.token:
            self.currentBlock.append(self.token)
            self.token = ""

        if token:
            self.currentBlock.append(token)

    # Adds a block consisting of one character
    # @param string char block character
    def singleCharBlock(self, char: str) -> None:
        self.newBlock()
        self.blocks.append([char])

    # Handles void blocks represented by dots
    def dot(self) -> None:
        if self.token == ".":
            self.token = ".."
            self.newBlock()
        else:
            self.newBlock()
            self.token = "."

    # Adds a miscellaneous character to current token
    # @param string char character to add
    def char(self, char: str) -> None:
        if self.token == ".":
            self.newBlock()
            self.token = char
        else:
            self.token += char


ERD_FACTOR = 2.5
DEFAULT_SCALE = -1
CARTOUCHE_WIDTH = int(2 * ERD_FACTOR)
IMAGE_MARGIN = int(1 * ERD_FACTOR)
MAX_HEIGHT = int(44 * ERD_FACTOR)
TD_STYLE = "padding: 0; text-align: center; vertical-align: middle; font-size:1em;"
TABLE_STYLE = "border: 0; border-spacing: 0; font-size:1em;"
TABLE_START = f'<table class="mw-hiero-table" style="{TABLE_STYLE}">'
MIRROR_STYLE = "-webkit-transform: scaleX( -1 ); -moz-transform: scaleX( -1 ); -ms-transform: scaleX( -1 ); -o-transform: scaleX( -1 ); transform: scaleX( -1 ); filter: FlipH; -ms-filter: 'FlipH';"


def isMirrored(glyph: str) -> bool:
    return glyph[-1] == "\\"


def extractCode(glyph: str) -> str:
    return re.sub("\\\\.*$", "", glyph)


def renderVoidBlock(width: int) -> str:
    return f'<table class="mw-hiero-table" style="width: {width}px; {TABLE_STYLE}"><tr><td style="{TD_STYLE}">&#160;</td></tr></table>'


def renderGlyphImage(glyph: str, height: int, margin: int, moreStyle: str) -> str:
    if glyph in wh_phonemes:
        code = wh_phonemes[glyph]
        filename = code
        title = f"{code} [{glyph}]" if re.match(r"/^[A-Za-z0-9]+$/", glyph) else glyph
    else:
        filename = title = glyph

    if filename not in wh_files:
        return glyph
    style = "" if margin == 0 else f"margin: {margin}px;"
    style += "border: 0; vertical-align: middle; width:auto;" + (f" {moreStyle}" if moreStyle else "")
    result = f'<img src="{wh_hiero[filename]}" style="{style}" title="{title}" alt="glyph"'
    if height > 0:
        result += f' height="{height}"'
    result += "/>"
    return result


def renderGlyph(glyph: str, *, height: int = -1) -> str:
    moreStyle = MIRROR_STYLE if isMirrored(glyph) else ""
    glyph = extractCode(glyph)
    if glyph == "..":
        return renderVoidBlock(MAX_HEIGHT)
    if glyph == ".":
        return renderVoidBlock(int(MAX_HEIGHT / 2))
    if glyph in ["<", ">"]:
        return renderGlyphImage(glyph, MAX_HEIGHT, 0, moreStyle)

    return renderGlyphImage(glyph, height, IMAGE_MARGIN, moreStyle)


# Resize a glyph
#
# @param string $item glyph code
# @param bool $is_cartouche true if glyph is inside a cartouche
# @param int $total total size of a group for multi-glyph block
# @return int size
def resizeGlyph(item: str, *, is_cartouche: bool = False, total: int = 0) -> int:
    item = extractCode(item)
    glyph = wh_phonemes.get(item, item)

    margin = 2 * IMAGE_MARGIN
    if is_cartouche:
        margin += 2 * CARTOUCHE_WIDTH

    if glyph in wh_files:
        height = int(margin + wh_files[glyph][1] * ERD_FACTOR)
        if total and total > MAX_HEIGHT:
            return int(height * MAX_HEIGHT / total) - margin
        elif total or height <= MAX_HEIGHT:
            return height - margin
        else:
            return int(MAX_HEIGHT * MAX_HEIGHT / height) - margin

    return MAX_HEIGHT - margin


def render_hiero(hiero: str, *, scale: float = 100, line: bool = False) -> str:
    """
    >>> render_hiero("F99")
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style=" border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">\\n<table class="mw-hiero-table" style="border: 0; border-spacing: 0; font-size:1em;"><tr>\\n<td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">F99</td></tr></table>\\n</td></tr></table>'
    >>> render_hiero("<-F35-X1-M18-U33-B7->")
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style=" border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;"...'
    >>> render_hiero("<-F35-X1-M18-U33-B7->!", scale=250, line=True)
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style="-ms-transform: scale(2.5,2.5); -webkit-transform: scale(2.5,2.5); -o-transform: scale(2.5,2.5); transform: scale(2.5,2.5); border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">\\n<hr />...'
    >>> render_hiero("anx-G5-zmA:tA:tA-nbty-zmA:tA:tA-sw:t-bit:t-<-zA-ra:.-mn:n-T:w-Htp:t*p->-anx-D:t:N17-!")
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style=" border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">\\n<table class="mw-hiero-table" style="border: 0; border-spacing: 0; font-size:1em;"><tr>\\n<td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;"><img src="data:image/gif;base64...'
    >>> render_hiero("-D:z-=A1 -..-Sm-m-D54:=V31A-=w-=A1 -r -b-i-!")
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style=" border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">\\n<table class="mw-hiero-table" style="border: 0; border-spacing: 0; font-size:1em;"><tr>\\n<td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;"><img src="data:image/gif;base64...'
    >>> render_hiero("-wr:r-S -ir:=n-=A1 -h:r-w-ra -Z1-Z1-Z1 -wa:a-Z1-wr-=k:=W-=A1 -!")
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style=" border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">\\n<table class="mw-hiero-table" style="border: 0; border-spacing: 0; font-size:1em;"><tr>\\n<td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;"><img src="data:image/gif;base64...'
    >>> render_hiero(".A1")
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style=" border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">\\n<table class="mw-hiero-table" style="border: 0; border-spacing: 0; font-size:1em;"><tr>\\n<td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;"><table class="mw-hiero-table"...'
    >>> render_hiero("Ca1a")
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style=" border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">\\n<table class="mw-hiero-table" style="border: 0; border-spacing: 0; font-size:1em;"><tr>\\n<td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;"><img src="data:image/gif;base64...'
    """

    html = ""

    if line:
        html += "<hr />\n"

    tokenizer = HieroTokenizer(hiero)
    blocks = tokenizer.tokenize()
    contentHtml = tableHtml = tableContentHtml = ""
    is_cartouche = False

    # ------------------------------------------------------------------------
    # Loop into all blocks
    for code in blocks:
        # simplest case, the block contain only 1 code . render
        if len(code) == 1:
            if code[0] == "!":
                # end of line
                tableHtml = f"</tr></table>{TABLE_START}<tr>\n"
                if line:
                    contentHtml += "<hr />\n"

            elif "<" in code[0]:
                # start cartouche
                contentHtml += f'<td style="{TD_STYLE}">{renderGlyph(code[0])}</td>'
                is_cartouche = True
                contentHtml += f'<td style="{TD_STYLE}">{TABLE_START}<tr><td class="mw-hiero-box" style="background: #000; height:{CARTOUCHE_WIDTH}px; {TD_STYLE}"></td></tr><tr><td style="{TD_STYLE}">{TABLE_START}<tr>'

            elif ">" in code[0]:
                # end cartouche
                contentHtml += f'</tr></table></td></tr><tr><td class="mw-hiero-box" style="background: #000; height:{CARTOUCHE_WIDTH}px; {TD_STYLE}"></td></tr></table></td>'
                is_cartouche = False
                contentHtml += f'<td style="{TD_STYLE}">{renderGlyph(code[0])}</td>'

            elif code[0] != "":
                # assume it's a glyph or '..' or '.'
                contentHtml += (
                    f'<td style="{TD_STYLE}">'
                    + renderGlyph(code[0], height=resizeGlyph(code[0], is_cartouche=is_cartouche))
                    + "</td>"
                )

        # block contains more than 1 glyph
        else:
            # convert all codes into '&' to test prefabs glyph
            prefabs = "".join("&" if re.search("[*:!()]", t[0]) else t for t in code)

            # test if block exists in the prefabs list
            if prefabs in wh_prefabs:
                contentHtml += (
                    f'<td style="{TD_STYLE}">'
                    + renderGlyph(prefabs, height=resizeGlyph(prefabs, is_cartouche=is_cartouche))
                    + "</td>"
                )

            # block must be manually computed
            else:
                # get block total height
                line_max = 0
                total = 0
                height = 0

                for t in code:
                    if t == "*":
                        line_max = max(line_max, height)
                    elif t == ":":
                        line_max = max(line_max, height)
                        total += line_max
                        line_max = 0
                    else:
                        glyph = wh_phonemes.get(t, t)
                        if glyph in wh_files:
                            height = int(2 + wh_files[glyph][1] * ERD_FACTOR)

                line_max = max(line_max, height)

                total += line_max

                # render all glyph into the block
                block = ""
                for t in code:
                    if t == ":":
                        block += "<br />"
                    elif t == "*":
                        block += " "
                    else:
                        # resize the glyph according to the block total height
                        block += renderGlyph(t, height=resizeGlyph(t, is_cartouche=is_cartouche, total=total))

                contentHtml += f'<td style="{TD_STYLE}">{block}</td>'

            contentHtml += "\n"

        if len(contentHtml) > 0:
            tableContentHtml += tableHtml + contentHtml
            contentHtml = tableHtml = ""

    if len(tableContentHtml) > 0:
        html += f"{TABLE_START}<tr>\n{tableContentHtml}</tr></table>"

    style = ""
    if scale != 100:
        ratio = scale / 100
        style = f"-ms-transform: scale({ratio},{ratio}); -webkit-transform: scale({ratio},{ratio}); -o-transform: scale({ratio},{ratio}); transform: scale({ratio},{ratio});"

    return f'<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style="{style} {TABLE_STYLE}"><tr><td style="{TD_STYLE}">\n{html}\n</td></tr></table>'
