#!/usr/bin/env python3
"""Draw entry.png for news-image-20261121: THE WORLD TODAY, Saturday 21 November 2026.

Fresh-authored in this session (2026-11-21). Clean newspaper layout: navy
masthead, one hero story, three region columns. Full-colour RGB, 1024x1024.
Stories verified against wire reports dated 21 Nov 2026 (event or first report).
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
COL_W = (W - 2 * MARGIN - 2 * 24) // 3  # 312
GAP = 24

NAVY = (14, 42, 71)
RED = (178, 34, 34)
INK = (22, 22, 22)
GREY = (84, 84, 84)
HAIR = (216, 216, 216)
HERO_BG = (253, 246, 236)
WHITE = (255, 255, 255)
BLUE = (29, 78, 137)
GREEN = (30, 122, 76)
DARKRED = (179, 38, 30)

F = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = F + "DejaVuSerif-Bold.ttf"
SANS = F + "DejaVuSans.ttf"
SANS_B = F + "DejaVuSans-Bold.ttf"

f_mast = ImageFont.truetype(SERIF_B, 46)
f_date_b = ImageFont.truetype(SANS_B, 21)
f_date = ImageFont.truetype(SANS, 13)
f_strip = ImageFont.truetype(SANS_B, 12)
f_hero_h = ImageFont.truetype(SANS_B, 29)
f_hero_s = ImageFont.truetype(SANS, 15)
f_chip = ImageFont.truetype(SANS_B, 12)
f_col = ImageFont.truetype(SANS_B, 14)
f_head = ImageFont.truetype(SANS_B, 14)
f_sum = ImageFont.truetype(SANS, 12)
f_foot = ImageFont.truetype(SANS, 11)


def wrap(draw, text, font, width):
    """Greedy word wrap by pixel width."""
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
        # trim last line with ellipsis until it fits
        while lines and draw.textlength(lines[-1] + "...", font=font) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


HERO = {
    "headline": "Russia fires ~100 missiles at Ukraine overnight; one lands in Poland",
    "summary": (
        "Eight people were killed in the barrage, including a seven-year-old in "
        "Kryvyi Rih. Warsaw says two missiles and a suspected drone came down on "
        "its soil while NATO drills ran nearby; France has called for an emergency "
        "UN Security Council meeting."
    ),
    "chips": ["~100 MISSILES", "8 KILLED", "POLAND HIT"],
}

COLUMNS = [
    ("EUROPE", BLUE, [
        ("EU to summon Russian envoy",
         "The EU will summon Moscow's envoy over damage to its Kyiv embassy, Kaja Kallas says."),
        ("Denmark: Russia plot to kill rapper",
         "Two Danes are charged over a foiled plot to kill Ukrainian rapper Kyivstoner; Moscow's attache expelled."),
        ("EU approves \u20ac1bn in arms aid",
         "EU ministers back joint weapons buying for Ukraine, deliveries due by end of 2027."),
        ("Estonia shuts its border",
         "Tallinn closes road crossings after a drone-plant attack; Moscow cries \u2018new Iron Curtain\u2019."),
        ("Moscow rejects US guarantees",
         "The Kremlin rebuffs a US proposal of NATO-like security guarantees for Ukraine."),
        ("COP31 runs into overtime",
         "Climate talks in Antalya pass their deadline, with the draft deal omitting any fossil-fuel phase-out."),
        ("Crimea bridge \u2018compromised\u2019",
         "Russia says the bridge's arch and girder were damaged; no repair date given."),
    ]),
    ("AMERICAS \u00b7 MIDDLE EAST", GREEN, [
        ("Trump dials in on Ukraine",
         "The US president joins a meeting of European allies after his Shenzhen talks with Putin and Xi."),
        ("Trump threatens tech penalties",
         "\u2018Tremendous penalties\u2019 for US firms that build data centres abroad, the president warns."),
        ("900,000 AI chips for China",
         "Washington approved the sale of close to 900,000 AI chips to China in six months, a House panel says."),
        ("US sanctions crime gangs",
         "Washington targets Italy's \u2018Ndrangheta and the Comancheros in a global crackdown."),
        ("Saudi intercepts Houthi missile",
         "Riyadh says it shot down a Houthi ballistic missile and drones; debris fell on the capital."),
        ("Six killed in Gaza strikes",
         "Israeli strikes kill six Palestinians, Gaza civil defence says, as the ceasefire frays."),
        ("China boosts S. China Sea ties",
         "Beijing says it will strengthen economic and security ties in the South China Sea."),
    ]),
    ("ASIA-PACIFIC \u00b7 WORLD", DARKRED, [
        ("Akvan: no major damage",
         "Odisha reports no major damage after landfall; 370,000 people had been evacuated."),
        ("India fight back in Wellington",
         "India reach 159 for one at stumps on day two of the first Test against New Zealand."),
        ("Japan, India deepen defence ties",
         "Tokyo and New Delhi agree closer military and arms-industry cooperation."),
        ("UN seeks $12bn for food aid",
         "The World Food Programme asks for $12bn to help 91 million people in 2027."),
        ("1,144 children killed in Ukraine",
         "UNICEF counts at least 1,144 children killed since Russia's invasion began."),
        ("Banks hit by vendor cyberattack",
         "JPMorgan, Visa and Mastercard report incidents at third-party providers; core networks unaffected."),
        ("UAE Bulls keep T10 crown",
         "The Bulls beat Yas Lions by 24 runs in Abu Dhabi to win a second straight T10 title."),
    ]),
]


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, W, 86], fill=NAVY)
    d.text((MARGIN, 18), "THE WORLD TODAY", font=f_mast, fill=WHITE)
    d.text((W - MARGIN, 16), "SATURDAY", font=f_date, fill=(200, 210, 220), anchor="ra")
    d.text((W - MARGIN, 36), "21 NOVEMBER 2026", font=f_date_b, fill=WHITE, anchor="ra")
    d.rectangle([0, 86, W, 90], fill=RED)

    # ---- Strip ----
    d.text((MARGIN, 100), "22 STORIES FROM ONE DAY", font=f_strip, fill=RED)
    d.text((W - MARGIN, 100), "Compiled from wire reports", font=f_date, fill=GREY, anchor="ra")
    d.line([(MARGIN, 122), (W - MARGIN, 122)], fill=HAIR, width=1)

    # ---- Hero ----
    hx0, hy0, hx1, hy1 = MARGIN, 132, W - MARGIN, 316
    d.rectangle([hx0, hy0, hx1, hy1], fill=HERO_BG)
    d.rectangle([hx0, hy0, hx0 + 6, hy1], fill=RED)
    tx = hx0 + 20
    lines = fit(d, HERO["headline"], f_hero_h, hx1 - tx - 16, 2)
    y = hy0 + 14
    for ln in lines:
        d.text((tx, y), ln, font=f_hero_h, fill=INK)
        y += 36
    slines = fit(d, HERO["summary"], f_hero_s, hx1 - tx - 16, 3)
    y += 2
    for ln in slines:
        d.text((tx, y), ln, font=f_hero_s, fill=(52, 52, 52))
        y += 20
    # chips
    cx = tx
    cy = hy1 - 34
    for chip in HERO["chips"]:
        cw = int(d.textlength(chip, font=f_chip)) + 20
        d.rounded_rectangle([cx, cy, cx + cw, cy + 24], radius=4,
                            outline=RED, width=1, fill=WHITE)
        d.text((cx + 10, cy + 5), chip, font=f_chip, fill=RED)
        cx += cw + 10

    # ---- Columns ----
    body_y = 332
    col_h = 640
    for i, (title, colour, stories) in enumerate(COLUMNS):
        x0 = MARGIN + i * (COL_W + GAP)
        # header
        d.rectangle([x0, body_y, x0 + 12, body_y + 12], fill=colour)
        d.text((x0 + 18, body_y - 2), title, font=f_col, fill=INK)
        d.line([(x0, body_y + 22), (x0 + COL_W, body_y + 22)], fill=colour, width=3)
        y = body_y + 34
        for j, (head, summ) in enumerate(stories):
            hlines = fit(d, head, f_head, COL_W, 2)
            for ln in hlines:
                d.text((x0, y), ln, font=f_head, fill=INK)
                y += 18
            slines = fit(d, summ, f_sum, COL_W, 3)
            for ln in slines:
                d.text((x0, y), ln, font=f_sum, fill=GREY)
                y += 16
            y += 10
            if j < len(stories) - 1:
                d.line([(x0, y), (x0 + COL_W, y)], fill=HAIR, width=1)
                y += 18
        # sanity: no overflow past footer
        assert y <= body_y + col_h + 8, f"column {title} overflow: {y}"

    # ---- Footer ----
    fy = 988
    d.line([(MARGIN, fy - 8), (W - MARGIN, fy - 8)], fill=HAIR, width=1)
    d.text((W // 2, fy), "Compiled Saturday 21 November 2026 from wire reports  \u00b7  THE WORLD TODAY  \u00b7  make.fun news-image-20261121",
           font=f_foot, fill=GREY, anchor="ma")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
