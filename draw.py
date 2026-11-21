#!/usr/bin/env python3
"""Draw entry.png for news-image-20261121 v2: THE WORLD TODAY, Saturday 21 November 2026.

Fresh-authored in this session (2026-11-21) for the v2 resubmit. A real front
page, not an index: one drawn locator map of Europe as the picture, one big
hero story, a by-the-numbers strip, then two columns of four stories each
(9 stories total). Fewer, bigger stories with real air between them — the
clean-layout family that beat dense layouts on this series (20261119 v2).
Full-colour RGB, 1024x1024. Facts are the same wire-verified facts as v1.
"""
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24

NAVY = (13, 38, 68)
SEA = (10, 28, 55)
LAND = (42, 88, 148)
LAND2 = (56, 110, 175)
RED = (196, 30, 30)
RED_SOFT = (226, 84, 66)
INK = (20, 20, 20)
GREY = (90, 90, 90)
HAIR = (214, 214, 214)
CREAM = (253, 246, 236)
WHITE = (255, 255, 255)
BLUE = (29, 78, 137)
GREEN = (30, 122, 76)
DARKRED = (179, 38, 30)
GOLD = (176, 124, 22)

F = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = F + "DejaVuSerif-Bold.ttf"
SANS = F + "DejaVuSans.ttf"
SANS_B = F + "DejaVuSans-Bold.ttf"

f_mast = ImageFont.truetype(SERIF_B, 48)
f_date_b = ImageFont.truetype(SANS_B, 21)
f_date = ImageFont.truetype(SANS, 13)
f_strip = ImageFont.truetype(SANS_B, 12)
f_map_tag = ImageFont.truetype(SANS_B, 12)
f_city = ImageFont.truetype(SANS_B, 12)
f_sea = ImageFont.truetype(SANS, 11)
f_hero_h = ImageFont.truetype(SANS_B, 32)
f_hero_s = ImageFont.truetype(SANS, 15)
f_chip = ImageFont.truetype(SANS_B, 12)
f_num = ImageFont.truetype(SANS_B, 30)
f_num_l = ImageFont.truetype(SANS, 11)
f_col = ImageFont.truetype(SANS_B, 15)
f_head = ImageFont.truetype(SANS_B, 16)
f_sum = ImageFont.truetype(SANS, 13)
f_foot = ImageFont.truetype(SANS, 11)


def wrap(draw, text, font, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, font, width, max_lines):
    lines = wrap(draw, text, font, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "...", font=font) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


def bezier(p0, p1, p2, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def burst(d, cx, cy, r1=13, r2=5, colour=RED_SOFT):
    pts = []
    for i in range(16):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / 8
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=colour, outline=WHITE)


# --- the day, verified against wire reports dated 21 Nov 2026 ---
HERO = {
    "headline": "Russia fires ~100 missiles at Ukraine overnight; one lands in Poland",
    "summary": (
        "Eight people were killed in the barrage, including a seven-year-old in Kryvyi Rih. "
        "Warsaw says two missiles and a suspected drone came down on its soil while NATO drills "
        "ran nearby; France has called for an emergency UN Security Council meeting."
    ),
    "chips": ["~100 MISSILES", "8 KILLED", "POLAND HIT"],
}

NUMBERS = [
    ("~100", "missiles fired\nin one night"),
    ("8", "people killed\nin the barrage"),
    ("1,144", "children killed\nin Ukraine — UNICEF"),
    ("$12bn", "sought for food aid\nin 2027 — WFP"),
]

COLUMNS = [
    ("EUROPE", BLUE, [
        ("EU to summon Russian envoy",
         "The EU will summon Moscow's envoy over damage to its Kyiv embassy, Kaja Kallas says."),
        ("Denmark: Russia plot to kill rapper",
         "Two Danes are charged over a foiled plot to kill Ukrainian rapper Kyivstoner; Moscow's attache expelled."),
        ("EU approves \u20ac1bn in arms aid",
         "EU ministers back joint weapons buying for Ukraine, deliveries due by end of 2027."),
        ("COP31 runs into overtime",
         "Climate talks in Antalya pass their deadline, with the draft deal omitting any fossil-fuel phase-out."),
    ]),
    ("WORLD", DARKRED, [
        ("Trump dials in on Ukraine",
         "The US president joins a meeting of European allies after his Shenzhen talks with Putin and Xi."),
        ("Saudi intercepts Houthi missile",
         "Riyadh says it shot down a Houthi ballistic missile and drones; debris fell on the capital."),
        ("Six killed in Gaza strikes",
         "Israeli strikes kill six Palestinians, Gaza civil defence says, as the ceasefire frays."),
        ("Akvan: no major damage",
         "Odisha reports no major damage after landfall; 370,000 people had been evacuated."),
    ]),
]


