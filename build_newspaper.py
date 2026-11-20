#!/usr/bin/env python3
"""Build the v2 one-page newspaper for make.fun news-image-20261119.

Fresh renderer for the @huaminyo v2 entry: "Thursday 19 November 2026",
52 stories, 7 regions, 17 drawn illustrations, a day-in-UTC timeline,
a numbers strip, a pinned world map and a DATE CHECK footer.

Draws everything in code with PIL (no photos, no copied artwork).
Writes entry.png (1024x1024, < 1 MiB) next to this file.
"""
import json
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

# ---- palette: cream paper, ink navy, signal red, muted accents ----
PAPER = (247, 242, 231)
INK = (26, 26, 30)
NAVY = (26, 42, 74)
RED = (166, 25, 46)
DARKRED = (122, 16, 32)
GOLD = (184, 134, 11)
TEAL = (0, 122, 122)
GREEN = (46, 125, 50)
PURPLE = (106, 27, 154)
ORANGE = (194, 84, 10)
GREY = (110, 110, 108)
LIGHT = (233, 226, 210)
CARD = (255, 253, 247)
SKY = (198, 222, 235)
SEA = (205, 226, 235)
LAND = (232, 220, 190)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = f"{FONT_DIR}/liberation/LiberationSerif-Bold.ttf"
SERIF = f"{FONT_DIR}/liberation/LiberationSerif-Regular.ttf"
SERIF_I = f"{FONT_DIR}/liberation/LiberationSerif-Italic.ttf"
SANS = f"{FONT_DIR}/liberation/LiberationSans-Regular.ttf"
SANS_B = f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf"
SANS_I = f"{FONT_DIR}/liberation/LiberationSans-Italic.ttf"
DJVU = f"{FONT_DIR}/dejavu/DejaVuSans.ttf"
DJVU_B = f"{FONT_DIR}/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap to pixel width; returns list of lines."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if d.textlength(trial, font=fnt) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def fit_lines(d, text, fnt, max_w, max_lines):
    """Wrap and truncate with ellipsis to max_lines."""
    lines = wrap(d, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "...", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


def num_badge(d, cx, cy, r, n, fill=RED):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    f = font(SANS_B, int(r * 1.15))
    t = str(n)
    tw = d.textlength(t, font=f)
    d.text((cx - tw / 2, cy - r * 0.78), t, font=f, fill=(255, 255, 255))


def tag(d, x, y, text, fill, fg=(255, 255, 255), size=9):
    f = font(SANS_B, size)
    tw = d.textlength(text, font=f)
    d.rectangle([x, y, x + tw + 10, y + size + 7], fill=fill)
    d.text((x + 5, y + 2), text, font=f, fill=fg)
    return tw + 10


def skyline(d, x, y, w, h, color, n=7, seed=1):
    """Simple night-city skyline silhouette with lit windows."""
    import random

    rnd = random.Random(seed)
    bw = w / n
    for i in range(n):
        bh = h * rnd.uniform(0.35, 0.95)
        bx = x + i * bw + 1
        d.rectangle([bx, y + h - bh, bx + bw - 2, y + h], fill=color)
        for wy in range(int(y + h - bh) + 4, int(y + h) - 3, 7):
            for wx in range(int(bx) + 3, int(bx + bw - 2) - 2, 6):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 214, 120))


def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    for i in range(7):
        d.rectangle([x, y + i * h / 6.5, x + w, y + (i + 0.5) * h / 6.5],
                    fill=(178, 34, 52))
    d.rectangle([x, y, x + w * 0.4, y + h * 0.55], fill=(60, 59, 110))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    d.text((x + w * 0.08, y - h * 0.08), "*", font=font(DJVU_B, int(h * 0.55)),
           fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


def flag_kr(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    d.ellipse([x + w * 0.38, y + h * 0.2, x + w * 0.62, y + h * 0.8],
              fill=(205, 49, 57))
    d.ellipse([x + w * 0.38, y + h * 0.5, x + w * 0.62, y + h * 0.8],
              fill=(0, 56, 147))


def flag_dk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 16, 46))
    d.rectangle([x + w * 0.3, y, x + w * 0.42, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill=(255, 255, 255))


def flag_au(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 0, 139))
    d.rectangle([x, y, x + w * 0.5, y + h * 0.5], fill=(0, 0, 100))
    for sx, sy in [(0.7, 0.3), (0.85, 0.6), (0.65, 0.75), (0.8, 0.85)]:
        d.text((x + w * sx, y + h * sy), "*", font=font(DJVU_B, int(h * 0.3)),
               fill=(255, 255, 255))


def flag_so(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(65, 137, 221))
    d.text((x + w * 0.38, y + h * 0.05), "*", font=font(DJVU_B, int(h * 0.8)),
           fill=(255, 255, 255))


def flag_ae(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(0, 122, 61))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(0, 0, 0))
    d.rectangle([x, y, x + w * 0.25, y + h], fill=(255, 0, 0))


def person(d, cx, base_y, h, suit, skin=(232, 190, 150), hair=(60, 45, 30)):
    """Simple seated figure: head + shoulders + tie."""
    hr = h * 0.16
    d.ellipse([cx - hr, base_y - h, cx + hr, base_y - h + 2 * hr], fill=skin)
    d.pieslice([cx - hr, base_y - h, cx + hr, base_y - h + 2 * hr],
               start=180, end=360, fill=hair)
    d.rounded_rectangle([cx - h * 0.28, base_y - h * 0.62,
                         cx + h * 0.28, base_y], radius=6, fill=suit)
    d.polygon([(cx, base_y - h * 0.6), (cx - 4, base_y - h * 0.45),
               (cx, base_y - h * 0.28), (cx + 4, base_y - h * 0.45)],
              fill=RED)


