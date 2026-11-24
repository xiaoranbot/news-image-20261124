"""Draw the front page of THE WORLD TODAY for Tuesday 24 November 2026.

Pure standard library. Renders a 1024x1024 PNG newspaper front page:
Jensen Huang returns as Nvidia chief (NVDA +31%), the EU's 22nd sanctions
package, Ukraine sinking the Russian warship Merkury off Libya, the ICJ
ruling on Myanmar, Odesa in the dark, plus a briefs ticker.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Output is deterministic: two runs produce byte-identical PNGs.
"""

import math
import os
import struct
import zlib
from binascii import crc32

WIDTH = 1024
HEIGHT = 1024

CREAM = (244, 239, 228)
NAVY = (16, 24, 64)
NAVY_SOFT = (24, 36, 84)
INK = (26, 26, 26)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
GOLD_BRIGHT = (232, 184, 32)
GREEN = (34, 139, 34)
GREEN_DARK = (27, 94, 32)
TEAL = (42, 122, 120)
BLUE_EU = (0, 51, 153)
SKY = (168, 205, 230)
SEA = (16, 92, 99)
ORANGE = (232, 120, 24)
WHITE = (255, 255, 255)
GREY_LINE = (201, 196, 184)


# ---------------------------------------------------------------- PNG writer

def _png_chunk(kind, payload):
    """One PNG chunk: length, type, data, CRC."""
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(
        ">I", crc32(body) & 0xFFFFFFFF)