def draw_map(d, x0, y0, x1, y1):
    """Stylised locator map of Europe on a dark sea, with the missile arcs."""
    d.rectangle([x0, y0, x1, y1], fill=SEA)
    # rough continent: one big landmass + Britain off the north-west
    land = [
        (x0 + 130, y0 + 18), (x0 + 300, y0 + 8), (x0 + 520, y0 + 22),
        (x0 + 760, y0 + 12), (x0 + 930, y0 + 40), (x0 + 950, y0 + 110),
        (x0 + 900, y0 + 150), (x0 + 920, y0 + 195), (x0 + 830, y0 + 212),
        (x0 + 700, y0 + 202), (x0 + 620, y0 + 214), (x0 + 520, y0 + 205),
        (x0 + 430, y0 + 212), (x0 + 330, y0 + 200), (x0 + 250, y0 + 208),
        (x0 + 150, y0 + 198), (x0 + 60, y0 + 185), (x0 + 40, y0 + 110),
        (x0 + 70, y0 + 55),
    ]
    d.polygon(land, fill=LAND)
    # Black Sea / Mediterranean cut: paint sea-coloured inlets
    d.polygon([(x0 + 640, y0 + 200), (x0 + 760, y0 + 192), (x0 + 820, y0 + 218),
               (x0 + 700, y0 + 236), (x0 + 620, y0 + 228)], fill=SEA)
    d.polygon([(x0 + 300, y0 + 205), (x0 + 430, y0 + 214), (x0 + 520, y0 + 206),
               (x0 + 480, y0 + 238), (x0 + 340, y0 + 238)], fill=SEA)
    # Britain
    d.polygon([(x0 + 95, y0 + 60), (x0 + 125, y0 + 55), (x0 + 140, y0 + 95),
               (x0 + 120, y0 + 130), (x0 + 95, y0 + 110)], fill=LAND2)
    # sea labels
    d.text((x0 + 30, y0 + 200), "ATLANTIC", font=f_sea, fill=(140, 165, 200))
    d.text((x0 + 688, y0 + 208), "BLACK SEA", font=f_sea, fill=(140, 165, 200))
    # missile arcs: Russia -> Kyiv, Russia -> Poland
    moscow = (x0 + 830, y0 + 70)
    kyiv = (x0 + 620, y0 + 165)
    warsaw = (x0 + 470, y0 + 105)
    for p0, p1, p2 in [
        (moscow, (x0 + 780, y0 + 90), kyiv),
        (moscow, (x0 + 700, y0 + 45), warsaw),
    ]:
        pts = bezier(p0, p1, p2)
        for i, (px, py) in enumerate(pts):
            if i % 3 == 0:
                d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED_SOFT)
        ex, ey = pts[-1]
        d.polygon([(ex + 10, ey), (ex - 6, ey - 6), (ex - 6, ey + 6)],
                  fill=RED_SOFT)
    # impact bursts + city dots
    burst(d, warsaw[0], warsaw[1])
    burst(d, kyiv[0], kyiv[1], r1=11, r2=4)
    d.ellipse([moscow[0] - 4, moscow[1] - 4, moscow[0] + 4, moscow[1] + 4],
              fill=WHITE, outline=RED)
    d.text((moscow[0] + 10, moscow[1] - 8), "MOSCOW", font=f_city, fill=WHITE)
    d.text((kyiv[0] + 12, kyiv[1] - 6), "KYIV", font=f_city, fill=WHITE)
    d.text((warsaw[0] - 8, warsaw[1] - 26), "WARSAW", font=f_city, fill=WHITE)
    d.text((x0 + 12, y0 + 10), "EUROPE — OVERNIGHT BARRAGE", font=f_map_tag,
           fill=(170, 195, 225))


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, W, 86], fill=NAVY)
    d.text((MARGIN, 16), "THE WORLD TODAY", font=f_mast, fill=WHITE)
    d.text((W - MARGIN, 16), "SATURDAY", font=f_date, fill=(200, 210, 220), anchor="ra")
    d.text((W - MARGIN, 36), "21 NOVEMBER 2026", font=f_date_b, fill=WHITE, anchor="ra")
    d.rectangle([0, 86, W, 90], fill=RED)

    # ---- Strip ----
    d.text((MARGIN, 100), "9 STORIES FROM ONE DAY", font=f_strip, fill=RED)
    d.text((W - MARGIN, 100), "Compiled from wire reports", font=f_date, fill=GREY, anchor="ra")
    d.line([(MARGIN, 122), (W - MARGIN, 122)], fill=HAIR, width=1)

    # ---- Map picture ----
    draw_map(d, MARGIN, 132, W - MARGIN, 372)

    # ---- Hero headline + summary + chips ----
    tx = MARGIN
    y = 388
    for ln in fit(d, HERO["headline"], f_hero_h, W - 2 * MARGIN, 2):
        d.text((tx, y), ln, font=f_hero_h, fill=INK)
        y += 40
    y += 2
    for ln in fit(d, HERO["summary"], f_hero_s, W - 2 * MARGIN, 2):
        d.text((tx, y), ln, font=f_hero_s, fill=(52, 52, 52))
        y += 20
    cx = tx
    cy = 520
    for chip in HERO["chips"]:
        cw = int(d.textlength(chip, font=f_chip)) + 20
        d.rounded_rectangle([cx, cy, cx + cw, cy + 24], radius=4,
                            outline=RED, width=1, fill=CREAM)
        d.text((cx + 10, cy + 5), chip, font=f_chip, fill=RED)
        cx += cw + 10

    # ---- By the numbers ----
    ny0, ny1 = 560, 636
    bw = (W - 2 * MARGIN - 3 * 16) // 4
    for i, (num, label) in enumerate(NUMBERS):
        bx0 = MARGIN + i * (bw + 16)
        d.rectangle([bx0, ny0, bx0 + bw, ny1], fill=CREAM, outline=HAIR)
        d.text((bx0 + 14, ny0 + 8), num, font=f_num, fill=RED)
        ly = ny0 + 44
        for ln in label.split("\n"):
            d.text((bx0 + 14, ly), ln, font=f_num_l, fill=GREY)
            ly += 14

    # ---- Two columns, four stories each ----
    col_w = (W - 2 * MARGIN - 24) // 2
    body_y = 650
    for i, (title, colour, stories) in enumerate(COLUMNS):
        x0 = MARGIN + i * (col_w + 24)
        d.rectangle([x0, body_y, x0 + 12, body_y + 12], fill=colour)
        d.text((x0 + 18, body_y - 2), title, font=f_col, fill=INK)
        d.line([(x0, body_y + 22), (x0 + col_w, body_y + 22)], fill=colour, width=3)
        y = body_y + 36
        for j, (head, summ) in enumerate(stories):
            for ln in fit(d, head, f_head, col_w, 2):
                d.text((x0, y), ln, font=f_head, fill=INK)
                y += 19
            for ln in fit(d, summ, f_sum, col_w, 2):
                d.text((x0, y), ln, font=f_sum, fill=GREY)
                y += 16
            y += 8
            if j < len(stories) - 1:
                d.line([(x0, y), (x0 + col_w, y)], fill=HAIR, width=1)
                y += 14
        assert y <= 972, f"column {title} overflow: {y}"

    # ---- Footer ----
    d.line([(MARGIN, 980), (W - MARGIN, 980)], fill=HAIR, width=1)
    d.text((W // 2, 988),
           "Compiled Saturday 21 November 2026 from wire reports  \u00b7  THE WORLD TODAY  \u00b7  make.fun news-image-20261121",
           font=f_foot, fill=GREY, anchor="ma")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