# ---------------------------------------------------------------- illustrations
def ill_summit(d, x, y, w, h):
    """Three leaders at a table under three flags (lead 1)."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 240))
    d.rectangle([x, y, x + w, y + h * 0.42], fill=NAVY)
    flag_us(d, x + w * 0.06, y + 8, w * 0.2, h * 0.28)
    flag_cn(d, x + w * 0.40, y + 8, w * 0.2, h * 0.28)
    flag_ru(d, x + w * 0.74, y + 8, w * 0.2, h * 0.28)
    ty = y + h * 0.66
    person(d, x + w * 0.16, ty, h * 0.44, (30, 50, 90), hair=(230, 220, 180))
    person(d, x + w * 0.50, ty, h * 0.44, (20, 20, 20))
    person(d, x + w * 0.84, ty, h * 0.44, (60, 30, 30), hair=(210, 210, 210))
    d.rectangle([x + 6, ty, x + w - 6, ty + 7], fill=(120, 72, 30))
    f = font(SANS_B, 11)
    for cx, name in [(0.16, "TRUMP"), (0.50, "XI"), (0.84, "PUTIN")]:
        tw = d.textlength(name, font=f)
        px = x + w * cx - tw / 2 - 4
        d.rectangle([px, ty + 10, px + tw + 8, ty + 26], fill=(255, 255, 255),
                    outline=INK, width=1)
        d.text((px + 4, ty + 11), name, font=f, fill=INK)


def ill_icj(d, x, y, w, h):
    """Peace Palace facade + scales + big 9-6 badge (lead 2)."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + w * 0.78, y + 6, x + w * 0.78 + 26, y + 32], fill=(255, 222, 100))
    # palace
    bx, by, bw, bh = x + w * 0.08, y + h * 0.38, w * 0.55, h * 0.5
    d.rectangle([bx, by, bx + bw, by + bh], fill=(176, 132, 92))
    d.rectangle([bx - 4, by - 8, bx + bw + 4, by], fill=(120, 80, 50))
    d.rectangle([bx + bw * 0.42, by - h * 0.28, bx + bw * 0.58, by],
                fill=(150, 110, 75))
    d.polygon([(bx + bw * 0.40, by - h * 0.28), (bx + bw * 0.60, by - h * 0.28),
               (bx + bw * 0.5, by - h * 0.42)], fill=(120, 80, 50))
    for i in range(5):
        d.rectangle([bx + 8 + i * (bw - 16) / 5, by + 8,
                     bx + 8 + (i + 0.6) * (bw - 16) / 5, by + bh - 8],
                    fill=(240, 230, 210))
    # scales
    sx = x + w * 0.80
    d.line([sx, y + h * 0.42, sx, y + h * 0.85], fill=GOLD, width=3)
    d.line([sx - 26, y + h * 0.46, sx + 26, y + h * 0.46], fill=GOLD, width=3)
    d.arc([sx - 34, y + h * 0.60, sx - 10, y + h * 0.80], start=0, end=180,
          fill=GOLD, width=2)
    d.arc([sx + 10, y + h * 0.60, sx + 34, y + h * 0.80], start=0, end=180,
          fill=GOLD, width=2)
    d.rectangle([x + w - 64, y + 6, x + w - 8, y + 40], fill=RED)
    f = font(SANS_B, 22)
    t = "9-6"
    d.text((x + w - 36 - d.textlength(t, font=f) / 2, y + 9), t, font=f,
           fill=(255, 255, 255))


def ill_cop(d, x, y, w, h):
    """Globe + thermometer + CUT stamp (lead 3)."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 222, 208))
    cx, cy, r = x + w * 0.26, y + h * 0.42, h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 180))
    d.ellipse([cx - r * 0.55, cy - r * 0.6, cx + r * 0.2, cy + r * 0.1],
              fill=(80, 160, 90))
    d.ellipse([cx + r * 0.1, cy + r * 0.2, cx + r * 0.7, cy + r * 0.75],
              fill=(80, 160, 90))
    # thermometer
    tx = x + w * 0.58
    d.rounded_rectangle([tx, y + 10, tx + 14, y + h - 34], radius=7,
                        fill=(255, 255, 255), outline=INK, width=1)
    d.rectangle([tx + 3, y + h * 0.45, tx + 11, y + h - 37], fill=RED)
    d.ellipse([tx - 5, y + h - 46, tx + 19, y + h - 22], fill=RED)
    # draft text card
    d.rectangle([x + w * 0.68, y + 8, x + w - 8, y + h * 0.62], fill=(255, 255, 255),
                outline=INK, width=1)
    f = font(SANS_B, 11)
    d.text((x + w * 0.68 + 6, y + 11), "DRAFT", font=f, fill=INK)
    f2 = font(SANS, 10)
    d.text((x + w * 0.68 + 6, y + 26), "fossil fuels", font=f2, fill=INK)
    d.line([x + w * 0.68 + 5, y + 35, x + w - 12, y + 35], fill=RED, width=2)
    d.text((x + w * 0.68 + 6, y + 39), "$120bn aid", font=f2, fill=INK)
    d.line([x + w * 0.68 + 5, y + 48, x + w - 12, y + 48], fill=RED, width=2)
    # CUT stamp
    f3 = font(SANS_B, 16)
    t = "CUT"
    tw = d.textlength(t, font=f3)
    sx, sy = x + w * 0.40, y + h - 40
    d.rectangle([sx, sy, sx + tw + 12, sy + 22], outline=RED, width=3)
    d.text((sx + 6, sy + 2), t, font=f3, fill=RED)


def ill_ipo(d, x, y, w, h):
    """Candlestick chart climbing, ANT label (4)."""
    d.rectangle([x, y, x + w, y + h], fill=(12, 40, 30))
    f = font(SANS_B, 11)
    d.text((x + 6, y + 3), "ANT  $83 → $97.17", font=f, fill=(255, 255, 255))
    f2 = font(SANS_B, 10)
    d.text((x + w - 38, y + 4), "+17%", font=f2, fill=(80, 220, 120))
    base = y + h - 4
    tops = [0.62, 0.55, 0.58, 0.44, 0.47, 0.34, 0.30]
    bw = (w - 16) / len(tops)
    for i, t in enumerate(tops):
        cx = x + 8 + i * bw + bw / 2
        top = y + 16 + t * (h - 20)
        col = (80, 220, 120) if i % 2 == 0 else (220, 90, 90)
        d.line([cx, top - 3, cx, base - 2], fill=col, width=1)
        d.rectangle([cx - bw * 0.28, top, cx + bw * 0.28, base - 2], fill=col)


def ill_gta(d, x, y, w, h):
    """Neon night city + VI badge + car (5)."""
    d.rectangle([x, y, x + w, y + h], fill=(40, 16, 64))
    d.ellipse([x + w * 0.72, y + 4, x + w * 0.72 + 22, y + 26],
              fill=(255, 200, 120))
    skyline(d, x, y + h * 0.25, w, h * 0.55, (24, 10, 44), n=8, seed=7)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(20, 20, 28))
    d.rounded_rectangle([x + w * 0.30, y + h - 26, x + w * 0.62, y + h - 14],
                        radius=4, fill=(255, 60, 120))
    d.ellipse([x + w * 0.35, y + h - 16, x + w * 0.35 + 8, y + h - 8],
              fill=INK)
    d.ellipse([x + w * 0.53, y + h - 16, x + w * 0.53 + 8, y + h - 8],
              fill=INK)
    f = font(SERIF_B, 26)
    d.text((x + 8, y + 2), "VI", font=f, fill=(255, 255, 255),
           stroke_width=1, stroke_fill=(255, 60, 180))
    f2 = font(SANS_B, 10)
    d.text((x + w - 66, y + h - 15), "OUT NOW", font=f2, fill=(255, 214, 120))


def ill_cyclone(d, x, y, w, h):
    """Spiral storm over a coastline map (6)."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 225, 240))
    d.rectangle([x, y, x + w * 0.30, y + h], fill=(222, 210, 170))
    d.text((x + 4, y + 4), "INDIA", font=font(SANS_B, 9), fill=(120, 90, 40))
    cx, cy = x + w * 0.62, y + h * 0.52
    for i, r in enumerate([h * 0.48, h * 0.38, h * 0.28, h * 0.19, h * 0.10]):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=200 + i * 55,
              end=200 + i * 55 + 250, fill=(30, 90, 160), width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255),
              outline=(30, 90, 160), width=2)
    f = font(SANS_B, 9)
    d.text((x + w - 62, y + 3), "90-100 km/h", font=f, fill=NAVY)


