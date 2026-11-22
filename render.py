#!/usr/bin/env python3
"""Draw the front page for Saturday 21 November 2026 (news-image-20261121 v5).

A fresh broadsheet, drawn from scratch with Pillow: masthead + dateline, a
drawn night scene over Manama as the hero, six story cards with small drawn
thumbnails, and an "also today" brief strip. Everything is drawn in code;
the only outside files are the DejaVu fonts bundled in fonts/, loaded by a
path relative to this file. Deterministic: fixed seed, no clock, no network.
Writes entry.png (1024x1024) next to this file.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

PAPER = (248, 244, 236)
INK = (17, 17, 17)
MUTED = (85, 85, 85)
RULE = (150, 140, 125)
ACCENT = (163, 22, 33)
NAVY = (20, 33, 61)
SKY_TOP = (8, 22, 46)
SKY_LOW = (32, 66, 104)
GOLD = (232, 180, 80)


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)


F_MAST = font("DejaVuSerif-Bold.ttf", 74)
F_KICK = font("DejaVuSans-Bold.ttf", 17)
F_HEAD = font("DejaVuSerif-Bold.ttf", 36)
F_CARD_H = font("DejaVuSerif-Bold.ttf", 25)
F_DECK = font("DejaVuSerif.ttf", 17)
F_HERO_DECK = font("DejaVuSerif.ttf", 20)
F_DATE = font("DejaVuSans-Bold.ttf", 19)
F_DATE_R = font("DejaVuSans.ttf", 17)
F_BRIEF = font("DejaVuSans.ttf", 18)
F_BRIEF_H = font("DejaVuSans-Bold.ttf", 17)
F_FOOT = font("DejaVuSans.ttf", 13)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit in width px."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, spacing):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += spacing
    return y


def vgrad(img, box, top, bottom):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        img.paste(c, (x0, y0 + i, x1, y0 + i + 1))


def draw_hero(img, rng):
    """Night over Manama: sky, stars, skyline, missile arcs, industrial fire."""
    x0, y0, x1, y1 = 28, 148, 996, 378
    vgrad(img, (x0, y0, x1, y1), SKY_TOP, SKY_LOW)
    d = ImageDraw.Draw(img, "RGBA")
    # Stars.
    for _ in range(70):
        sx = rng.randint(x0 + 4, x1 - 4)
        sy = rng.randint(y0 + 4, y1 - 90)
        r = rng.choice([1, 1, 2])
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(255, 255, 255, rng.randint(120, 220)))
    # Moon.
    d.ellipse((880, 168, 912, 200), fill=(235, 230, 210, 255))
    d.ellipse((888, 172, 912, 200), fill=(200, 195, 175, 255))
    # Skyline silhouette (twin sail towers + blocks), windows lit.
    base = y1 - 26
    d.rectangle((x0, base, x1, y1), fill=(10, 16, 28, 255))
    bx = x0 + 30
    while bx < x1 - 40:
        bw = rng.randint(34, 66)
        bh = rng.randint(40, 110)
        d.rectangle((bx, base - bh, bx + bw, base), fill=(13, 22, 38, 255))
        for _ in range(bw * bh // 260):
            wx = rng.randint(bx + 4, bx + bw - 6)
            wy = rng.randint(base - bh + 5, base - 8)
            d.rectangle((wx, wy, wx + 3, wy + 4), fill=(240, 200, 110, rng.randint(140, 230)))
        bx += bw + rng.randint(6, 18)
    # Twin sail towers, centre-left.
    for tx in (430, 500):
        d.polygon([(tx, base - 150), (tx + 34, base - 150), (tx + 26, base), (tx + 8, base)],
                  fill=(16, 26, 44, 255))
        for wy in range(base - 140, base - 10, 12):
            d.rectangle((tx + 12, wy, tx + 22, wy + 4), fill=(240, 200, 110, 200))
    # Water strip with reflections.
    d.rectangle((x0, y1 - 26, x1, y1), fill=(12, 30, 52, 255))
    for _ in range(26):
        rx = rng.randint(x0 + 6, x1 - 60)
        ry = rng.randint(y1 - 24, y1 - 6)
        d.line((rx, ry, rx + rng.randint(14, 44), ry), fill=(150, 190, 230, 130), width=1)
    # Missile arcs (orange trails) + interceptor streaks.
    arcs = [
        (120, 300, 620, 330, 200, 340),
        (300, 260, 760, 320, 205, 335),
        (520, 300, 900, 330, 215, 330),
    ]
    for (ax0, ay0, ax1, ay1, a0, a1) in arcs:
        d.arc((ax0, ay0, ax1, ay1), a0, a1, fill=(255, 154, 60, 220), width=5)
        d.arc((ax0, ay0, ax1, ay1), a0, a1, fill=(255, 230, 180, 255), width=2)
    # Bright warheads at arc ends.
    for hx, hy in ((588, 322), (742, 306), (872, 318)):
        d.ellipse((hx - 4, hy - 4, hx + 4, hy + 4), fill=(255, 240, 200, 255))
    # Interceptors rising.
    for ix, iy0, iy1 in ((700, 392, 250), (830, 392, 280)):
        d.line((ix, iy0, ix + 26, iy1), fill=(200, 225, 255, 230), width=3)
        d.ellipse((ix + 22, iy1 - 4, ix + 30, iy1 + 4), fill=(255, 255, 255, 255))
    # Industrial fire glow, right side.
    for r, alpha in ((90, 40), (64, 70), (40, 110)):
        d.ellipse((860 - r, base - 40 - r // 2, 860 + r, base + 10), fill=(255, 120, 30, alpha))
    d.polygon([(836, base), (848, base - 34), (858, base - 12), (868, base - 40),
               (878, base - 10), (888, base - 28), (896, base)],
              fill=(255, 170, 60, 255))
    d.polygon([(850, base), (858, base - 18), (866, base - 6), (874, base - 20), (882, base)],
              fill=(255, 230, 140, 255))


def thumb_skyline(d, x, y, s, rng):
    """Impact burst over a skyline (Kryvyi Rih / Poland)."""
    d.rectangle((x, y, x + s, y + s), fill=(38, 44, 66))
    for _ in range(24):
        sx = x + rng.randint(2, s - 2)
        sy = y + rng.randint(2, s // 2)
        d.point((sx, sy), fill=(255, 255, 255))
    for bx in range(x + 8, x + s - 8, 18):
        bh = rng.randint(24, 52)
        d.rectangle((bx, y + s - 14 - bh, bx + 13, y + s - 14), fill=(16, 18, 30))
    cx, cy = x + s // 2 + 14, y + s // 2 - 6
    for r, col in ((30, (255, 120, 30)), (20, (255, 180, 70)), (10, (255, 230, 150))):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    d.rectangle((x, y + s - 14, x + s, y + s), fill=(20, 24, 40))


def thumb_badge(d, x, y, s, rng):
    """Sheriff star over desert road (Mexico capture)."""
    d.rectangle((x, y, x + s, y + s), fill=(196, 164, 120))
    d.polygon([(x, y + s), (x + s, y + s), (x + s, y + s - 34), (x, y + s - 34)],
              fill=(150, 110, 70))
    d.polygon([(x, y + s - 34), (x + s // 2, y + s - 70), (x + s, y + s - 34)],
              fill=(120, 84, 52))
    cx, cy = x + s // 2, y + s // 2 - 8
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = 34 if i % 2 == 0 else 15
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=(232, 190, 90), outline=(120, 90, 20))
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(163, 22, 33))


def thumb_globe(d, x, y, s, rng):
    """Sun over a globe (COP31 climate talks)."""
    d.rectangle((x, y, x + s, y + s), fill=(168, 205, 225))
    cx, cy = x + s // 2, y + s // 2 + 12
    for i in range(8):
        ang = i * math.pi / 4
        d.line((cx + 30 * math.cos(ang), cy - 26 + 30 * math.sin(ang) * 0.4,
                cx + 44 * math.cos(ang), cy - 26 + 44 * math.sin(ang) * 0.4),
               fill=(232, 160, 40), width=4)
    d.ellipse((cx - 20, cy - 46, cx + 20, cy - 6), fill=(245, 190, 60))
    d.ellipse((cx - 34, cy - 18, cx + 34, cy + 50), fill=(52, 110, 70))
    d.ellipse((cx - 34, cy - 18, cx + 34, cy + 50), outline=(30, 70, 45), width=2)
    d.arc((cx - 34, cy - 18, cx + 34, cy + 50), 200, 340, fill=(120, 190, 130), width=6)
    d.arc((cx - 34, cy - 18, cx + 34, cy + 50), 20, 160, fill=(120, 190, 130), width=6)


def thumb_chart(d, x, y, s, rng):
    """Falling red chart (Nasdaq sell-off)."""
    d.rectangle((x, y, x + s, y + s), fill=(238, 236, 230))
    d.rectangle((x + 10, y + 10, x + s - 10, y + s - 10), fill=(255, 255, 255))
    pts = [(x + 16, y + 26), (x + 38, y + 40), (x + 58, y + 34), (x + 80, y + 62),
           (x + 100, y + 78), (x + 118, y + 96)]
    d.line(pts, fill=(163, 22, 33), width=5, joint="curve")
    for px, py in pts:
        d.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(163, 22, 33))
    d.line((x + 10, y + s - 22, x + s - 10, y + s - 22), fill=(150, 140, 125), width=1)


def thumb_shield(d, x, y, s, rng):
    """Shield with a cross (dengue study)."""
    d.rectangle((x, y, x + s, y + s), fill=(190, 220, 200))
    cx, cy = x + s // 2, y + s // 2
    d.polygon([(cx - 32, cy - 34), (cx + 32, cy - 34), (cx + 32, cy + 2),
               (cx, cy + 40), (cx - 32, cy + 2)], fill=(52, 110, 70),
              outline=(30, 70, 45))
    d.rectangle((cx - 6, cy - 22, cx + 6, cy + 6), fill=(255, 255, 255))
    d.rectangle((cx - 16, cy - 12, cx + 16, cy - 0), fill=(255, 255, 255))
    for _ in range(10):
        mx = x + rng.randint(4, s - 4)
        my = y + rng.randint(4, s - 4)
        d.ellipse((mx - 1, my - 1, mx + 1, my + 1), fill=(60, 60, 60))


def thumb_tanker(d, x, y, s, rng):
    """Tanker on waves, smoke on the horizon (Hormuz)."""
    d.rectangle((x, y, x + s, y + s), fill=(170, 205, 225))
    d.rectangle((x, y + s - 40, x + s, y + s), fill=(38, 84, 128))
    for wy in (y + s - 34, y + s - 22, y + s - 10):
        for wx in range(x + 4, x + s - 10, 22):
            d.arc((wx, wy - 4, wx + 18, wy + 6), 180, 360, fill=(220, 235, 245), width=2)
    d.polygon([(x + 14, y + s - 40), (x + s - 14, y + s - 40), (x + s - 26, y + s - 58),
               (x + 26, y + s - 58)], fill=(40, 40, 48))
    d.rectangle((x + 62, y + s - 76, x + 76, y + s - 58), fill=(40, 40, 48))
    d.rectangle((x + 80, y + s - 70, x + 88, y + s - 58), fill=(120, 120, 120))
    for r, col in ((16, (90, 90, 90)), (10, (140, 140, 140)), (5, (200, 200, 200))):
        d.ellipse((x + 92 - r, y + 18 - r, x + 92 + r, y + 18 + r), fill=col)


THUMBS = [thumb_skyline, thumb_badge, thumb_globe, thumb_chart, thumb_shield, thumb_tanker]

STORIES = [
    ("UKRAINE",
     "Missile hits Kryvyi Rih; two fall in Poland",
     "Two killed, dozens hurt; Warsaw calls the border strike a provocation."),
    ("MEXICO",
     "Cartel boss \u2018El Chapo Isidro\u2019 captured",
     "FBI most-wanted chief seized in Sinaloa; 11 dead in the violence after."),
    ("CLIMATE",
     "COP31 runs past deadline in Antalya",
     "Climate talks close to a final deal, the summit president says."),
    ("MARKETS",
     "AI sell-off wipes out Nasdaq\u2019s 2026 gains",
     "Worst week since March 2020; Nvidia halts H200 chip exports to China."),
    ("HEALTH",
     "Mosquitoes cut child dengue by 69%",
     "A major Brazil study brings rare hopeful health news."),
    ("ENERGY",
     "Two tankers hit near the Strait of Hormuz",
     "Attacks reach a wartime high; oil shipments through the strait fall 15%."),
]

BRIEFS = [
    "Russian cargo ship Sparta II ablaze in the Gulf of Finland after a drone strike; crew evacuates.",
    "Houthi missiles damage a Riyadh skyscraper after a Saudi-led coalition strike on Hodeidah.",
    "Earthquake shakes central Peru, rattling the Andes.",
    "Harden scores 51, passing Kobe Bryant, as the Cavaliers beat the Pacers 128\u2013119.",
]


def main():
    rng = random.Random(7)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # Masthead.
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=F_MAST)
    d.text(((W - tw) / 2, 22), title, font=F_MAST, fill=INK)
    d.line((28, 104, 996, 104), fill=INK, width=3)
    d.line((28, 109, 996, 109), fill=INK, width=1)
    # Dateline.
    d.text((28, 116), "SATURDAY, 21 NOVEMBER 2026", font=F_DATE, fill=INK)
    right = "ONE DAY \u00b7 ONE PAGE"
    d.text((996 - d.textlength(right, font=F_DATE_R), 118), right, font=F_DATE_R, fill=MUTED)
    d.line((28, 142, 996, 142), fill=RULE, width=1)

    # Hero scene + caption.
    draw_hero(img, rng)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((28, 378, 996, 382), fill=INK)
    d.text((28, 390), "THE GULF \u2014 MANAMA, BAHRAIN", font=F_KICK, fill=ACCENT)
    d.text((28, 410), "Iran strikes Bahrain", font=F_HEAD, fill=INK)
    deck = "Guards claim hits on two US bases; Bahrain reports an industrial fire, no injuries."
    d.text((28, 452), deck, font=F_HERO_DECK, fill=MUTED)

    # Story grid: 3 rows x 2 columns.
    grid_y, row_h, col_w, gap = 478, 136, 476, 16
    for i, (kick, head, deck_text) in enumerate(STORIES):
        row, col = divmod(i, 2)
        cx = 28 + col * (col_w + gap)
        cy = grid_y + row * row_h
        if row:
            d.line((28, cy - 6, 996, cy - 6), fill=RULE, width=1)
        if col:
            d.line((cx - 8, cy + 2, cx - 8, cy + row_h - 10), fill=RULE, width=1)
        THUMBS[i](d, cx, cy + 6, 128, rng)
        tx = cx + 142
        d.text((tx, cy + 4), kick, font=F_KICK, fill=ACCENT)
        y = draw_lines(d, wrap(d, head, F_CARD_H, col_w - 142), tx, cy + 26,
                       F_CARD_H, INK, 29)
        draw_lines(d, wrap(d, deck_text, F_DECK, col_w - 142), tx, y + 2,
                   F_DECK, MUTED, 20)

    # Brief strip.
    by = 896
    d.line((28, by - 6, 996, by - 6), fill=INK, width=2)
    d.text((28, by), "ALSO TODAY", font=F_BRIEF_H, fill=ACCENT)
    foot = "Drawn from Saturday\u2019s reporting"
    d.text((996 - d.textlength(foot, font=F_FOOT), by + 2), foot, font=F_FOOT, fill=MUTED)
    y = by + 26
    for b in BRIEFS:
        lines = wrap(d, "\u25aa  " + b, F_BRIEF, 968)
        y = draw_lines(d, lines, 28, y, F_BRIEF, INK, 22)
        y += 2

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
