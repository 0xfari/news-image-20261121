#!/usr/bin/env python3
"""Render the v4 front page for news-image-20261121.

Draws a broadsheet front page for Saturday 21 November 2026 with PIL:
masthead + date, a drawn night scene over Kyiv as the hero, a bold
headline, six story cards with small drawn thumbnails, and an
"also today" brief strip. Writes entry.png (1024x1024) next to this file.

Fonts are bundled in fonts/ and loaded by relative path, so the build
needs no system font paths. All randomness is seeded: the output is
byte-identical on every run.
"""

import math
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (23, 19, 12)
MUTED = (90, 82, 70)
RED = (164, 31, 31)
NAVY = (16, 26, 51)
GOLD = (201, 162, 39)
BLUE_EU = (0, 51, 153)
TEAL = (14, 110, 110)
GREEN = (31, 110, 61)


def font(name, size):
    return ImageFont.truetype(str(HERE / "fonts" / name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def wrap(draw, text, fnt, max_w, max_lines=2):
    """Greedy wrap by pixel width; truncate the last line with ... if needed."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and draw.textlength(lines[-1], font=fnt) > max_w:
        while lines[-1] and draw.textlength(lines[-1] + "...", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "..."
    return lines


def center(draw, cx, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- hero art
def draw_hero(img, box, rng):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hero = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(hero)
    # night-sky gradient
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp((8, 12, 32), (38, 58, 96), y / h))
    # stars
    for _ in range(140):
        sx, sy = rng.randrange(w), rng.randrange(int(h * 0.62))
        r = rng.choice([1, 1, 1, 2])
        c = rng.choice([(255, 255, 255), (220, 225, 255), (255, 240, 200)])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=c)
    # moon + halo
    mx, my, mr = int(w * 0.84), 52, 26
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r, a in ((90, 18), (70, 26), (48, 40)):
        gd.ellipse([mx - r, my - r, mx + r, my + r], fill=(235, 240, 255, a))
    hero = Image.alpha_composite(hero.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(hero)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(238, 240, 248))
    d.ellipse([mx - mr + 9, my - mr + 4, mx + mr - 4, my + mr - 8],
              fill=(214, 219, 235))
    # missile arcs: quadratic bezier launch -> impact
    def bezier(p0, p1, p2, n=42):
        pts = []
        for i in range(n + 1):
            t = i / n
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
            pts.append((x, y))
        return pts

    arcs = [
        ((30, h - 30), (w * 0.30, 18), (w * 0.52, h - 118)),
        ((90, h - 24), (w * 0.42, 34), (w * 0.66, h - 96)),
        ((170, h - 28), (w * 0.55, 8), (w * 0.78, h - 128)),
        ((250, h - 26), (w * 0.62, 44), (w * 0.40, h - 104)),
        ((330, h - 30), (w * 0.74, 22), (w * 0.88, h - 110)),
        ((120, h - 22), (w * 0.36, 60), (w * 0.58, h - 132)),
    ]
    for p0, p1, p2 in arcs:
        pts = bezier(p0, p1, p2)
        for i in range(len(pts) - 1):
            fade = 1 - i / (len(pts) - 1)
            col = lerp((255, 210, 120), (255, 246, 220), fade)
            d.line([pts[i], pts[i + 1]], fill=col, width=2 if fade > 0.4 else 1)
        hx, hy = pts[-1]
        d.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=(255, 244, 200))
    # explosion bursts near the skyline
    def burst(cx, cy, r0):
        for k in range(14):
            ang = k * math.pi / 7 + rng.uniform(-0.12, 0.12)
            ln = r0 * rng.uniform(0.7, 1.25)
            d.line([(cx, cy), (cx + math.cos(ang) * ln, cy + math.sin(ang) * ln)],
                   fill=(255, 170, 60), width=3)
        for r, col in ((r0 * 0.95, (255, 120, 30)), (r0 * 0.6, (255, 180, 70)),
                       (r0 * 0.32, (255, 230, 150))):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    for bx, by, br in ((w * 0.52, h - 122, 26), (w * 0.66, h - 100, 20),
                       (w * 0.80, h - 130, 17)):
        burst(bx, by, br)
    # smoke puffs
    smoke = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for sx, sy, sr in ((w * 0.50, h - 150, 34), (w * 0.64, h - 128, 26),
                       (w * 0.82, h - 158, 22), (w * 0.58, h - 168, 30)):
        sd.ellipse([sx - sr, sy - sr * 0.7, sx + sr, sy + sr * 0.7],
                   fill=(150, 150, 160, 60))
    hero = Image.alpha_composite(hero.convert("RGBA"), smoke).convert("RGB")
    d = ImageDraw.Draw(hero)
    # searchlight wedges
    beam = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(w * 0.24, h), (w * 0.30, h), (w * 0.44, 30)], fill=(255, 255, 240, 26))
    bd.polygon([(w * 0.72, h), (w * 0.78, h), (w * 0.60, 46)], fill=(255, 255, 240, 22))
    hero = Image.alpha_composite(hero.convert("RGBA"), beam).convert("RGB")
    d = ImageDraw.Draw(hero)
    # skyline silhouette with lit windows + domed church
    ground = h - 34
    buildings = [(0, 92, 52), (92, 60, 78), (152, 74, 44), (226, 58, 92),
                 (284, 88, 60), (372, 66, 84), (438, 96, 48), (534, 62, 96),
                 (596, 80, 58), (676, 70, 88), (746, 90, 50), (836, 64, 80),
                 (900, 68, 56)]
    for bx, bw, bh in buildings:
        d.rectangle([bx, ground - bh, bx + bw, ground], fill=(7, 9, 18))
        for _ in range(bw * bh // 260):
            wx = rng.randrange(bx + 5, bx + bw - 6)
            wy = rng.randrange(ground - bh + 6, ground - 6)
            d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 196, 90))
    # church: tower + dome + cross, centre-left
    cx = 480
    d.rectangle([cx - 22, ground - 118, cx + 22, ground], fill=(7, 9, 18))
    d.pieslice([cx - 25, ground - 148, cx + 25, ground - 98], 180, 360,
               fill=(7, 9, 18))
    d.line([(cx, ground - 168), (cx, ground - 146)], fill=(7, 9, 18), width=4)
    d.line([(cx - 8, ground - 160), (cx + 8, ground - 160)], fill=(7, 9, 18), width=3)
    d.rectangle([cx - 3, ground - 112, cx + 3, ground - 96], fill=(255, 196, 90))
    # ground band
    d.rectangle([0, ground, w, h], fill=(5, 6, 12))
    img.paste(hero, (x0, y0))


# ---------------------------------------------------------------- thumbnails
def thumb(draw, box, kind, rng):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if kind == "poland":
        draw.rectangle(box, fill=(255, 255, 255))
        draw.rectangle([x0, y0 + h // 2, x1, y1], fill=(220, 40, 60))
        cx, cy = x0 + w * 0.62, y0 + h * 0.58
        for k in range(10):
            ang = k * math.pi / 5
            ln = 26 if k % 2 == 0 else 15
            draw.line([(cx, cy), (cx + math.cos(ang) * ln, cy + math.sin(ang) * ln)],
                      fill=(40, 30, 30), width=3)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 140, 40))
    elif kind == "eu":
        draw.rectangle(box, fill=BLUE_EU)
        cx, cy = x0 + w / 2, y0 + h / 2
        for k in range(12):
            ang = -math.pi / 2 + k * math.pi / 6
            sx, sy = cx + math.cos(ang) * 30, cy + math.sin(ang) * 30
            draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=GOLD)
    elif kind == "cop":
        draw.rectangle(box, fill=(232, 244, 232))
        cx, cy = x0 + w / 2, y0 + h / 2 - 4
        draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(46, 139, 87))
        draw.arc([cx - 30, cy - 30, cx + 30, cy + 30], 200, 340, fill=(200, 230, 200), width=3)
        draw.line([(cx - 30, cy), (cx + 30, cy)], fill=(200, 230, 200), width=3)
        draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=(20, 80, 40), width=3)
        center(draw, cx, y0 + h - 26, "31", SANS_B(24), fill=INK)
    elif kind == "cyclone":
        draw.rectangle(box, fill=(208, 232, 232))
        cx, cy = x0 + w / 2, y0 + h / 2
        pts = []
        for i in range(120):
            t = i / 119
            ang = t * math.pi * 5.2
            r = 4 + t * 36
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r * 0.9))
        draw.line(pts, fill=TEAL, width=5, joint="curve")
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255))
    elif kind == "sport":
        draw.rectangle(box, fill=GREEN)
        cx, cy = x0 + w / 2, y0 + h / 2 - 6
        draw.polygon([(cx - 22, cy - 18), (cx + 22, cy - 18), (cx + 14, cy + 6),
                      (cx - 14, cy + 6)], fill=GOLD)
        draw.arc([cx - 30, cy - 20, cx - 8, cy + 2], 90, 270, fill=GOLD, width=5)
        draw.arc([cx + 8, cy - 20, cx + 30, cy + 2], 270, 90, fill=GOLD, width=5)
        draw.rectangle([cx - 4, cy + 6, cx + 4, cy + 16], fill=GOLD)
        draw.rectangle([cx - 14, cy + 16, cx + 14, cy + 22], fill=GOLD)
        center(draw, cx, y0 + h - 24, "2 FIRSTS", SANS_B(17), fill=(255, 255, 255))
    elif kind == "numbers":
        draw.rectangle(box, fill=(24, 24, 30))
        center(draw, x0 + w / 2, y0 + 14, "≈100", SERIF_B(34), fill=(255, 214, 90))
        center(draw, x0 + w / 2, y0 + 56, "MISSILES", SANS_B(15), fill=(255, 255, 255))


# ---------------------------------------------------------------- page
def main():
    rng = random.Random(20261121)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([14, 14, W - 15, H - 15], outline=INK, width=2)

    # masthead
    center(d, W // 2, 30, "THE WORLD TODAY", SERIF_B(60))
    center(d, W // 2, 102, "SATURDAY  ·  21 NOVEMBER 2026", SANS_B(23))
    d.line([(28, 134), (W - 28, 134)], fill=INK, width=3)
    d.line([(28, 139), (W - 28, 139)], fill=INK, width=1)

    # hero
    draw_hero(img, (28, 150, W - 28, 448), rng)
    d = ImageDraw.Draw(img)
    center(d, W // 2, 462, "MISSILES RAIN ON KYIV", SERIF_B(56))
    center(d, W // 2, 530,
           "About 100 missiles strike overnight — one lands in Poland",
           SANS(23), fill=MUTED)
    d.line([(28, 566), (W - 28, 566)], fill=INK, width=2)

    # story cards: (kicker, headline, summary, thumb kind)
    cards = [
        ("POLAND", "ONE LANDS IN POLAND",
         "A missile comes down on Polish soil; Warsaw raises the alert.",
         "poland"),
        ("EUROPE", "EU CONDEMNS THE BARRAGE",
         "Allies call emergency talks.",
         "eu"),
        ("CLIMATE", "COP31 INTO OVERTIME",
         "Climate talks in Antalya stretch past their deadline.",
         "cop"),
        ("WEATHER", "AFTER CYCLONE AKVAN",
         "Relief reaches the coast as the damage is counted.",
         "cyclone"),
        ("SPORT", "TWO FIRSTS IN ONE DAY",
         "Records fall on a day of firsts across two sports.",
         "sport"),
        ("THE DAY", "THE DAY IN NUMBERS",
         "≈100 missiles fired · 1 lands in Poland · 21 Nov 2026",
         "numbers"),
    ]
    x_cols = [28, 522]
    y_rows = [580, 690, 800]
    for i, (kicker, head, summ, kind) in enumerate(cards):
        cx, cy = x_cols[i % 2], y_rows[i // 2]
        thumb(d, (cx, cy, cx + 96, cy + 96), kind, rng)
        tx, tw = cx + 108, 474 - 108 - 4
        d.text((tx, cy + 2), kicker, font=SANS_B(15), fill=RED)
        hl = wrap(d, head, SANS_B(22), tw, 2)
        yy = cy + 22
        for ln in hl:
            d.text((tx, yy), ln, font=SANS_B(22), fill=INK)
            yy += 25
        sl = wrap(d, summ, SANS(17), tw, 2)
        for ln in sl:
            d.text((tx, yy), ln, font=SANS(17), fill=MUTED)
            yy += 20

    # brief strip
    d.line([(28, 912), (W - 28, 912)], fill=INK, width=1)
    d.text((28, 922), "ALSO TODAY", font=SANS_B(16), fill=RED)
    briefs = [
        "Kyiv's defences intercept most of the incoming missiles.",
        "Poland seeks allied consultations after the strike.",
        "COP31 negotiators keep working into a second extra day.",
    ]
    bx = [28, 356, 684]
    for x, b in zip(bx, briefs):
        bl = wrap(d, b, SANS(16), 300, 2)
        yy = 948
        for ln in bl:
            d.text((x, yy), ln, font=SANS(16), fill=INK)
            yy += 20

    out = HERE / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