def ill_bridge(d, x, y, w, h):
    """Bridge span with explosion + RAIL HALTED banner (7)."""
    d.rectangle([x, y, x + w, y + h], fill=(210, 222, 232))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(90, 140, 180))
    d.line([x, y + h * 0.45, x + w, y + h * 0.45], fill=(60, 60, 66), width=4)
    for px in (0.15, 0.5, 0.85):
        d.line([x + w * px, y + h * 0.45, x + w * px, y + h * 0.62],
               fill=(60, 60, 66), width=3)
    bx, by = x + w * 0.62, y + h * 0.32
    for r, c in [(h * 0.30, (255, 140, 0)), (h * 0.21, (255, 220, 60)),
                 (h * 0.12, (255, 255, 255))]:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=c)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=RED)
    f = font(SANS_B, 10)
    t = "RAIL HALTED"
    d.text((x + (w - d.textlength(t, font=f)) / 2, y + h - 14), t, font=f,
           fill=(255, 255, 255))


def ill_intercept(d, x, y, w, h):
    """Night skyline, missile arc, intercept burst (8)."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 48))
    skyline(d, x, y + h * 0.4, w, h * 0.6, (10, 14, 30), n=6, seed=3)
    d.arc([x + w * 0.1, y - h * 0.4, x + w * 0.9, y + h * 0.9], start=200,
          end=330, fill=(255, 214, 120), width=2)
    bx, by = x + w * 0.68, y + h * 0.26
    for r, c in [(h * 0.24, (255, 140, 0)), (h * 0.14, (255, 255, 220))]:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=c)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(20, 90, 60))
    f = font(SANS_B, 10)
    t = "INTERCEPTED"
    d.text((x + (w - d.textlength(t, font=f)) / 2, y + h - 14), t, font=f,
           fill=(255, 255, 255))


def ill_arctic(d, x, y, w, h):
    """Snow peaks + Danish flag + 109-0 badge (9)."""
    d.rectangle([x, y, x + w, y + h], fill=(205, 228, 240))
    d.polygon([(x, y + h), (x + w * 0.3, y + h * 0.25), (x + w * 0.55, y + h)],
              fill=(255, 255, 255))
    d.polygon([(x + w * 0.4, y + h), (x + w * 0.7, y + h * 0.12),
               (x + w, y + h)], fill=(235, 242, 248))
    d.polygon([(x + w * 0.24, y + h * 0.35), (x + w * 0.3, y + h * 0.25),
               (x + w * 0.36, y + h * 0.35)], fill=(255, 255, 255))
    flag_dk(d, x + 6, y + 6, 30, 20)
    d.rectangle([x + w - 56, y + 6, x + w - 6, y + 30], fill=NAVY)
    f = font(SANS_B, 14)
    t = "109-0"
    d.text((x + w - 31 - d.textlength(t, font=f) / 2, y + 9), t, font=f,
           fill=(255, 255, 255))


def ill_jobs(d, x, y, w, h):
    """Bar chart 4.7% -> 4.9% + flag (10)."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 40, 80))
    flag_au(d, x + 6, y + 6, 30, 20)
    base = y + h - 10
    for i, (v, c) in enumerate([(0.42, (120, 180, 220)), (0.55, (255, 90, 90))]):
        bx = x + w * 0.30 + i * w * 0.30
        d.rectangle([bx, base - (h - 26) * v, bx + w * 0.20, base], fill=c)
    f = font(SANS_B, 12)
    d.text((x + w * 0.30, base - (h - 26) * 0.42 - 16), "4.7%", font=f,
           fill=(200, 220, 240))
    d.text((x + w * 0.60, base - (h - 26) * 0.55 - 16), "4.9%", font=f,
           fill=(255, 120, 120))


