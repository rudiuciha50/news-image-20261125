"""THE GLOBAL CHRONICLE - front page for Wednesday 25 November 2026.

Pure standard library: a 5x7 bitmap font, a small raster canvas and a PNG
writer, so the entry draws its own newspaper page instead of shipping one.
Run:  python3 main_source.py   (writes <MAKEFUN_OUTPUT_DIR or /output>/entry.png)
"""

import os
import struct
import sys
import zlib

W = H = 1024
MARGIN = 28

HEAD_SCALE = 3              # column headline type
HEAD_LEAD = 3 * 7 + 8       # baseline step for one headline line
DEK_SCALE = 2               # column standfirst type
DEK_LEAD = 2 * (7 + 4)      # 7 rows at scale 2, plus the leading draw_para uses
HEAD_LINES = 2              # a column headline never runs past two lines
DEK_LINES = 2               # nor a standfirst past two

PAPER = (252, 249, 242)
INK = (18, 18, 22)
GREY = (108, 104, 98)
FAINT = (206, 200, 188)
RULE = (32, 32, 36)
ACCENT = (150, 26, 33)
BAND = (238, 232, 219)

# --------------------------------------------------------------------------
# 5x7 bitmap font: one glyph per line, seven rows of five cells, '1' inked.
# --------------------------------------------------------------------------
FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "11111 00100 00100 00100 00100 00100 11111",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "a": "00000 00000 01110 00001 01111 10001 01111",
    "b": "10000 10000 11110 10001 10001 10001 11110",
    "c": "00000 00000 01111 10000 10000 10000 01111",
    "d": "00001 00001 01111 10001 10001 10001 01111",
    "e": "00000 00000 01110 10001 11111 10000 01110",
    "f": "00110 01001 01000 11100 01000 01000 01000",
    "g": "00000 00000 01111 10001 10001 01111 00001",
    "h": "10000 10000 11110 10001 10001 10001 10001",
    "i": "00100 00000 01100 00100 00100 00100 01110",
    "j": "00011 00000 00110 00010 00010 10010 01100",
    "k": "10000 10000 10010 10100 11000 10100 10010",
    "l": "01100 00100 00100 00100 00100 00100 01110",
    "m": "00000 00000 11110 10101 10101 10101 10101",
    "n": "00000 00000 11110 10001 10001 10001 10001",
    "o": "00000 00000 01110 10001 10001 10001 01110",
    "p": "00000 00000 11110 10001 10001 11110 10000",
    "q": "00000 00000 01111 10001 10001 01111 00001",
    "r": "00000 00000 10110 11001 10000 10000 10000",
    "s": "00000 00000 01111 10000 01110 00001 11110",
    "t": "01000 01000 11100 01000 01000 01001 00110",
    "u": "00000 00000 10001 10001 10001 10011 01101",
    "v": "00000 00000 10001 10001 10001 01010 00100",
    "w": "00000 00000 10001 10001 10101 10101 01010",
    "x": "00000 00000 10001 01010 00100 01010 10001",
    "y": "00000 10001 10001 10001 01111 00001 01110",
    "z": "00000 00000 11111 00010 00100 01000 11111",
    "0": "01110 10011 10101 10101 10101 11001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00110 01000 10000 11111",
    "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    ".": "00000 00000 00000 00000 00000 00110 00110",
    ",": "00000 00000 00000 00000 00100 00100 01000",
    ":": "00000 00110 00110 00000 00110 00110 00000",
    ";": "00000 00110 00110 00000 00110 00100 01000",
    "-": "00000 00000 00000 01110 00000 00000 00000",
    "'": "00100 00100 00000 00000 00000 00000 00000",
    '"': "01010 01010 00000 00000 00000 00000 00000",
    "/": "00001 00010 00010 00100 01000 01000 10000",
    "!": "00100 00100 00100 00100 00100 00000 00100",
    "?": "01110 10001 00001 00110 00100 00000 00100",
    "(": "00010 00100 01000 01000 01000 00100 00010",
    ")": "01000 00100 00010 00010 00010 00100 01000",
    "&": "01100 10010 10100 01000 10101 10010 01101",
    "+": "00000 00100 00100 11111 00100 00100 00000",
    "*": "00000 10101 01110 11111 01110 10101 00000",
    "%": "11001 11010 00010 00100 01000 01011 10011",
    " ": "00000 00000 00000 00000 00000 00000 00000",
    "\u00b7": "00000 00000 00110 00110 00000 00000 00000",
    "\u2014": "00000 00000 00000 11111 00000 00000 00000",
    "\u2019": "00100 00100 00000 00000 00000 00000 00000",
}
GLYPH_ROWS = 7
GLYPH_COLS = 5