def encode_png(rgb, width, height):
    """Encode raw RGB bytes (row-major, no alpha) as a PNG file.

    Filter type 0 on every scanline and a fixed zlib level keep the
    output byte-for-byte identical across runs.
    """
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    compressed = zlib.compress(bytes(raw), 9)
    header = struct.pack(">8s", b"\x89PNG\r\n\x1a\n")
    ihdr = _png_chunk(b"IHDR", struct.pack(
        ">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    return header + ihdr + _png_chunk(b"IDAT", compressed) + _png_chunk(
        b"IEND", b"")


# ------------------------------------------------------------- bitmap font

# Hand-drawn 5x7 pixel glyphs. Each glyph is seven rows of five cells;
# '#' is ink, '.' is blank. Only the characters the page needs are here.
GLYPHS = {
    "A": (
        ".###.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "B": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#...#",
        "#...#",
        "####.",
    ),
    "C": (
        ".####",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        ".####",
    ),
    "D": (
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ),
    "E": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#####",
    ),
    "F": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "G": (
        ".####",
        "#....",
        "#....",
        "#.###",
        "#...#",
        "#...#",
        ".###.",
    ),
    "H": (
        "#...#",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "I": (
        ".###.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ),
    "J": (
        "..###",
        "...#.",
        "...#.",
        "...#.",
        "...#.",
        "#..#.",
        ".##..",
    ),
    "K": (
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "L": (
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ),
    "M": (
        "#...#",
        "##.##",
        "#.#.#",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
    ),
}

GLYPHS.update({
    "N": (
        "#...#",
        "##..#",
        "#.#.#",
        "#..##",
        "#...#",
        "#...#",
        "#...#",
    ),
    "O": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "P": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "Q": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    "R": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "S": (
        ".####",
        "#....",
        "#....",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    "T": (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "U": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "V": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
    ),
    "W": (
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#.#.#",
        "##.##",
        "#...#",
    ),
    "X": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
        "#...#",
    ),
    "Y": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "Z": (
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#####",
    ),
    "0": (
        ".###.",
        "#...#",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        ".###.",
    ),
    "1": (
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ),
    "2": (
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#####",
    ),
    "3": (
        "####.",
        "....#",
        "....#",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    "4": (
        "...#.",
        "..##.",
        ".#.#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ),
    "5": (
        "#####",
        "#....",
        "####.",
        "....#",
        "....#",
        "#...#",
        ".###.",
    ),
    "6": (
        ".###.",
        "#....",
        "#....",
        "####.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "7": (
        "#####",
        "....#",
        "...#.",
        "...#.",
        "..#..",
        "..#..",
        "..#..",
    ),
    "8": (
        ".###.",
        "#...#",
        "#...#",
        ".###.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "9": (
        ".###.",
        "#...#",
        "#...#",
        ".####",
        "....#",
        "....#",
        ".###.",
    ),
    ".": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".##..",
        ".##..",
    ),
    ",": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".##..",
        ".##..",
        ".#...",
    ),
    "-": (
        ".....",
        ".....",
        ".....",
        ".###.",
        ".....",
        ".....",
        ".....",
    ),
    "+": (
        ".....",
        "..#..",
        "..#..",
        ".###.",
        "..#..",
        "..#..",
        ".....",
    ),
    "%": (
        "##..#",
        "##.#.",
        "...#.",
        "..#..",
        ".#...",
        "#.##.",
        "#..##",
    ),
    ":": (
        ".....",
        ".##..",
        ".##..",
        ".....",
        ".##..",
        ".##..",
        ".....",
    ),
    "/": (
        "....#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#....",
    ),
    "(": (
        "...##",
        "..#..",
        ".#...",
        ".#...",
        ".#...",
        "..#..",
        "...##",
    ),
    ")": (
        "##...",
        "..#..",
        "...#.",
        "...#.",
        "...#.",
        "..#..",
        "##...",
    ),
    "'": (
        "..#..",
        "..#..",
        "..#..",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    "&": (
        ".###.",
        "#...#",
        "#.#..",
        ".#...",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    " ": (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
})

# ------------------------------------------------------------ canvas

CHAR_W = 6  # 5 glyph columns + 1 column of tracking, in font units


def text_width(text, scale):
    """Pixel width of a string at a given scale."""
    return len(text) * CHAR_W * scale - scale


class Page:
    """An RGB pixel buffer with small drawing helpers."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def put(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def disc(self, cx, cy, r, color):
        """Filled circle, centre (cx, cy), radius r."""
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=2):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = math.hypot(xx - cx, yy - cy)
                if r - thick <= d <= r:
                    self.put(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle via a scanline walk."""
        top = min(y0, y1, y2)
        bottom = max(y0, y1, y2)
        pts = [(x0, y0), (x1, y1), (x2, y2)]
        for yy in range(top, bottom + 1):
            xs = []
            for (ax, ay), (bx, by) in ((pts[0], pts[1]),
                                       (pts[1], pts[2]),
                                       (pts[2], pts[0])):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.put(xx, yy, color)

    def glyph(self, x, y, char, scale, color):
        rows = GLYPHS.get(char)
        if rows is None:
            return
        for ry, row in enumerate(rows):
            for rx, cell in enumerate(row):
                if cell == "#":
                    self.rect(x + rx * scale, y + ry * scale,
                              scale, scale, color)

    def text(self, x, y, string, scale, color):
        """Draw a string; returns the x just past its last glyph."""
        cx = x
        for char in string:
            self.glyph(cx, y, char, scale, color)
            cx += CHAR_W * scale
        return cx - scale

    def text_centered(self, cx, y, string, scale, color):
        x = cx - text_width(string, scale) // 2
        return self.text(x, y, string, scale, color)

    def text_right(self, right, y, string, scale, color):
        x = right - text_width(string, scale)
        return self.text(x, y, string, scale, color)

    def paragraph(self, x, y, string, scale, color, max_width, leading):
        """Word-wrap a paragraph; returns the y just past its last line."""
        words = string.split()
        lines = []
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if text_width(trial, scale) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        for row in lines:
            self.text(x, y, row, scale, color)
            y += leading
        return y


# ------------------------------------------------------------ masthead

def draw_masthead(page):
    page.rect(24, 24, 976, 88, NAVY)
    page.text(48, 48, "THE WORLD TODAY", 6, WHITE)
    page.text_right(976, 38, "TUESDAY", 3, GOLD_BRIGHT)
    page.text_right(976, 70, "24 NOVEMBER 2026", 3, WHITE)
    page.hline(24, 120, 976, RED, 6)


# ------------------------------------------------------------ top story

def draw_chip(page, x, y):
    """A green processor with pins, labelled NVDA, on the navy panel."""
    page.text(x, y, "THE CHIP GIANT", 2, GOLD_BRIGHT)
    bx, by, bw, bh = x, y + 34, 210, 130
    # pins around the package
    for i in range(5):
        page.rect(bx + 18 + i * 38, by - 10, 12, 10, CREAM)
        page.rect(bx + 18 + i * 38, by + bh, 12, 10, CREAM)
    for i in range(3):
        page.rect(bx - 10, by + 18 + i * 38, 10, 12, CREAM)
        page.rect(bx + bw, by + 18 + i * 38, 10, 12, CREAM)
    page.rect(bx, by, bw, bh, GREEN)
    page.rect(bx + 10, by + 10, bw - 20, bh - 20, GREEN_DARK)
    page.text_centered(bx + bw // 2, by + 44, "NVDA", 5, WHITE)
    page.text_centered(bx + bw // 2, by + 96, "NVIDIA", 2, CREAM)


def draw_bars(page, x, y):
    """Five rising bars for the share-price jump, tallest in gold."""
    heights = [26, 44, 62, 80, 100]
    colors = [TEAL, TEAL, GREEN, GREEN, GOLD_BRIGHT]
    for i, h in enumerate(heights):
        page.rect(x + i * 42, y + 100 - h, 30, h, colors[i])


def draw_top_story(page):
    top = 136
    bottom = 500
    # left: navy illustration panel
    page.rect(24, top, 476, bottom - top, NAVY)
    draw_chip(page, 84, top + 22)
    draw_bars(page, 84, top + 226)
    page.text(312, top + 262, "+31%", 6, GOLD_BRIGHT)
    page.text(316, top + 306, "IN ONE DAY", 2, CREAM)
    # right: headline column
    x = 524
    page.text(x, top + 6, "TECH - MARKETS", 2, RED)
    page.text(x, top + 34, "HUANG IS BACK", 5, INK)
    page.paragraph(x, top + 108, "NVIDIA CHIEF RETURNS AS SHARES SOAR 31%",
                   3, INK, 476, 34)
    page.paragraph(
        x, top + 196,
        "JENSEN HUANG IS BACK AS NVIDIA CHIEF AFTER AN INDEPENDENT "
        "INQUIRY CLEARED HIM. SHARES SOARED MORE THAN 31% IN A DAY. "
        "THE SENATE WILL QUESTION HIM ON DEC 3.",
        2, INK, 476, 22)
    page.rect(x, top + 316, 200, 34, GREEN)
    page.text_centered(x + 100, top + 326, "NVDA +31%", 2, WHITE)
    page.rect(x + 220, top + 316, 220, 34, NAVY)
    page.text_centered(x + 330, top + 326, "DEC 3 HEARING", 2, WHITE)
    page.hline(24, 514, 976, GREY_LINE, 2)


# ------------------------------------------------------------ middle row

def draw_eu_flag(page, x, y, w, h):
    """EU blue field, a ring of twelve gold stars, and a big 22."""
    page.rect(x, y, w, h, BLUE_EU)
    cx, cy = x + w // 2, y + h // 2
    for i in range(12):
        angle = -math.pi / 2 + i * math.pi / 6
        sx = cx + int(58 * math.cos(angle))
        sy = cy + int(42 * math.sin(angle))
        # five-point star, drawn as a small diamond cross
        page.disc(sx, sy, 4, GOLD_BRIGHT)
        page.rect(sx - 7, sy - 1, 14, 2, GOLD_BRIGHT)
        page.rect(sx - 1, sy - 7, 2, 14, GOLD_BRIGHT)
    page.text_centered(cx, cy - 18, "22", 5, GOLD_BRIGHT)


def draw_sea_battle(page, x, y, w, h):
    """Calm sky and sea, a warship under a red flag, shells bursting."""
    page.rect(x, y, w, h // 2, SKY)
    page.rect(x, y + h // 2, w, h - h // 2, SEA)
    page.disc(x + w - 52, y + 26, 16, (240, 214, 130))  # low sun
    # warship silhouette
    sx, sy = x + 96, y + h // 2 - 6
    page.rect(sx, sy - 34, 118, 34, INK)
    page.rect(sx + 44, sy - 52, 14, 18, INK)
    page.vline(sx + 50, sy - 74, 24, INK, 3)
    page.rect(sx + 52, sy - 74, 26, 14, RED)  # flag
    page.triangle(sx - 26, sy, sx, sy - 34, sx, sy, INK)
    # bursting shells to the right of the ship
    page.disc(sx + 168, sy - 46, 14, ORANGE)
    page.disc(sx + 190, sy - 30, 9, GOLD_BRIGHT)
    page.disc(sx + 158, sy - 18, 7, RED)
    page.disc(sx + 206, sy - 52, 5, (120, 120, 120))
    # wake lines
    for i, wy in enumerate((y + h - 30, y + h - 20, y + h - 10)):
        page.hline(x + 60 + i * 40, wy, w - 120 - i * 40, CREAM, 2)


def draw_middle_row(page):
    top = 528
    panel_h = 100
    left_x, right_x = 24, 524
    col_w = 476
    draw_eu_flag(page, left_x, top, col_w, panel_h)
    draw_sea_battle(page, right_x, top, col_w, panel_h)

    ty = top + panel_h + 10
    page.text(left_x, ty, "EUROPE", 2, RED)
    page.paragraph(left_x, ty + 24, "EU UNVEILS 22ND SANCTIONS PACKAGE",
                   3, INK, col_w, 28)
    page.paragraph(left_x, ty + 82,
                   "BRUSSELS TARGETS RUSSIAN BANKS, CRYPTO AND ATHLETES.",
                   2, INK, col_w, 18)

    page.text(right_x, ty, "UKRAINE", 2, RED)
    page.paragraph(right_x, ty + 24, "KYIV SAYS IT SANK RUSSIAN WARSHIP",
                   3, INK, col_w, 28)
    page.paragraph(right_x, ty + 82,
                   "DRONE SHIPS HIT THE MERKURY OFF THE LIBYAN COAST IN A "
                   "LONG-RANGE STRIKE.",
                   2, INK, col_w, 18)
    page.hline(24, 754, 976, GREY_LINE, 2)


# ------------------------------------------------------------ bottom row

def draw_scales(page, cx, cy, r):
    """Gold disc carrying a simple balance scale."""
    page.disc(cx, cy, r, GOLD)
    page.vline(cx, cy - r + 14, 2 * r - 30, INK, 4)
    page.disc(cx, cy - r + 14, 5, INK)
    page.hline(cx - 34, cy - r + 22, 68, INK, 4)
    # left pan
    page.vline(cx - 34, cy - r + 22, 22, INK, 2)
    page.triangle(cx - 48, cy - r + 44, cx - 20, cy - r + 44,
                  cx - 34, cy - r + 24, INK)
    # right pan
    page.vline(cx + 34, cy - r + 22, 22, INK, 2)
    page.triangle(cx + 20, cy - r + 44, cx + 48, cy - r + 44,
                  cx + 34, cy - r + 24, INK)
    page.rect(cx - 16, cy + r - 22, 32, 8, INK)


def draw_odesa_night(page, x, y, w, h):
    """Blacked-out port city: dark skyline, one orange moon, lit windows."""
    page.rect(x, y, w, h, NAVY)
    page.disc(x + w - 34, y + 26, 18, ORANGE)
    page.disc(x + w - 34, y + 26, 12, (240, 150, 60))
    buildings = [(0, 70, 34, 60), (38, 52, 30, 78), (72, 84, 36, 46),
                 (110, 62, 22, 68)]
    for bx, by, bw, bh in buildings:
        page.rect(x + bx, y + by, bw, bh, INK)
        for wy in range(by + 10, by + bh - 8, 16):
            for wx in range(bx + 7, bx + bw - 7, 12):
                if (wx + wy) % 24 == 7:
                    page.rect(x + wx, y + wy, 4, 5, GOLD_BRIGHT)


def draw_bottom_row(page):
    top = 770
    left_x, right_x = 24, 524
    col_w = 476

    draw_scales(page, left_x + 52, top + 66, 52)
    page.text(left_x + 122, top + 6, "THE HAGUE", 2, RED)
    page.paragraph(left_x + 122, top + 30,
                   "MYANMAR GUILTY OF ROHINGYA GENOCIDE",
                   3, INK, col_w - 122, 30)
    page.paragraph(left_x + 122, top + 96,
                   "THE WORLD COURT RULED MYANMAR COMMITTED GENOCIDE "
                   "AGAINST THE ROHINGYA MINORITY.",
                   2, INK, col_w - 122, 20)

    draw_odesa_night(page, right_x, top, 118, 132)
    page.text(right_x + 134, top + 6, "UKRAINE", 2, RED)
    page.paragraph(right_x + 134, top + 30, "ODESA IN THE DARK",
                   3, INK, col_w - 134, 30)
    page.paragraph(right_x + 134, top + 96,
                   "RUSSIAN STRIKES KNOCKED OUT POWER, HEAT AND WATER "
                   "ACROSS THE PORT CITY.",
                   2, INK, col_w - 134, 20)


# ------------------------------------------------------------ footer ticker

def draw_footer(page):
    page.hline(24, 934, 976, RED, 4)
    page.text_centered(
        512, 950,
        "ALSO TODAY: DELTA MELTDOWN HITS 3,000+ FLIGHTS - 6.5 QUAKE OFF "
        "VANUATU", 2, INK)
    page.text_centered(
        512, 972,
        "NO TSUNAMI RISK - WAYMO OFF U.S. FREEWAYS - TRUMP, XI AND PUTIN "
        "MEET AT APEC", 2, INK)
    page.text_centered(
        512, 1002, "24 NOVEMBER 2026 - ONE DAY. ONE PAGE. THE WHOLE WORLD",
        1, (110, 105, 95))


# ------------------------------------------------------------ entry point

def build_page():
    page = Page(WIDTH, HEIGHT, CREAM)
    page.rect(0, 0, WIDTH, 8, NAVY)
    page.rect(0, HEIGHT - 8, WIDTH, 8, NAVY)
    page.rect(0, 0, 8, HEIGHT, NAVY)
    page.rect(WIDTH - 8, 0, 8, HEIGHT, NAVY)
    draw_masthead(page)
    draw_top_story(page)
    draw_middle_row(page)
    draw_bottom_row(page)
    draw_footer(page)
    return page


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    page = build_page()
    data = encode_png(bytes(page.pixels), WIDTH, HEIGHT)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as handle:
        handle.write(data)
    os.chmod(path, 0o644)
    print("wrote {} ({} bytes)".format(path, len(data)))


if __name__ == "__main__":
    main()

