#!/usr/bin/env python3
"""news-image-20261124: one picture summing up Tuesday 24 November 2026.

A pure-stdlib Python program that draws a newspaper front page for the day:
Jensen Huang returns to Nvidia as its shares soar, the EU unveils its 22nd
sanctions package, Ukraine says it sank a Russian warship off Libya, the
world court rules Myanmar committed genocide against the Rohingya, and
Russian strikes leave Odesa in the dark -- plus the day's briefs in a ticker.

No network, no clock, no randomness: the same bytes on every run. Writes
entry.png to $MAKEFUN_OUTPUT_DIR, /output, or ./out as a fallback.
"""
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (31, 58, 95)
RED = (180, 35, 24)
TEAL = (14, 107, 122)
SEA = (16, 88, 110)
SKY = (168, 198, 224)
GOLD = (201, 162, 39)
EUGOLD = (242, 197, 0)
EUBLUE = (0, 51, 153)
GREEN = (46, 125, 50)
ORANGE = (224, 122, 26)
GREY = (107, 107, 102)
LIGHT = (228, 223, 210)
WHITE = (255, 255, 255)
DARK = (12, 12, 14)

_row = bytes(PAPER) * W
buf = bytearray(_row * H)
STRIDE = W * 3


def fill_rect(x, y, w, h, color):
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    px = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        off = yy * STRIDE + x0 * 3
        buf[off:off + len(px)] = px


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        off = (y * W + x) * 3
        buf[off:off + 3] = bytes(color)


def draw_disc(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def draw_ring(cx, cy, r, color, thick=2):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)
    draw_disc(cx, cy, r - thick, PAPER if color != PAPER else NAVY)


def draw_line(x0, y0, x1, y1, color, thick=1):
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    half = thick // 2
    for i in range(steps + 1):
        x = x0 + dx * i // steps
        y = y0 + dy * i // steps
        fill_rect(x - half, y - half, thick, thick, color)


def poly_fill(pts, color):
    ys = [p[1] for p in pts]
    y0, y1 = min(ys), max(ys)
    n = len(pts)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            if ay == by:
                continue
            if min(ay, by) <= y < max(ay, by):
                t = (y - ay) / float(by - ay)
                xs.append(ax + t * (bx - ax))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa = int(math.ceil(xs[i]))
            xb = int(math.floor(xs[i + 1]))
            if xb >= xa:
                fill_rect(xa, y, xb - xa + 1, 1, color)


def tri(x0, y0, x1, y1, x2, y2, color):
    poly_fill([(x0, y0), (x1, y1), (x2, y2)], color)


def star(cx, cy, ro, ri, color):
    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = math.radians(-90 + i * 36)
        pts.append((round(cx + r * math.cos(a)), round(cy + r * math.sin(a))))
    poly_fill(pts, color)


# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits, '1' = ink. Letters A-M here, the rest
# follow in the next block.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
}
FONT.update({
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "?2": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
})


def text_w(s, scale=1):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, color, scale=1):
    cx = x
    for ch in s:
        rows = FONT.get(ch, FONT["?2"])
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    fill_rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx - x - scale


def draw_text_right(x, y, s, color, scale=1):
    return draw_text(x - text_w(s, scale), y, s, color, scale)


def draw_text_center(cx, y, s, color, scale=1):
    return draw_text(cx - text_w(s, scale) // 2, y, s, color, scale)


def wrap(s, max_w, scale=1):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, color, scale, max_w, leading=12):
    lines = wrap(s, max_w, scale)
    for i, line in enumerate(lines):
        draw_text(x, y + i * leading, line, color, scale)
    return y + len(lines) * leading