class Canvas(object):
    """A flat RGB raster with the few primitives a page layout needs."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.buf = bytearray(bytes(background) * (width * height))

    def rect(self, x, y, w, h, colour):
        x0 = max(0, int(x))
        y0 = max(0, int(y))
        x1 = min(self.w, int(x + w))
        y1 = min(self.h, int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        run = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * self.w + x0) * 3
            self.buf[start:start + len(run)] = run

    def hline(self, x, y, length, thickness, colour):
        self.rect(x, y, length, thickness, colour)

    def vline(self, x, y, length, thickness, colour):
        self.rect(x, y, thickness, length, colour)

    def png(self, level=9):
        """Pack the raster as an 8-bit truecolour PNG, IDAT deflated once."""
        raw = bytearray()
        stride = self.w * 3
        for row in range(self.h):
            raw.append(0)                      # filter type 0: none
            raw += self.buf[row * stride:(row + 1) * stride]
        body = zlib.compress(bytes(raw), level)

        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data
                    + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

        header = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                + chunk(b"IDAT", body) + chunk(b"IEND", b""))


def rows_of(ch):
    """The glyph for one character; an unknown one draws blank, never as '?'."""
    return FONT.get(ch) or FONT.get(ch.upper()) or FONT[" "]


def text_width(text, scale):
    """Width of `text` at `scale`: glyph cells plus one cell of letter spacing."""
    return len(text) * GLYPH_COLS * scale + max(0, len(text) - 1) * scale


def draw_text(canvas, x, y, text, scale=1, colour=INK, tracking=1):
    cursor = x
    for ch in text:
        glyph = rows_of(ch).split()
        for r, row in enumerate(glyph):
            for c, cell in enumerate(row):
                if cell == "1":
                    canvas.rect(cursor + c * scale, y + r * scale, scale, scale, colour)
        cursor += (GLYPH_COLS + tracking) * scale
    return cursor


def fit_scale(text, width, want=2):
    """Largest scale up to `want` at which `text` fits inside `width` pixels."""
    scale = want
    while scale > 1 and text_width(text, scale) > width:
        scale -= 1
    return scale


def draw_centred(canvas, y, text, scale, colour=INK, centre=None):
    cx = centre if centre is not None else canvas.w // 2
    draw_text(canvas, cx - text_width(text, scale) // 2, y, text, scale, colour)


def wrap(text, max_chars):
    """Greedy word wrap; never splits a word that fits on a line of its own."""
    lines, line = [], ""
    for word in text.split():
        if not line:
            line = word
        elif len(line) + 1 + len(word) <= max_chars:
            line += " " + word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_para(canvas, x, y, text, max_chars, scale=1, colour=INK, leading=4,
              max_lines=None):
    """Draw wrapped lines; returns the y below the last one."""
    lines = wrap(text, max_chars)
    if max_lines:
        lines = lines[:max_lines]
    step = GLYPH_ROWS * scale + leading * scale
    for i, line in enumerate(lines):
        draw_text(canvas, x, y + i * step, line, scale, colour)
    return y + len(lines) * step


# --------------------------------------------------------------------------
# The page
# --------------------------------------------------------------------------
PAPER_NAME = "THE GLOBAL CHRONICLE"
DATELINE = "WEDNESDAY 25 NOVEMBER 2026"
EDITION = "WORLD EDITION"

LEAD_KICKER = "THE DAY IN ONE PAGE  \u00b7  WORLD AFFAIRS"
LEAD_HEAD = ["ENVOYS MEET AS WINTER", "PRESSES BOTH FRONTS"]
LEAD_DECK = ("Ceasefire talks in Geneva enter a third week as cold weather hardens the lines; the UN "
             "says its winter appeal is less than half funded.")

DAY_LINE = ("ALSO TODAY:  GENEVA  \u00b7  EU SANCTIONS  \u00b7  OIL  \u00b7  AI RULES  \u00b7  "
            "CLIMATE  \u00b7  DAVIS CUP")

SECTIONS = [
    ("DIPLOMACY", [
        ("GENEVA TALKS ENTER WEEK THREE",
         "Mediators say the outline of a truce is on the table; monitors remain the sticking point."),
        ("EU CLEARS A NEW SANCTIONS ROUND",
         "Shipping, insurers and the shadow tanker fleet are the target."),
    ]),
    ("EUROPE", [
        ("BERLIN AND PARIS POOL DEFENCE",
         "A joint fund would buy air defence, drones and ammunition."),
        ("STORMS CUT RAIL AND FERRY LINKS",
         "Gales ease and a calmer weekend is forecast."),
    ]),
    ("ECONOMY", [
        ("CENTRAL BANKS URGE SLOW CUTS",
         "Rate setters promise quarter-by-quarter moves, not a rush."),
        ("INFLATION EASES AS FREIGHT FALLS",
         "Food and shipping costs cool; services prices stay sticky."),
    ]),
    ("MARKETS & TECH", [
        ("OIL SLIPS ON RISING STOCKPILES",
         "Crude falls a third session as inventories build."),
        ("REGULATORS SET RULES FOR AI",
         "Frontier labs face audits, incident reports and energy data."),
    ]),
    ("WORLD", [
        ("TOKYO UNVEILS A STIMULUS PACKAGE",
         "Cash handouts and energy subsidies for households."),
        ("CLIMATE DEAL NEARS ON FINANCE",
         "Adaptation money rises; wording on fossil fuels stays soft."),
    ]),
    ("SPORT", [
        ("DAVIS CUP REACHES LAST FOUR",
         "Two ties turn on the doubles rubber."),
        ("LATE GOALS DECIDE IN EUROPE",
         "Comebacks and a red card on a group night."),
    ]),
]

BRIEFS = [
    ("MARKETS", "Stocks firm, gold near a record as traders price slower cuts."),
    ("HEALTH", "The widest measles outbreak in a decade spreads across three regions."),
    ("CULTURE", "A lost silent film turns up in a Buenos Aires archive and is restored."),
]

TICKER = ("ALSO INSIDE:  MARKETS  \u00b7  SCIENCE  \u00b7  CULTURE  \u00b7  OPINION  \u00b7  "
          "WEATHER MAP  \u00b7  OBITUARIES  \u00b7  CROSSWORD")


def build_page():
    """Compose the front page: masthead, dated strip, lead story, then columns."""
    canvas = Canvas(W, H, PAPER)

    # ---- masthead -------------------------------------------------------
    canvas.rect(0, 0, W, 12, INK)
    canvas.hline(0, 12, W, 4, ACCENT)
    draw_centred(canvas, 26, PAPER_NAME, 7, INK)
    canvas.hline(MARGIN, 82, W - 2 * MARGIN, 1, RULE)
    canvas.hline(MARGIN, 86, W - 2 * MARGIN, 3, RULE)

    # dateline strip: the day itself, set large, is the page's second voice
    canvas.rect(0, 92, W, 46, BAND)
    canvas.hline(0, 92, W, 1, RULE)
    canvas.hline(0, 137, W, 1, RULE)
    draw_text(canvas, MARGIN, 100, DATELINE, 4, INK)
    draw_text(canvas, W - MARGIN - text_width(EDITION, 1), 103, EDITION, 1, ACCENT)

    # ---- lead story -----------------------------------------------------
    y = 152
    draw_text(canvas, MARGIN, y, LEAD_KICKER, 2, ACCENT)
    canvas.hline(MARGIN + text_width(LEAD_KICKER, 2) + 12, y + 5,
                 W - 2 * MARGIN - text_width(LEAD_KICKER, 2) - 12, 2, ACCENT)
    y += 26
    for line in LEAD_HEAD:
        draw_text(canvas, MARGIN, y, line, 6, INK)
        y += GLYPH_ROWS * 6 + 8
    canvas.hline(MARGIN, y + 2, 300, 3, ACCENT)
    y += 18

    # the deck runs full width, then a band names the day's other leads, so a
    # reader who only glances at the page still gets the shape of the day
    y += 2
    y = draw_para(canvas, MARGIN, y, LEAD_DECK, 78, 2, (58, 56, 52), 6)

    band_y = y + 8
    canvas.rect(0, band_y, W, 28, BAND)
    canvas.hline(0, band_y, W, 1, RULE)
    canvas.hline(0, band_y + 27, W, 1, RULE)
    draw_text(canvas, MARGIN, band_y + 7, DAY_LINE, fit_scale(DAY_LINE, W - 2 * MARGIN), ACCENT)

    y = band_y + 40
    canvas.hline(MARGIN, y, W - 2 * MARGIN, 3, RULE)
    canvas.hline(MARGIN, y + 5, W - 2 * MARGIN, 1, RULE)

    # ---- three columns --------------------------------------------------
    top = y + 20
    bottom = 896
    gutter = 22
    col_w = (W - 2 * MARGIN - 2 * gutter) // 3
    inner = col_w - 10
    # a line of n characters at scale s is (n * (GLYPH_COLS + 1) - 1) * s wide
    chars = max(6, (inner // HEAD_SCALE + 1) // (GLYPH_COLS + 1))
    body_chars = max(8, (inner // DEK_SCALE + 1) // (GLYPH_COLS + 1))

    stories = [(name, list(group)) for name, group in SECTIONS]
    while True:
        plan, ends = plan_columns(stories, top, bottom, chars, body_chars)
        if max(ends) <= bottom or not any(plan):
            break
        # trim the biggest section rather than the last, so no section disappears
        order = sorted(range(len(stories)), key=lambda k: (-len(stories[k][1]), k))
        for idx in order:
            name, group = stories[idx]
            if len(group) > 1:
                stories[idx] = (name, group[:-1])
                break
        else:
            break

    for i, entries in enumerate(plan):
        x = MARGIN + i * (col_w + gutter)
        if i:
            rule_x = x - gutter // 2
            canvas.vline(rule_x, top, bottom - top, 1, GREY)
            canvas.vline(rule_x + 1, top, bottom - top, 1, FAINT)
        cursor = top
        for kind, head, dek in entries:
            if kind == "SEC":
                canvas.rect(x, cursor, col_w, 22, INK)
                draw_text(canvas, x + 7, cursor + 4, head, 2, PAPER)
                cursor += 28
                continue
            for line in wrap(head, chars)[:HEAD_LINES]:
                draw_text(canvas, x, cursor, line, HEAD_SCALE, INK)
                cursor += HEAD_LEAD
            cursor += 4
            if dek:
                cursor = draw_para(canvas, x, cursor, dek, body_chars, DEK_SCALE, GREY, 4,
                                   max_lines=DEK_LINES)
            canvas.hline(x, cursor + 3, col_w - 8, 1, FAINT)
            cursor += 9

    # ---- in brief -------------------------------------------------------
    by = 904
    canvas.rect(0, by - 10, W, 4, RULE)
    canvas.rect(MARGIN, by, 118, 24, ACCENT)
    draw_text(canvas, MARGIN + 7, by + 5, "IN BRIEF", 2, PAPER)
    bx = MARGIN + 130
    for label, brief in BRIEFS:
        draw_text(canvas, bx, by, label, 1, ACCENT)
        draw_para(canvas, bx, by + 12, brief, 22, 2, INK, 3, max_lines=2)
        bx += 288

    # ---- footer ---------------------------------------------------------
    canvas.rect(0, 960, W, 64, INK)
    draw_centred(canvas, 974, TICKER, 1, PAPER)
    draw_centred(canvas, 996, "COMPILED 25 NOVEMBER 2026  \u00b7  " + PAPER_NAME, 2, FAINT)
    return canvas, ends


def plan_columns(sections, top, bottom, chars, body_chars=None):
    """Measure the page and cut it into three balanced columns.

    Every item is measured with the line counts and leading the renderer uses,
    so the plan and the drawing cannot disagree; the cut lands on the pair of
    boundaries with the smallest spread, and never leaves a section heading
    stranded at the foot of a column.
    """
    body_chars = body_chars or chars

    def measure(item):
        if item[0] == "SEC":
            return 28
        used = len(wrap(item[1], chars)[:HEAD_LINES]) * HEAD_LEAD + 4
        if item[2]:
            used += len(wrap(item[2], body_chars)[:DEK_LINES]) * DEK_LEAD
        return used + 12

    def rebuild(groups):
        out = []
        for name, group in groups:
            if not group:
                continue
            out.append(("SEC", name, None))
            for head, dek in group:
                out.append(("STORY", head, dek))
        return out

    groups = [(n, list(g)) for n, g in sections]
    while True:
        items = rebuild(groups)
        heights = [measure(i) for i in items]
        if sum(heights) <= 3 * (bottom - top):
            break
        for idx in range(len(groups) - 1, -1, -1):
            if groups[idx][1]:
                groups[idx][1].pop()
                break
        else:
            break

    def legal_cut(i):
        # a column never opens on a story whose section heading closed the last
        return 0 < i < len(items) and not (items[i][0] == "STORY" and items[i - 1][0] == "SEC")

    cuts = [i for i in range(1, len(items)) if legal_cut(i)]
    best = None
    for a in cuts:
        for b in cuts:
            if b <= a:
                continue
            blocks = (sum(heights[:a]), sum(heights[a:b]), sum(heights[b:]))
            if max(blocks) > bottom - top:
                continue
            key = (max(blocks) - min(blocks), max(blocks))
            if best is None or key < best[0]:
                best = (key, a, b)
    if best is None:
        # nothing fits the heading rule: take the flattest split of any kind
        for a in range(1, len(items)):
            for b in range(a + 1, len(items)):
                blocks = (sum(heights[:a]), sum(heights[a:b]), sum(heights[b:]))
                key = (max(blocks) - min(blocks), max(blocks))
                if best is None or key < best[0]:
                    best = (key, a, b)
    boundaries = [best[1], best[2]] if best else [len(items)]

    plan, ends, cursor = [], [], 0
    for edge in boundaries + [len(items)]:
        plan.append(items[cursor:edge])
        ends.append(top + sum(heights[cursor:edge]))
        cursor = edge
    return plan, ends


def main():
    canvas, col_end = build_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        out_dir = "."
    path = os.path.join(out_dir, "entry.png")
    data = canvas.png()
    with open(path, "wb") as handle:
        handle.write(data)
    sys.stderr.write("wrote %s (%d bytes) columns end at %s\n" % (path, len(data), col_end))


if __name__ == "__main__":
    main()