def ill_exam(d, x, y, w, h):
    """Exam hall: rows of desks + clock (11)."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 210))
    flag_kr(d, x + 6, y + 5, 26, 17)
    f = font(SANS_B, 10)
    t = "551,864 SIT"
    d.text((x + (w - d.textlength(t, font=f)) / 2, y + 5), t, font=f,
           fill=NAVY)
    d.ellipse([x + w - 24, y + 4, x + w - 6, y + 22], fill=(255, 255, 255),
              outline=INK, width=1)
    d.line([x + w - 15, y + 13, x + w - 15, y + 7], fill=INK, width=1)
    d.line([x + w - 15, y + 13, x + w - 10, y + 13], fill=INK, width=1)
    for c in range(4):
        dx = x + 12 + c * (w - 24) / 4
        d.ellipse([dx + 8, y + h - 20, dx + 20, y + h - 8],
                  fill=(232, 190, 150))
        d.rectangle([dx + 4, y + h - 8, dx + 24, y + h - 2], fill=(120, 72, 30))


def ill_expel(d, x, y, w, h):
    """Two flags + 72 HRS clock (12)."""
    d.rectangle([x, y, x + w, y + h], fill=(225, 232, 238))
    flag_so(d, x + 8, y + 8, 44, 30)
    flag_ae(d, x + w - 52, y + 8, 44, 30)
    d.line([x + 56, y + 23, x + w - 56, y + 23], fill=RED, width=2)
    d.polygon([(x + w - 60, y + 18), (x + w - 52, y + 23), (x + w - 60, y + 28)],
              fill=RED)
    d.ellipse([x + w / 2 - 14, y + h - 34, x + w / 2 + 14, y + h - 6],
              fill=(255, 255, 255), outline=INK, width=1)
    f = font(SANS_B, 9)
    t = "72 HRS"
    d.text((x + w / 2 - d.textlength(t, font=f) / 2, y + h - 27), t, font=f,
           fill=RED)


def ill_strike(d, x, y, w, h):
    """Crowd with placards + PARO NACIONAL banner (13)."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 210))
    d.rectangle([x + 8, y + 6, x + w - 8, y + 24], fill=(255, 220, 0))
    f = font(SANS_B, 10)
    t = "PARO NACIONAL"
    d.text((x + (w - d.textlength(t, font=f)) / 2, y + 9), t, font=f, fill=INK)
    for i, c in enumerate([(200, 60, 60), (60, 120, 200), (60, 180, 90),
                           (230, 160, 40), (150, 80, 180)]):
        cx = x + 12 + i * (w * 0.52) / 5
        d.ellipse([cx, y + h - 22, cx + 12, y + h - 10], fill=(232, 190, 150))
        d.rectangle([cx - 2, y + h - 10, cx + 14, y + h - 2], fill=c)
    d.rectangle([x + w * 0.60, y + 25, x + w * 0.92, y + 39],
                fill=(255, 255, 255), outline=INK, width=1)
    d.text((x + w * 0.62, y + 27), "NO", font=font(SANS_B, 9), fill=RED)