# ------------------------------------------------------------------ scenes
def chip_scene(x, y, w, h):
    """Lead pictorial: a green chip, rising bars, and a big +31%."""
    fill_rect(x, y, w, h, NAVY)
    draw_text(x + 56, y + 58, "THE CHIP GIANT", GOLD, 1)
    # chip body with pins
    cx0, cy0, cw, ch = x + 56, y + 88, 220, 150
    for px in (110, 160, 210, 260):
        fill_rect(x + px, cy0 - 8, 14, 8, LIGHT)
        fill_rect(x + px, cy0 + ch, 14, 8, LIGHT)
    for py in (120, 160, 200):
        fill_rect(cx0 - 8, y + py, 8, 14, LIGHT)
        fill_rect(cx0 + cw, y + py, 8, 14, LIGHT)
    fill_rect(cx0, cy0, cw, ch, GREEN)
    fill_rect(cx0 + 14, cy0 + 14, cw - 28, ch - 28, (28, 96, 38))
    draw_text_center(cx0 + cw // 2, cy0 + 52, "NVDA", WHITE, 4)
    draw_text_center(cx0 + cw // 2, cy0 + 104, "NVIDIA", WHITE, 1)
    # rising bars along the bottom
    base = y + h - 20
    for i, bh in enumerate((18, 28, 40, 52, 64)):
        col = TEAL if i < 2 else (GREEN if i < 4 else GOLD)
        fill_rect(x + 56 + i * 40, base - bh, 28, bh, col)
    # the day's number, big and gold
    draw_text(x + 300, y + h - 88, "+31%", GOLD, 6)
    draw_text(x + 300, y + h - 32, "IN ONE DAY", WHITE, 1)


def eu_scene(x, y, w, h):
    """EU flag field: a ring of twelve gold stars around a big 22."""
    fill_rect(x, y, w, h, EUBLUE)
    cx, cy = x + w // 2, y + h // 2
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx = cx + int(52 * math.cos(a))
        sy = cy + int(52 * math.sin(a))
        star(sx, sy, 9, 4, EUGOLD)
    draw_text_center(cx, cy - 14, "22", EUGOLD, 4)


def sea_scene(x, y, w, h):
    """A warship on the sea with an explosion astern."""
    fill_rect(x, y, w, h // 2, SKY)
    fill_rect(x, y + h // 2, w, h - h // 2, SEA)
    draw_disc(x + w - 70, y + 26, 14, (240, 220, 140))
    # hull, mast and flag
    poly_fill([(x + 116, y + 88), (x + 236, y + 88), (x + 221, y + 63),
               (x + 131, y + 63)], DARK)
    fill_rect(x + 160, y + 52, 32, 11, DARK)
    draw_line(x + 176, y + 52, x + 176, y + 22, DARK, 3)
    fill_rect(x + 176, y + 22, 18, 10, RED)
    # explosion and smoke
    draw_disc(x + 268, y + 40, 16, ORANGE)
    draw_disc(x + 288, y + 50, 12, GOLD)
    draw_disc(x + 253, y + 55, 10, RED)
    draw_disc(x + 300, y + 30, 8, GREY)
    draw_disc(x + 312, y + 44, 6, GREY)
    # waves
    fill_rect(x + 36, y + 94, w - 72, 2, LIGHT)
    fill_rect(x + 60, y + 102, w - 120, 2, LIGHT)


def scales_glyph(cx, cy, color):
    """Small scales of justice, drawn in one colour."""
    draw_line(cx, cy - 26, cx, cy + 26, color, 3)
    draw_line(cx - 26, cy - 22, cx + 26, cy - 22, color, 3)
    draw_disc(cx, cy - 28, 3, color)
    for sx in (cx - 26, cx + 26):
        draw_line(sx, cy - 22, sx - 12, cy - 2, color, 2)
        draw_line(sx, cy - 22, sx + 12, cy - 2, color, 2)
        tri(sx - 12, cy - 2, sx + 12, cy - 2, sx, cy + 8, color)


def skyline_scene(x, y, w, h):
    """Odesa at night: a dark skyline, a few lit windows, a pale moon."""
    fill_rect(x, y, w, h, NAVY)
    draw_disc(x + w - 16, y + 20, 10, LIGHT)
    draw_disc(x + w - 40, y + 70, 18, ORANGE)
    heights = (70, 92, 58, 84, 66)
    bx = x
    for i, bh in enumerate(heights):
        bw = 19 if i % 2 == 0 else 18
        fill_rect(bx, y + h - bh, bw, bh, DARK)
        bx += bw
    # lit windows, fixed pattern
    for wx, wy in ((4, 102), (24, 82), (42, 112), (62, 92), (80, 112)):
        fill_rect(x + wx, y + wy, 3, 4, GOLD)


# ------------------------------------------------------------------ compose
def compose():
    # frame
    fill_rect(0, 0, W, 6, NAVY)
    fill_rect(0, H - 6, W, 6, NAVY)
    fill_rect(0, 0, 6, H, NAVY)
    fill_rect(W - 6, 0, 6, H, NAVY)

    # masthead
    fill_rect(24, 24, 976, 92, NAVY)
    draw_text(44, 52, "THE WORLD TODAY", WHITE, 5)
    draw_text_right(980, 40, "TUESDAY", GOLD, 2)
    draw_text_right(980, 68, "24 NOVEMBER 2026", WHITE, 2)
    fill_rect(24, 122, 976, 5, RED)

    # lead story: Nvidia
    chip_scene(24, 142, 472, 326)
    draw_text(520, 150, "TECH - MARKETS", RED, 2)
    draw_text(520, 184, "HUANG IS BACK", INK, 4)
    draw_text(520, 240, "NVIDIA CHIEF RETURNS", INK, 2)
    draw_text(520, 266, "AS SHARES SOAR 31%", INK, 2)
    draw_para(520, 306,
              "JENSEN HUANG IS BACK AS NVIDIA CHIEF AFTER AN INDEPENDENT "
              "INQUIRY CLEARED HIM. SHARES SOARED MORE THAN 31% IN A DAY. "
              "THE SENATE WILL QUESTION HIM ON DEC 3.",
              INK, 1, 460, 12)
    fill_rect(520, 400, 150, 30, GREEN)
    draw_text_center(595, 411, "NVDA +31%", WHITE, 1)
    fill_rect(690, 400, 190, 30, NAVY)
    draw_text_center(785, 411, "DEC 3 HEARING", WHITE, 1)

    # divider
    fill_rect(24, 482, 976, 4, LIGHT)

    # middle row: EU sanctions, Ukraine sinks a warship
    eu_scene(24, 500, 476, 110)
    draw_text(24, 622, "EUROPE", RED, 1)
    draw_text(24, 646, "EU UNVEILS 22ND", INK, 2)
    draw_text(24, 672, "SANCTIONS PACKAGE", INK, 2)
    draw_para(24, 706,
              "BRUSSELS TARGETS RUSSIAN BANKS, CRYPTO PLATFORMS AND "
              "ATHLETES COMPETING UNDER THE RUSSIAN FLAG.",
              INK, 1, 476, 12)

    sea_scene(524, 500, 476, 110)
    draw_text(524, 622, "UKRAINE", RED, 1)
    draw_text(524, 646, "KYIV SAYS IT SANK", INK, 2)
    draw_text(524, 672, "RUSSIAN WARSHIP", INK, 2)
    draw_para(524, 706,
              "UKRAINIAN DRONE SHIPS HIT THE MERKURY OFF THE LIBYAN COAST "
              "IN A LONG-RANGE STRIKE, KYIV SAYS.",
              INK, 1, 476, 12)

    # divider
    fill_rect(24, 750, 976, 4, LIGHT)

    # third row: the world court, Odesa in the dark
    draw_disc(72, 849, 46, GOLD)
    scales_glyph(72, 849, NAVY)
    draw_text(140, 784, "THE HAGUE", RED, 1)
    draw_text(140, 808, "MYANMAR GUILTY OF", INK, 2)
    draw_text(140, 834, "ROHINGYA GENOCIDE", INK, 2)
    draw_para(140, 868,
              "THE WORLD COURT RULED MYANMAR COMMITTED GENOCIDE AGAINST "
              "THE ROHINGYA MINORITY.",
              INK, 1, 360, 12)

    skyline_scene(524, 768, 96, 162)
    draw_text(640, 784, "UKRAINE", RED, 1)
    draw_text(640, 808, "ODESA IN THE DARK", INK, 2)
    draw_para(640, 844,
              "RUSSIAN STRIKES KNOCKED OUT POWER, HEAT AND WATER ACROSS "
              "THE PORT CITY.",
              INK, 1, 360, 12)

    # briefs ticker and footer
    fill_rect(24, 944, 976, 3, RED)
    draw_text_center(512, 958,
                     "ALSO TODAY: DELTA MELTDOWN HITS 3,000+ FLIGHTS - "
                     "6.5 QUAKE OFF VANUATU, NO TSUNAMI RISK",
                     INK, 1)
    draw_text_center(512, 974,
                     "WAYMO PULLS DRIVERLESS CARS OFF U.S. FREEWAYS - "
                     "TRUMP, XI AND PUTIN MEET AT APEC IN SHENZHEN",
                     INK, 1)
    draw_text_center(512, 996,
                     "24 NOVEMBER 2026 - ONE DAY, ONE PAGE, THE WHOLE WORLD",
                     GREY, 1)


# ------------------------------------------------------------------ PNG out
def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * STRIDE:(yy + 1) * STRIDE]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def main():
    compose()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "entry.png")
        with open(path, "wb") as f:
            f.write(png_bytes())
    except OSError:
        os.makedirs("out", exist_ok=True)
        with open(os.path.join("out", "entry.png"), "wb") as f:
            f.write(png_bytes())


if __name__ == "__main__":
    main()