def ill_doping(d, x, y, w, h):
    """Track + BANNED stamp (14)."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 120, 80))
    for i in range(3):
        ly = y + 12 + i * (h - 24) / 3
        d.line([x, ly, x + w, ly], fill=(255, 255, 255), width=1)
    rx, ry = x + w * 0.22, y + h * 0.38
    d.ellipse([rx, ry - 6, rx + 9, ry + 3], fill=(120, 70, 40))
    d.line([rx + 4, ry + 3, rx + 2, ry + 14], fill=(120, 70, 40), width=4)
    d.line([rx + 2, ry + 14, rx - 6, ry + 22], fill=(120, 70, 40), width=3)
    d.line([rx + 2, ry + 14, rx + 10, ry + 21], fill=(120, 70, 40), width=3)
    f = font(SANS_B, 14)
    t = "BANNED · 3 YRS"
    tw = d.textlength(t, font=f)
    bx = x + w * 0.52
    d.rectangle([bx, y + h - 24, bx + tw + 10, y + h - 4], fill=(255, 255, 255),
                outline=RED, width=2)
    d.text((bx + 5, y + h - 22), t, font=f, fill=RED)


def ill_verdict(d, x, y, w, h):
    """Gavel + OVERTURNED banner (15)."""
    d.rectangle([x, y, x + w, y + h], fill=(230, 222, 205))
    d.rectangle([x + w * 0.2, y + h - 22, x + w * 0.8, y + h - 14],
                fill=(120, 72, 30))
    d.rectangle([x + w * 0.30, y + 16, x + w * 0.62, y + 30], fill=(150, 95, 40))
    d.line([x + w * 0.62, y + 23, x + w * 0.80, y + h - 22], fill=(150, 95, 40),
           width=5)
    flag_kr(d, x + 6, y + 6, 26, 17)
    f = font(SANS_B, 11)
    t = "OVERTURNED"
    tw = d.textlength(t, font=f)
    d.rectangle([x + (w - tw) / 2 - 6, y + h * 0.42, x + (w + tw) / 2 + 6,
                 y + h * 0.42 + 20], fill=GREEN)
    d.text((x + (w - tw) / 2, y + h * 0.42 + 3), t, font=f,
           fill=(255, 255, 255))


def ill_cricket(d, x, y, w, h):
    """Cricket field + 9 WICKETS badge (16)."""
    d.rectangle([x, y, x + w, y + h], fill=(120, 190, 110))
    d.ellipse([x + w * 0.2, y + h * 0.2, x + w * 0.8, y + h * 0.9],
              fill=(170, 220, 150))
    d.rectangle([x + w * 0.46, y + h * 0.35, x + w * 0.54, y + h * 0.75],
                fill=(222, 205, 160))
    for i in range(3):
        sx = x + w * 0.47 + i * 4
        d.line([sx, y + h * 0.38, sx, y + h * 0.52], fill=(255, 220, 100),
               width=2)
    d.ellipse([x + w * 0.70, y + h * 0.30, x + w * 0.70 + 9, y + h * 0.30 + 9],
              fill=(200, 40, 40))
    f = font(SANS_B, 13)
    t = "9 WICKETS"
    tw = d.textlength(t, font=f)
    d.rectangle([x + (w - tw) / 2 - 6, y + h - 24, x + (w + tw) / 2 + 6, y + h - 4],
                fill=NAVY)
    d.text((x + (w - tw) / 2, y + h - 22), t, font=f, fill=(255, 255, 255))


def ill_exports(d, x, y, w, h):
    """Container ship + $1 TRILLION banner (17)."""
    d.rectangle([x, y, x + w, y + h], fill=(190, 220, 235))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(70, 130, 180))
    for i, c in enumerate([(200, 60, 60), (60, 120, 200), (230, 160, 40),
                           (60, 180, 90)]):
        d.rectangle([x + 10 + i * 22, y + h * 0.42, x + 30 + i * 22,
                     y + h * 0.62], fill=c)
    d.polygon([(x + 6, y + h * 0.62), (x + w - 6, y + h * 0.62),
               (x + w - 16, y + h * 0.82), (x + 16, y + h * 0.82)],
              fill=(40, 40, 50))
    f = font(SANS_B, 13)
    t = "$1 TRILLION"
    tw = d.textlength(t, font=f)
    d.rectangle([x + (w - tw) / 2 - 6, y + 6, x + (w + tw) / 2 + 6, y + 28],
                fill=(255, 255, 255), outline=NAVY, width=1)
    d.text((x + (w - tw) / 2, y + 8), t, font=f, fill=NAVY)


ILLUSTRATIONS = {1: ill_summit, 2: ill_icj, 3: ill_cop, 4: ill_ipo,
                 5: ill_gta, 6: ill_cyclone, 7: ill_bridge, 8: ill_intercept,
                 9: ill_arctic, 10: ill_jobs, 11: ill_exam, 12: ill_expel,
                 13: ill_strike, 14: ill_doping, 15: ill_verdict,
                 16: ill_cricket, 17: ill_exports}

# ------------------------------------------------------------- story data
LEADS = [
    dict(n=1, loc="SHENZHEN · SUMMIT", status="REPORTED",
         head="Trump, Xi and Putin hold first three-way summit",
         body="The three leaders met for 90 minutes and issued a "
              "\"Declaration on Peace\". Kyiv was not in the room.",
         src="Reuters · AP · Xinhua"),
    dict(n=2, loc="THE HAGUE · JUSTICE", status="REPORTED",
         head="World Court: Myanmar committed genocide",
         body="By 9–6 the ICJ found Myanmar guilty of genocide against the "
              "Rohingya, and ordered reparations.",         src="Al Jazeera · UN News"),
    dict(n=3, loc="ANTALYA · CLIMATE", status="REPORTED",
         head="COP31 draft drops fossil fuels and $120bn aid goal",
         body="The slimmer text has no fossil-fuel phase-out and no figure "
              "for adaptation aid. Talks are due to end on Friday.",
         src="Reuters · AFP"),
]

SMALL = [
    dict(n=4, loc="NEW YORK · MARKETS", status="REPORTED",
         head="Anthropic debuts in the biggest IPO on record",
         body="ANT priced at $83, closed up 17% at $97.17. The $81.3bn sale "
              "tops the record.",
         src="AP · CNBC"),
    dict(n=5, loc="WORLDWIDE · GAMES", status="REPORTED",
         head="GTA VI goes on sale after a 13-year wait",
         body="Midnight launches, NZ first. Sensor Tower puts day one at "
              "17.1m copies.",
         src="BBC · Sensor Tower"),
    dict(n=6, loc="ODISHA · STORM", status="FORECAST",
         head="Cyclone Akvan nears India's coast",
         body="Over 200,000 moved to safety; landfall due Friday.",
         src="IMD"),
    dict(n=7, loc="CRIMEA · WAR", status="REPORTED",
         head="Kerch Bridge hit again",
         body="Third strike in a week halts trains to Russia.",
         src="Euronews"),
    dict(n=8, loc="RIYADH · WAR", status="REPORTED",
         head="Saudis shoot down Houthi missiles",
         body="Debris fell on the capital; no casualties reported.",
         src="Reuters"),
    dict(n=9, loc="GREENLAND · SECURITY", status="REPORTED",
         head="Denmark backs Arctic pact with US",
         body="Parliament approves the Greenland security deal 109–0.",
         src="AP"),
    dict(n=10, loc="CANBERRA · ECONOMY", status="REPORTED",
         head="Australia's jobless rate hits 4.9%",
         body="Highest since 2021; 43,500 jobs lost in October.",
         src="ABS"),
    dict(n=11, loc="SEOUL · EDUCATION", status="REPORTED",
         head="551,864 sit Suneung exam",
         body="Flights pause for the listening section.",
         src="Yonhap"),
    dict(n=12, loc="MOGADISHU · DIPLOMACY", status="REPORTED",
         head="Somalia expels UAE envoy",
         body="72 hours to leave; Mogadishu cites \"open invasion\".",
         src="Reuters"),
    dict(n=13, loc="BOGOTÁ · LABOUR", status="REPORTED",
         head="Colombia's unions hold national strike",
         body="Marches in three cities against a rescue law.",
         src="InfoBae"),
    dict(n=14, loc="NAIROBI · SPORT", status="REPORTED",
         head="Marathon champion banned for doping",
         body="Kenya's Peres Jepchirchir gets three years.",
         src="ABC"),
    dict(n=15, loc="SEOUL · JUSTICE", status="REPORTED",
         head="Korea's top court clears ex-PM Han",
         body="Han Duck-soo's martial-law conviction is overturned.",
         src="AP"),
    dict(n=16, loc="JOHANNESBURG · SPORT", status="REPORTED",
         head="South Africa beat Bangladesh by 9 wickets",
         body="Harmer takes 6–51; SA lead the series 1–0.",
         src="AP"),
    dict(n=17, loc="SEOUL · TRADE", status="REPORTED",
         head="South Korea exports pass $1 trillion",
         body="Fourth country to reach $1tn, aided by AI chips.",
         src="Reuters"),
]

BRIEFS = [
    (18, "Kyiv", "Drones hit Kyiv by day; embassies hit.", "Kyiv Independent"),
    (19, "Berlin", "Europe seeks winter truce; Putin: no.", "Euronews"),
    (20, "Hormuz", "Iran says tankers hit mines.", "Al Jazeera"),
    (21, "Gaza", "Israel says its tank raid is over.", "BBC"),
    (22, "Florida", "Floods shut schools again.", "CBS"),
    (23, "Jakarta", "Asset-seizure law passes.", "Kompas"),
    (24, "Paris", "French left splits over pact.", "Reuters"),
    (25, "Atacama", "NASA reports desert bloom.", "NASA"),
    (26, "Doha", "U-17 Cup: France 3–1 Holland.", "AP"),
    (27, "Odesa", "Overnight strike kills 11.", "Reuters"),
    (28, "Washington", "Senate rejects Iran curb, 48–51.", "AP"),
    (29, "New York", "Dow closes down 1,101.", "CNBC"),
    (30, "San Salvador", "Bukele seeks third term.", "Reuters"),
    (31, "Brasília", "Lula cuts work week to 42h.", "Reuters"),
    (32, "Buenos Aires", "Disability law passes 71–0.", "Reuters"),
    (33, "Port-au-Prince", "34 gang suspects killed.", "AP"),
    (34, "Bentonville", "Walmart revenue up 5.2%.", "Reuters"),
    (35, "California", "Blue Origin to launch AI sats.", "Reuters"),
    (36, "Tonga", "Drought emergency in effect.", "RNZ"),
    (37, "Rarotonga", "Cyclone Xavier weakens.", "RNZ"),
    (38, "Dhaka", "Yunus home ablaze; two killed.", "Reuters"),
    (39, "Ulaanbaatar", "MPs accept resignation.", "Reuters"),
    (40, "Shenzhen", "Xi urges nuclear-arms ban.", "Xinhua"),
    (41, "Canaries", "Record 11,000 migrants.", "Euronews"),
    (42, "Wellington", "Pay-equity cuts unlawful.", "RNZ"),
    (43, "Space", "Red giant eats a Sun-sized star.", "Nature"),
    (44, "Brussels", "EU delays methane rules.", "Euronews"),
    (45, "London", "Yacht Bayesian 'vulnerable'.", "BBC"),
    (46, "Zurich", "Two to challenge Infantino.", "ABC"),
    (47, "Dakar", "Dozens missing as boat sinks.", "Reuters"),
    (48, "Addis Ababa", "Airline probes hack.", "Reuters"),
    (49, "Vienna", "West seeks Iran inspections.", "Reuters"),
    (50, "Pretoria", "Central bank holds at 7.25%.", "SABC"),
    (51, "Rome", "Author Augias dies at 91.", "Euronews"),
    (52, "Madrid", "Sánchez, Feijóo clash on TV.", "Reuters"),
]

REGIONS = [("ASIA", 9, (30, 90, 160)), ("EUROPE", 11, (0, 122, 61)),
           ("MIDDLE EAST", 5, (160, 90, 20)), ("AFRICA", 7, (150, 50, 120)),
           ("AMERICAS", 11, (180, 40, 40)), ("OCEANIA", 4, (0, 140, 140)),
           ("GLOBAL", 5, (90, 90, 90))]

NUMBERS = [("3", "presidents at one table"),
           ("9–6", "World Court genocide vote"),
           ("$81.3bn", "Anthropic's record IPO"),
           ("109–0", "Danish vote on Arctic pact"),
           ("4.9%", "Australian jobless rate"),
           ("204,070", "listed to evacuate in Odisha"),
           ("551,864", "candidates in Korea's exam")]

TIMELINE = [("00:00", "GTA VI unlocks in Auckland"),
            ("02:05", "Houthi missile hits Riyadh"),
            ("08:40", "Suneung exam begins"),
            ("09:30", "Jakarta passes asset law"),
            ("10:15", "Hormuz tankers hit mines"),
            ("13:00", "Three leaders meet"),
            ("15:00", "ICJ reads genocide ruling"),
            ("21:00", "Dow closes down 1,101")]

# lon/lat of pinned places on the map (number -> (lon, lat))
PINS = {1: (114.1, 22.5), 2: (4.3, 52.1), 3: (30.7, 36.9), 4: (-74.0, 40.7),
        6: (85.5, 20.0), 7: (36.5, 45.3), 8: (46.7, 24.6),
        9: (-42.0, 72.0), 10: (149.1, -35.3), 11: (127.0, 37.5),
        12: (45.3, 2.0), 13: (-74.1, 4.7), 14: (36.8, -1.3),
        15: (129.8, 35.8), 16: (28.0, -26.2), 17: (124.5, 39.2),
        18: (30.5, 50.4), 19: (13.4, 52.5), 20: (56.3, 26.5),
        21: (34.5, 31.5), 22: (-80.2, 26.0), 23: (106.8, -6.2),
        24: (2.3, 48.9), 25: (-69.0, -23.0), 26: (51.5, 25.3),
        27: (30.7, 46.5), 28: (-77.0, 38.9), 29: (-78.0, 42.8),
        30: (-89.2, 13.7), 31: (-47.9, -15.8), 32: (-58.4, -34.6),
        33: (-72.3, 18.5), 34: (-94.2, 36.4), 35: (-122.0, 37.4),
        36: (-175.2, -21.1), 37: (-159.8, -21.2), 38: (90.4, 23.8),
        39: (106.9, 47.9), 40: (111.0, 25.0), 41: (-15.6, 28.1),
        42: (174.8, -41.3), 44: (4.4, 50.8),
        45: (-0.1, 51.5), 46: (8.5, 47.4), 47: (-17.5, 14.7),
        48: (38.7, 9.0), 49: (16.4, 48.2), 50: (28.2, -25.7),
        51: (12.5, 41.9), 52: (-3.7, 40.4)}
# stories 5 (worldwide) and 43 (space) have no map pin by design


# ------------------------------------------------------------------- map
def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    with open(os.path.join(HERE, "land-110m.json")) as f:
        topo = json.load(f)
    # decode TopoJSON arcs (delta-encoded, transformed)
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        pts, ax, ay = [], 0, 0
        for dx, dy in arc:
            ax += dx
            ay += dy
            pts.append((tx + ax * sx, ty + ay * sy))
        arcs.append(pts)

    def ring_points(idxs):
        pts = []
        for idx in idxs:
            seg = arcs[idx] if idx >= 0 else list(reversed(arcs[~idx]))
            pts.extend(seg[:-1] if pts else seg)
        return pts

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (90.0 - lat) / 180.0 * h
        return px, py

    land = topo["objects"]["land"]
    for geom in land["geometries"]:
        if geom["type"] == "MultiPolygon":
            for pol in geom["arcs"]:
                for ring in pol:
                    pts = [proj(lon, lat)
                           for lon, lat in ring_points(ring)]
                    d.polygon(pts, fill=LAND, outline=(190, 175, 140))
        elif geom["type"] == "Polygon":
            for ring in geom["arcs"]:
                pts = [proj(lon, lat) for lon, lat in ring_points(ring)]
                d.polygon(pts, fill=LAND, outline=(190, 175, 140))
    fnum = font(SANS_B, 8)
    for n, (lon, lat) in PINS.items():
        px, py = proj(lon, lat)
        r = 8 if n >= 10 else 7
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(n)
        tw = d.textlength(t, font=fnum)
        d.text((px - tw / 2, py - 5.5), t, font=fnum, fill=(255, 255, 255))


# ------------------------------------------------------------------ cards
STATUS_COLOR = {"REPORTED": (20, 120, 60), "FORECAST": (200, 120, 0),
                "CLAIM": (160, 60, 60)}


def lead_card(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=(200, 192, 172),
                width=1)
    ill_h = 86
    ILLUSTRATIONS[story["n"]](d, x + 1, y + 1, w - 2, ill_h)
    tx = x + 8
    ty = y + ill_h + 6
    num_badge(d, tx + 9, ty + 8, 9, story["n"])
    f_loc = font(SANS_B, 10)
    d.text((tx + 22, ty + 2), story["loc"], font=f_loc, fill=RED)
    tw = d.textlength(story["loc"], font=f_loc)
    tag(d, tx + 26 + tw, ty + 1, story["status"],
        STATUS_COLOR[story["status"]], size=8)
    ty += 20
    f_head = font(SERIF_B, 18)
    lines = fit_lines(d, story["head"], f_head, w - 16, 2)
    for ln in lines:
        d.text((tx, ty), ln, font=f_head, fill=INK)
        ty += 21
    ty += 2
    f_body = font(SERIF, 10.5)
    for ln in fit_lines(d, story["body"], f_body, w - 16, 2):
        d.text((tx, ty), ln, font=f_body, fill=(50, 50, 50))
        ty += 12
    f_src = font(SANS_I, 8)
    d.text((tx, y + h - 13), "— " + story["src"], font=f_src, fill=GREY)


def small_card(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=(200, 192, 172),
                width=1)
    ill_h = 42
    ILLUSTRATIONS[story["n"]](d, x + 1, y + 1, w - 2, ill_h)
    tx = x + 6
    ty = y + ill_h + 4
    num_badge(d, tx + 7, ty + 6, 7, story["n"])
    f_loc = font(SANS_B, 8)
    d.text((tx + 16, ty + 1), story["loc"], font=f_loc, fill=RED)
    ty += 14
    f_head = font(SERIF_B, 12.5)
    lines = fit_lines(d, story["head"], f_head, w - 12, 2)
    for ln in lines:
        d.text((tx, ty), ln, font=f_head, fill=INK)
        ty += 14
    f_body = font(SERIF, 9)
    for ln in fit_lines(d, story["body"], f_body, w - 12, 2):
        d.text((tx, ty), ln, font=f_body, fill=(60, 60, 60))
        ty += 11
    f_src = font(SANS_I, 7.5)
    d.text((tx, y + h - 10), "— " + story["src"], font=f_src, fill=GREY)


# ----------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 14  # margin
    CW = W - 2 * M  # content width

    # top bar
    d.rectangle([0, 0, W, 22], fill=NAVY)
    f_top = font(SANS_B, 11)
    d.text((M, 4), "THE WORLD IN ONE DAY", font=f_top, fill=(255, 255, 255))
    t = "52 STORIES  ·  7 REGIONS  ·  17 DRAWN  ·  ALL FROM THIS ONE DAY"
    d.text((W - M - d.textlength(t, font=f_top), 4), t, font=f_top,
           fill=(255, 214, 120))

    # masthead
    f_mast = font(SERIF_B, 58)
    t = "Thursday 19 November 2026"
    d.text(((W - d.textlength(t, font=f_mast)) / 2, 24), t, font=f_mast,
           fill=INK)
    d.rectangle([M, 90, W - M, 92], fill=RED)
    f_sub = font(SERIF_I, 16)
    t = ("Trump, Xi and Putin share one table  ·  The World Court finds "
         "genocide in Myanmar  ·  COP31's draft drops fossil fuels")
    d.text(((W - d.textlength(t, font=f_sub)) / 2, 96), t, font=f_sub,
           fill=DARKRED)

    # numbers strip
    y0, y1 = 118, 157
    d.rectangle([M, y0, W - M, y1], fill=(255, 255, 255),
                outline=(200, 192, 172), width=1)
    colw = CW / len(NUMBERS)
    for i, (num, label) in enumerate(NUMBERS):
        cx = M + i * colw
        if i:
            d.line([cx, y0 + 5, cx, y1 - 5], fill=(220, 212, 190), width=1)
        f_num = font(SERIF_B, 23)
        d.text((cx + (colw - d.textlength(num, font=f_num)) / 2, y0 + 3),
               num, font=f_num, fill=RED)
        f_lab = font(SANS, 8.5)
        for j, ln in enumerate(fit_lines(d, label, f_lab, colw - 10, 2)):
            tw = d.textlength(ln, font=f_lab)
            d.text((cx + (colw - tw) / 2, y0 + 27 + j * 10), ln, font=f_lab,
                   fill=(70, 70, 70))

    # region bar
    y0, y1 = 161, 178
    total = sum(c for _, c, _ in REGIONS)
    cx = M
    f_reg = font(SANS_B, 9.5)
    for name, count, col in REGIONS:
        seg = CW * count / total
        d.rectangle([cx, y0, cx + seg - 1, y1], fill=col)
        t = f"{name} {count}"
        d.text((cx + (seg - d.textlength(t, font=f_reg)) / 2, y0 + 4), t,
               font=f_reg, fill=(255, 255, 255))
        cx += seg

    # timeline: the day in UTC (second quantitative visual)
    y0, y1 = 182, 220
    d.rectangle([M, y0, W - M, y1], fill=(255, 255, 255),
                outline=(200, 192, 172), width=1)
    f_th = font(SANS_B, 9)
    d.text((M + 6, y0 + 3), "THE DAY IN UTC", font=f_th, fill=NAVY)
    d.line([M + 30, y0 + 15, W - M - 30, y0 + 15], fill=(200, 192, 172),
           width=1)
    n = len(TIMELINE)
    span = CW - 60
    for i, (tm, what) in enumerate(TIMELINE):
        px = M + 30 + span * i / (n - 1)
        d.ellipse([px - 3, y0 + 12, px + 3, y0 + 18], fill=RED)
        f_tm = font(SANS_B, 9)
        tw = d.textlength(tm, font=f_tm)
        d.text((px - tw / 2, y0 + 19), tm, font=f_tm, fill=RED)
        f_w = font(SANS, 8)
        colw = span / n
        for j, ln in enumerate(fit_lines(d, what, f_w, colw - 4, 1)):
            tw = d.textlength(ln, font=f_w)
            lx = min(max(px - tw / 2, M + 2), W - M - 2 - tw)
            d.text((lx, y0 + 29 + j * 9), ln, font=f_w, fill=INK)

    # leads row
    y0, lh = 226, 192
    gap = 8
    lw = (CW - 2 * gap) / 3
    for i, story in enumerate(LEADS):
        lead_card(d, M + i * (lw + gap), y0, lw, lh, story)

    # small rows: 5 + 5 + 4
    y = y0 + lh + 6
    sh = 118
    rows = [SMALL[0:5], SMALL[5:10], SMALL[10:14]]
    for row in rows:
        n = len(row)
        sw = (CW - (n - 1) * gap) / n
        for i, story in enumerate(row):
            small_card(d, M + i * (sw + gap), y, sw, sh, story)
        y += sh + 6
    # y is now just below the last small row

    # bottom: map + briefs
    y0 = y + 2
    bh = 166
    map_w = 318
    d.rectangle([M, y0, M + map_w, y0 + bh], fill=CARD,
                outline=(200, 192, 172), width=1)
    f_bh = font(SANS_B, 10)
    d.text((M + 6, y0 + 4), "WHERE IT HAPPENED", font=f_bh, fill=INK)
    draw_map(d, M + 4, y0 + 20, map_w - 8, bh - 38)
    f_note = font(SANS_I, 8)
    d.text((M + 6, y0 + bh - 14),
           "Numbers match the stories. 5 worldwide · 43 in space.",
           font=f_note, fill=GREY)

    bx = M + map_w + 10
    bw = W - M - bx
    d.text((bx, y0 + 4), "ALSO ON THURSDAY 19 NOVEMBER — 35 MORE STORIES",
           font=f_bh, fill=RED)
    cols = [BRIEFS[0:12], BRIEFS[12:24], BRIEFS[24:35]]
    colw = bw / 3
    f_bnum = font(SANS_B, 9)
    f_bcity = font(SERIF_B, 9)
    f_btext = font(SERIF, 9)
    f_bsrc = font(SANS_I, 7.5)
    for ci, col in enumerate(cols):
        cx = bx + ci * colw
        by = y0 + 20
        for n, city, text, src in col:
            d.text((cx, by), str(n), font=f_bnum, fill=RED)
            nw = d.textlength(str(n), font=f_bnum) + 4
            line = f"{city} — {text}"
            lines = fit_lines(d, line, f_btext, colw - nw - 2, 1)
            first = lines[0]
            if first.startswith(city):
                d.text((cx + nw, by), city, font=f_bcity, fill=INK)
                rest = first[len(city):]
                d.text((cx + nw + d.textlength(city, font=f_bcity), by),
                       rest, font=f_btext, fill=(50, 50, 50))
            else:
                d.text((cx + nw, by), first, font=f_btext, fill=(50, 50, 50))
            by += 12
    y1 = y0 + bh

    # DATE CHECK footer
    y0 = y1 + 6
    y1 = y0 + 30
    d.rectangle([M, y0, W - M, y1], outline=RED, width=1, fill=(255, 248, 240))
    f_dc = font(SANS_B, 9)
    d.text((M + 6, y0 + 3), "DATE CHECK", font=f_dc, fill=RED)
    f_dct = font(SERIF, 9)
    t1 = ("Left out, first reported Wed 18 Nov or earlier: EU's €45bn "
          "Ukraine loan · Iran fires on Kuwait and Bahrain · Nvidia results "
          "· Voyager 1 light-day · Van Gogh $190.4m sale · Epstein files.")
    t2 = ("Not yet news: Akvan's landfall, COP31's close (both Fri 20 Nov) "
          "· GTA VI day-one sales · Russia's Kyiv strike (Fri 01:25) · "
          "Starship test (29 Nov).")
    for ln in fit_lines(d, t1, f_dct, W - M - 74 - 6, 1):
        d.text((M + 74, y0 + 3), ln, font=f_dct, fill=INK)
    for ln in fit_lines(d, t2, f_dct, W - M - 74 - 6, 1):
        d.text((M + 74, y0 + 18), ln, font=f_dct, fill=INK)

    # sources footer
    f_ft = font(SANS, 8)
    t = ("Every story here happened, or was first reported, on Thursday 19 "
         "November 2026 (any time zone). Claims are attributed, not stated "
         "as fact. Pictures and map: original, drawn in code.")
    d.text(((W - d.textlength(t, font=f_ft)) / 2, y1 + 5), t, font=f_ft,
           fill=GREY)
    t2 = ("Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Euronews, "
          "ABC, RNZ, Xinhua, Yonhap, Kompas, ABS, IMD, Nature, InfoBae · "
          "2026-11-19")
    d.text(((W - d.textlength(t2, font=f_ft)) / 2, y1 + 16), t2, font=f_ft,
           fill=GREY)
    return img


def main():
    img = build()
    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    size = os.path.getsize(out)
    print(f"wrote {out} {img.size} {size} bytes "
          f"({'OK' if size <= 1048576 else 'OVER 1 MiB'})")


if __name__ == "__main__":
    main()
