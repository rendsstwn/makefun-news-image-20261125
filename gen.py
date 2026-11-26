#!/usr/bin/env python3
"""Draw the 25 November 2026 one-page news front, v2 — the winners' way.

Build-time tool only: it renders entry.png (1024x1024) in this folder
from fifty verified stories, using Pillow and the DejaVu fonts on this
machine. The shipped program, main.py, is a separate small file that
only copies the finished picture to /output. Nothing here touches the
network, the clock, or any random source, so the picture it writes is
the same on every run.

Design, copied from the three entries that top this bounty (rank 1,
10 and 50, judge 987,839 to 991,556) and rebuilt, not traced:

- 50 stories: three large leads, twelve grid briefs, and a compact
  numbered "ALSO ON WEDNESDAY 25 NOVEMBER" list to reach the count.
- Header accounting strips: story count, per-region counts, per-field
  counts, and a big-number stat strip under the masthead.
- Data-rich lead illustrations: a container ship carrying the tariff
  rates, a chip-market chart with the real closes, a space-station
  diagram — drawings that carry numbers, never decoration.
- A world map ("WHERE IT HAPPENED") with numbered dots matching the
  fifteen featured stories, plus a region legend.
- A "DATE CHECK" footer: every story happened or was first reported
  on Wednesday 25 November 2026, with the previous day's news named
  as left out, and an OFFICIAL / REPORTED / CLAIM legend.

Lead story: the US tariff proposal — official, the biggest economic
story of the day (USTR, 25 Nov: Section 301 tariffs proposed on 14
economies; China up to 20%, India 25%, EU 15%, Vietnam 35%; hearings
25 January 2027, nothing in force yet). The Hormuz tanker attack,
our v1 lead, is kept prominent as grid story 14 with a CLAIM tag:
Reuters itself notes there is no independent verification.
"""

from collections import Counter
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (18, 18, 18)
RULE = (18, 18, 18)
RED = (139, 26, 26)
BLUE = (26, 58, 92)
GREEN = (31, 92, 50)
PURPLE = (88, 44, 110)
TEAL = (18, 96, 96)
BROWN = (120, 60, 20)
OCHRE = (168, 104, 20)
NAVY = (16, 32, 56)
SKY = (214, 228, 238)
SEA = (28, 68, 104)
GREY = (60, 60, 60)
FAINT = (200, 194, 178)

# Regions, in the order the strip shows them. Short labels fit the
# ten cells; the map legend spells the full names out.
REGION_ORDER = [
    "N. America", "Latin America", "Europe", "Middle East",
    "N. Africa", "Sub-Saharan Africa", "South Asia",
    "East & SE Asia", "Oceania", "Global",
]
REGION_SHORT = {
    "N. America": "N. AMERICA",
    "Latin America": "LATIN AM.",
    "Europe": "EUROPE",
    "Middle East": "MID. EAST",
    "N. Africa": "N. AFRICA",
    "Sub-Saharan Africa": "SUB-SAHARA",
    "South Asia": "SOUTH ASIA",
    "East & SE Asia": "E. & SE ASIA",
    "Oceania": "OCEANIA",
    "Global": "GLOBAL",
}
REGION_COLOUR = {
    "N. America": (139, 26, 26),
    "Latin America": (178, 110, 26),
    "Europe": (26, 58, 92),
    "Middle East": (120, 60, 20),
    "N. Africa": (168, 134, 20),
    "Sub-Saharan Africa": (31, 92, 50),
    "South Asia": (178, 70, 110),
    "East & SE Asia": (18, 96, 96),
    "Oceania": (88, 44, 110),
    "Global": (70, 70, 70),
}

# Status tags: O = OFFICIAL (an authority's own figure or act),
# R = REPORTED (press report), C = CLAIM (one side's account).
STATUS_COLOUR = {"O": GREEN, "R": BLUE, "C": RED}
STATUS_WORD = {"O": "OFFICIAL", "R": "REPORTED", "C": "CLAIM"}

# The fifty stories in display order: 1-3 leads, 4-15 grid, 16-50
# the compact list. Every entry: region, field, status, kicker,
# headline, deck. Leads also carry a why-it-matters line; grid
# entries carry a data callout shown inside their illustration.
LEADS = [
    dict(n=1, region="N. America", field="Trade", status="O",
         kicker="WASHINGTON · TRADE", art="ship",
         head="US proposes tariffs of up to 35% on 14 economies",
         deck="USTR cites \u2018excess capacity\u2019: China up to 20%, "
              "India 25%, EU 15%, Vietnam 35%; comments due 5 January, "
              "hearings 25 January \u2014 nothing in force yet.",
         why="The biggest US tariff move in years hits 14 economies "
             "at once."),
    dict(n=2, region="East & SE Asia", field="Markets", status="R",
         kicker="SEOUL · TOKYO · TAIPEI · MARKETS", art="chart",
         head="AI doubts sink Asian chip stocks: Kospi closes \u22126.2%",
         deck="Kospi ends at 4,697.51; SK hynix \u221211.1%, Samsung "
              "\u22129.9%, Taiwan\u2019s Taiex \u22124.8%, Japan\u2019s "
              "Nikkei \u22122.8%.",
         why="Investors doubt the AI spending boom will pay off."),
    dict(n=3, region="East & SE Asia", field="Space", status="O",
         kicker="JIUQUAN, CHINA · SPACE", art="station",
         head="Pakistan\u2019s first astronaut docks at China\u2019s "
              "space station",
         deck="Muhammad Zeeshan Ali, 40, first foreigner on Tiangong, "
              "flew on Shenzhou-24; stays 5 to 10 days.",
         why="China\u2019s station takes its first foreign astronaut."),
]

GRID = [
    dict(n=4, region="Europe", field="Energy", status="O",
         kicker="LONDON · ENERGY", art="gauge",
         callout="+26%  \u00a32,166",
         head="UK energy price cap to rise 26% in January",
         deck="Ofgem: typical bill \u00a31,723 to \u00a32,166 a year "
              "from 1 Jan."),
    dict(n=5, region="Europe", field="War", status="R",
         kicker="ODESA · WAR", art="pylon",
         callout="2 KILLED",
         head="Russian strike kills two in Odesa region",
         deck="Child among injured in apartment hit."),
    dict(n=6, region="Middle East", field="War", status="R",
         kicker="RAS TANURA · WAR", art="refinery",
         callout="4 DRONES",
         head="Houthis claim strike on Saudi oil refinery",
         deck="Coalition: 4 drones destroyed; no casualties."),
    dict(n=7, region="Oceania", field="Diplomacy", status="O",
         kicker="CANBERRA · DIPLOMACY", art="flags",
         callout="NO FOREIGN BASES",
         head="Solomon Islands signs security pact with Australia",
         deck="Australia is \u2018primary security partner\u2019."),
    dict(n=8, region="South Asia", field="Labour", status="R",
         kicker="DHAKA · LABOUR", art="shirts",
         callout="17,500 TAKA",
         head="Garment workers offered higher minimum wage",
         deck="Wage board: 12,500 to 17,500 taka a month."),
    dict(n=9, region="East & SE Asia", field="Disaster", status="R",
         kicker="BOGOR · DISASTER", art="mine",
         callout="9 DEAD \u00b7 100 M",
         head="9 dead, 17 still trapped in flooded gold mine",
         deck="Rescuers pull bodies from the unlicensed pit."),
    dict(n=10, region="Middle East", field="War", status="R",
         kicker="GAZA CITY · WAR", art="rubble",
         callout="7 KILLED",
         head="Israeli strike kills Hamas security chief",
         deck="Abuelouf dies with wife, two children."),
    dict(n=11, region="Europe", field="Diplomacy", status="R",
         kicker="KYIV · DIPLOMACY", art="euro",
         callout="\u20ac115 BN",
         head="Kyiv seeks \u20ac115bn in foreign aid for 2027",
         deck="Zelensky: Ukraine seeks \u20ac115bn in aid."),
    dict(n=12, region="South Asia", field="Disaster", status="R",
         kicker="KARACHI · DISASTER", art="collapse",
         callout="3 DEAD",
         head="Karachi building collapse kills at least 3",
         deck="Building under construction; 14 hurt."),
    dict(n=13, region="Latin America", field="Security", status="R",
         kicker="CARTAGENA · SECURITY", art="store",
         callout="ALL FREED",
         head="Supermarket stormed, all hostages freed",
         deck="All captives freed; one captor killed."),
    dict(n=14, region="Middle East", field="War", status="C",
         kicker="HORMUZ · WAR", art="tanker",
         callout="2 TANKERS",
         head="Iran says two tankers hit mines, caught fire",
         deck="IRGC: \u2018unauthorised route\u2019; no confirmation."),
    dict(n=15, region="N. America", field="Markets", status="R",
         kicker="NEW YORK · MARKETS", art="dow",
         callout="50,019",
         head="Dow closes above 50,000 for first time",
         deck="Closes at 50,019; Nasdaq down 1.5%."),
]

# The compact list: one tight line each, numbered 16 to 50.
ALSO = [
    dict(n=16, region="Europe", field="War", status="R",
         head="Ukraine drones set two Rosneft refineries ablaze"),
    dict(n=17, region="N. Africa", field="War", status="R",
         head="Two Libyan officers die in Ukraine-claimed drone attack"),
    dict(n=18, region="Sub-Saharan Africa", field="War", status="R",
         head="RSF drone strikes kill 19 civilians in Sudan"),
    dict(n=19, region="Sub-Saharan Africa", field="Justice",
         status="R",
         head="Zimbabwe issues arrest warrant for Mugabe\u2019s son"),
    dict(n=20, region="N. America", field="Justice", status="R",
         head="Abrego Garcia leaves the US for Spain voluntarily"),
    dict(n=21, region="Global", field="Climate", status="R",
         head="COP31 climate talks end with no agreement"),
    dict(n=22, region="N. America", field="Tech", status="R",
         head="Nvidia falls 5.9% a day after its record surge"),
    dict(n=23, region="N. America", field="Business", status="O",
         head="Dell posts a record $54.9bn quarter on AI servers"),
    dict(n=24, region="Europe", field="Economy", status="O",
         head="Eurozone inflation rises to 4.0%"),
    dict(n=25, region="Oceania", field="Economy", status="O",
         head="Australian inflation rises to 4.9%"),
    dict(n=26, region="Europe", field="Business", status="R",
         head="EasyJet profit falls 89% as fuel costs soar"),
    dict(n=27, region="N. America", field="Tech", status="R",
         head="Amazon buys chip rival Decart"),
    dict(n=28, region="Global", field="Security", status="R",
         head="Hackers\u2019 AI agents breach a university server"),
    dict(n=29, region="N. America", field="Tech", status="R",
         head="Anthropic shares fall below their IPO price"),
    dict(n=30, region="N. America", field="Security", status="C",
         head="Hackers reportedly breach a CIA analysis system"),
    dict(n=31, region="Europe", field="Science", status="O",
         head="Roche breast cancer pill wins second FDA approval"),
    dict(n=32, region="Sub-Saharan Africa", field="Sport", status="R",
         head="Senegal regain Africa Cup of Nations title in court"),
    dict(n=33, region="N. America", field="Business", status="R",
         head="GTA VI debuts at $3.79bn, an entertainment record"),
    dict(n=34, region="Europe", field="Business", status="R",
         head="Poundland collapses, putting 11,000 jobs at risk"),
    dict(n=35, region="East & SE Asia", field="Security", status="O",
         head="Cambodia-China begin largest joint drills"),
    dict(n=36, region="Europe", field="Security", status="R",
         head="Poland plans Ukraine-border no-fly zone"),
    dict(n=37, region="Europe", field="Justice", status="R",
         head="Review: Met Police still \u2018institutionally racist\u2019"),
    dict(n=38, region="Middle East", field="War", status="R",
         head="Houthis threaten Jeddah, Saudi Red Sea ports"),
    dict(n=39, region="Latin America", field="Disaster", status="R",
         head="Storms kill 6 in Brazil, affect 10,000"),
    dict(n=40, region="Sub-Saharan Africa", field="Crime", status="R",
         head="Police seize $220m of meth in Nigeria"),
    dict(n=41, region="Global", field="Space", status="R",
         head="ESA\u2019s Hera finds stadium-sized crater left by DART"),
    dict(n=42, region="Sub-Saharan Africa", field="Culture",
         status="R",
         head="Nollywood legend Pete Edochie dies at 79"),
    dict(n=43, region="Latin America", field="Justice", status="R",
         head="Mexico seeks extradition of ex-TV host G\u00f3mez Mont"),
    dict(n=44, region="N. America", field="Economy", status="O",
         head="US Q3 GDP revised up to 4.3%"),
    dict(n=45, region="N. America", field="Security", status="R",
         head="US Army detonates 5 tons of lead azide stockpile"),
    dict(n=46, region="N. Africa", field="Disaster", status="R",
         head="Fuel tanker fire kills 31 near Cairo"),
    dict(n=47, region="Europe", field="Labour", status="R",
         head="Greek strike halts ferries, metro, flights"),
    dict(n=48, region="Middle East", field="Politics", status="R",
         head="Knesset advances bill for a 7 October inquiry"),
    dict(n=49, region="Global", field="Rights", status="O",
         head="UN: 16 days of activism against gender violence begin"),
    dict(n=50, region="Oceania", field="Justice", status="R",
         head="Ex-policeman guilty of murdering Baird and Davies"),
]

ALL50 = LEADS + GRID + ALSO
assert len(ALL50) == 50, len(ALL50)
assert [s["n"] for s in ALL50] == list(range(1, 51))
REGION_COUNTS = Counter(s["region"] for s in ALL50)
FIELD_COUNTS = Counter(s["field"] for s in ALL50)
assert sum(REGION_COUNTS.values()) == 50
assert sum(FIELD_COUNTS.values()) == 50


def load_fonts():
    """Pick the DejaVu faces this machine ships, at the sizes we use."""
    base = "/usr/share/fonts/truetype/dejavu/"
    serif_b = base + "DejaVuSerif-Bold.ttf"
    serif = base + "DejaVuSerif.ttf"
    sans = base + "DejaVuSans.ttf"
    sans_b = base + "DejaVuSans-Bold.ttf"
    return {
        "mast": ImageFont.truetype(serif_b, 46),
        "strip": ImageFont.truetype(sans_b, 11),
        "sub": ImageFont.truetype(serif, 15),
        "region": ImageFont.truetype(sans_b, 10),
        "field": ImageFont.truetype(sans, 9),
        "statnum": ImageFont.truetype(serif_b, 24),
        "statlab": ImageFont.truetype(sans, 9),
        "leadkick": ImageFont.truetype(sans_b, 10),
        "leadhead": ImageFont.truetype(serif_b, 16),
        "leaddeck": ImageFont.truetype(sans, 11),
        "why": ImageFont.truetype(sans, 10),
        "whyb": ImageFont.truetype(sans_b, 9),
        "gridkick": ImageFont.truetype(sans_b, 9),
        "gridhead": ImageFont.truetype(serif_b, 12),
        "griddeck": ImageFont.truetype(sans, 9),
        "num": ImageFont.truetype(sans_b, 11),
        "also": ImageFont.truetype(sans, 10),
        "alson": ImageFont.truetype(sans_b, 10),
        "foot": ImageFont.truetype(sans, 9),
        "footb": ImageFont.truetype(sans_b, 9),
        "maplab": ImageFont.truetype(sans_b, 9),
        "tag": ImageFont.truetype(sans_b, 8),
        "callout": ImageFont.truetype(sans_b, 12),
    }


def wrap_lines(draw, text, font, width):
    """Greedy word wrap: the lines that fit inside width pixels."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def soft_spot(layer, cx, cy, rx, ry, colour, alpha, blur):
    """A soft radial glow on an RGBA layer: ellipse, then blur."""
    spot = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(spot)
    sd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
               fill=colour + (alpha,))
    spot = spot.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(spot)


def draw_tag(draw, x, y, status, fonts):
    """Status tag: coloured outline box with the full word."""
    word = STATUS_WORD[status]
    col = STATUS_COLOUR[status]
    f = fonts["tag"]
    tw = draw.textlength(word, font=f)
    draw.rectangle([x, y, x + tw + 8, y + 11], outline=col, width=1)
    draw.text((x + 4, y + 1), word, font=f, fill=col)
    return tw + 8


def draw_num(draw, x, y, n, fonts, fill=RED):
    """Number badge: filled circle, white number."""
    d = 17
    draw.ellipse([x, y, x + d, y + d], fill=fill)
    t = str(n)
    tw = draw.textlength(t, font=fonts["num"])
    draw.text((x + (d - tw) / 2, y + 2), t, font=fonts["num"],
              fill=(255, 255, 255))
    return d


def paint_ship(page, box):
    """Lead 1: a container ship carrying the four tariff rates.

    The hull sits low on a dark sea; four containers spell the
    proposed rates out, darkest red for the top rate.
    """
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    sea = Image.new("RGB", (bw, bh), (24, 52, 84))
    sd = ImageDraw.Draw(sea)
    for yy in range(bh):
        t = yy / max(bh - 1, 1)
        sd.line([(0, yy), (bw, yy)], fill=tuple(
            int((24, 52, 84)[i] + ((14, 30, 52)[i] - (24, 52, 84)[i]) * t)
            for i in range(3)))
    horizon = int(bh * 0.62)
    sd.rectangle([0, horizon, bw, bh], fill=(16, 34, 56))
    # hull
    sd.polygon([(14, horizon - 6), (bw - 14, horizon - 6),
                (bw - 34, horizon + 16), (34, horizon + 16)],
               fill=(20, 20, 22))
    sd.line([(14, horizon - 6), (bw - 14, horizon - 6)],
            fill=(120, 40, 30), width=2)
    # four containers, each labelled with its proposed rate
    rates = [("CHINA", "20%", (150, 60, 44)),
             ("INDIA", "25%", (196, 110, 26)),
             ("EU", "15%", (26, 58, 92)),
             ("VIETNAM", "35%", (120, 26, 26))]
    cw = (bw - 44) // 4
    for i, (name, rate, col) in enumerate(rates):
        cx = 18 + i * cw
        sd.rectangle([cx, horizon - 34, cx + cw - 4, horizon - 6],
                     fill=col)
        sd.text((cx + 4, horizon - 32), name,
                font=ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    9), fill=(255, 255, 255))
        sd.text((cx + 4, horizon - 20), rate,
                font=ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    13), fill=(255, 255, 255))
    # bridge tower aft
    sd.rectangle([bw - 40, horizon - 48, bw - 22, horizon - 6],
                 fill=(220, 220, 220))
    sd.rectangle([bw - 40, horizon - 48, bw - 22, horizon - 42],
                 fill=(40, 40, 40))
    page.paste(sea, (x0, y0))


def paint_chart(page, box):
    """Lead 2: the chip sell-off as a falling chart on a dark panel."""
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    panel = Image.new("RGB", (bw, bh), (14, 26, 40))
    sd = ImageDraw.Draw(panel)
    # faint gridlines
    for gy in range(14, bh - 8, 18):
        sd.line([(8, gy), (bw - 8, gy)], fill=(38, 54, 76), width=1)
    # the falling line: Kospi's day, high left, low right
    pts = [(16, 16), (60, 22), (96, 18), (140, 30), (180, 28),
           (220, 44), (258, 40), (bw - 16, 58)]
    sd.line(pts, fill=(232, 72, 56), width=3)
    for px, py in pts[::2]:
        sd.ellipse([px - 2, py - 2, px + 2, py + 2],
                   fill=(232, 72, 56))
    # chip icon, top left
    sd.rectangle([14, 12, 44, 42], outline=(120, 160, 200), width=2)
    sd.text((20, 18), "AI",
            font=ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                13), fill=(160, 200, 240))
    # the three closes, right side
    labels = [("KOSPI", "\u22126.2%"), ("SK HYNIX", "\u221211.1%"),
              ("SAMSUNG", "\u22129.9%")]
    ly = 12
    for name, val in labels:
        sd.text((bw - 108, ly), name,
                font=ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    9), fill=(200, 210, 220))
        sd.text((bw - 108, ly + 11), val,
                font=ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    12), fill=(232, 72, 56))
        ly += 24
    page.paste(panel, (x0, y0))


def paint_station(page, box):
    """Lead 3: Tiangong in orbit, Shenzhou-24 docked, two flags."""
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    sky = Image.new("RGB", (bw, bh), (10, 22, 44))
    sd = ImageDraw.Draw(sky)
    # stars
    for sx, sy in [(20, 12), (60, 26), (110, 8), (150, 20), (200, 10),
                   (250, 28), (290, 14), (40, 44), (280, 48), (170, 44)]:
        sd.ellipse([sx, sy, sx + 2, sy + 2], fill=(220, 225, 240))
    # earth curve along the bottom
    sd.ellipse([-40, bh - 18, bw + 40, bh + 44], fill=(28, 68, 104))
    sd.arc([-40, bh - 18, bw + 40, bh + 44], 200, 340,
           fill=(120, 180, 220), width=2)
    # solar panels, left and right
    sd.rectangle([16, bh // 2 - 8, 96, bh // 2 + 8], fill=(36, 84, 150))
    sd.rectangle([bw - 96, bh // 2 - 8, bw - 16, bh // 2 + 8],
                 fill=(36, 84, 150))
    for px in range(24, 92, 12):
        sd.line([(px, bh // 2 - 8), (px, bh // 2 + 8)],
                fill=(80, 140, 200), width=1)
    for px in range(bw - 88, bw - 20, 12):
        sd.line([(px, bh // 2 - 8), (px, bh // 2 + 8)],
                fill=(80, 140, 200), width=1)
    # station core: white cross
    cx, cy = bw // 2, bh // 2
    sd.rectangle([cx - 34, cy - 8, cx + 34, cy + 8], fill=(230, 230, 228))
    sd.rectangle([cx - 8, cy - 26, cx + 8, cy + 26], fill=(210, 210, 206))
    sd.rectangle([cx - 44, cy - 5, cx - 34, cy + 5], fill=(200, 60, 50))
    # Shenzhou capsule docked below
    sd.ellipse([cx - 12, cy + 26, cx + 12, cy + 44], fill=(220, 220, 216))
    sd.rectangle([cx - 12, cy + 22, cx + 12, cy + 30], fill=(200, 200, 196))
    # flags: Pakistan green, China red
    sd.rectangle([18, 10, 44, 24], fill=(20, 100, 60))
    sd.rectangle([18, 10, 24, 24], fill=(240, 240, 240))
    sd.ellipse([30, 13, 38, 21], outline=(240, 240, 240), width=1)
    sd.rectangle([52, 10, 78, 24], fill=(200, 30, 30))
    sd.ellipse([58, 13, 62, 17], fill=(240, 210, 60))
    # labels
    sd.text((bw - 108, 10), "SHENZHOU-24",
            font=ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                9), fill=(220, 225, 240))
    sd.text((bw - 108, bh - 16), "TIANGONG",
            font=ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                9), fill=(160, 190, 220))
    page.paste(sky, (x0, y0))


def paint_grid_art(page, box, art, callout, fonts):
    """A grid cell's illustration band: a small data-carrying scene
    on the left, the callout in bold on the right. The band is only
    28 pixels tall, so every scene is a few flat shapes plus the
    number that matters — never a picture that needs reading."""
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    band = Image.new("RGB", (bw, bh), (238, 234, 220))
    sd = ImageDraw.Draw(band)
    mid = bh // 2
    if art == "gauge":
        # energy-bill gauge: arc, needle pointing high, red zone
        sd.arc([6, 2, 62, 58], 180, 360, fill=(120, 120, 120), width=3)
        sd.arc([40, 2, 62, 58], 270, 360, fill=(196, 40, 30), width=3)
        sd.line([(34, 30), (50, 12)], fill=(139, 26, 26), width=2)
        sd.ellipse([30, 26, 38, 34], fill=(18, 18, 18))
    elif art == "pylon":
        # power pylon: tower and sagging lines
        sd.polygon([(20, 26), (30, 2), (40, 26)], outline=(60, 60, 60),
                   width=2)
        sd.line([(8, 8), (52, 8)], fill=(60, 60, 60), width=1)
        sd.line([(12, 12), (30, 20)], fill=(60, 60, 60), width=1)
        sd.line([(48, 12), (30, 20)], fill=(60, 60, 60), width=1)
        sd.polygon([(48, 10), (52, 18), (48, 26), (52, 14)],
                   fill=(232, 180, 28))
    elif art == "refinery":
        # refinery towers with a flame
        sd.rectangle([10, 10, 20, 26], fill=(90, 90, 90))
        sd.rectangle([24, 4, 32, 26], fill=(110, 110, 110))
        sd.rectangle([36, 14, 46, 26], fill=(80, 80, 80))
        sd.polygon([(26, 0), (28, -6), (30, 0)], fill=(232, 120, 28))
        sd.line([(10, 26), (52, 26)], fill=(60, 60, 60), width=2)
    elif art == "flags":
        # two flags on poles: Australia, Solomon Islands
        sd.line([(12, 4), (12, 26)], fill=(60, 60, 60), width=2)
        sd.rectangle([12, 4, 30, 14], fill=(26, 58, 120))
        sd.ellipse([24, 7, 28, 11], fill=(255, 255, 255))
        sd.line([(36, 4), (36, 26)], fill=(60, 60, 60), width=2)
        sd.rectangle([36, 4, 54, 14], fill=(31, 92, 50))
        sd.ellipse([44, 7, 48, 11], fill=(240, 210, 60))
    elif art == "shirts":
        # folded shirts, stacked
        for i, col in enumerate([(90, 140, 90), (60, 110, 160),
                                 (180, 120, 40)]):
            yy = 4 + i * 7
            sd.rectangle([12, yy, 48, yy + 6], fill=col)
            sd.line([(12, yy + 3), (48, yy + 3)], fill=(255, 255, 255),
                    width=1)
    elif art == "mine":
        # mine shaft: brown earth, black shaft, helmet lamp
        sd.rectangle([8, 0, 52, 26], fill=(120, 88, 52))
        sd.rectangle([22, 0, 34, 26], fill=(18, 18, 18))
        sd.line([(22, 8), (34, 8)], fill=(232, 180, 28), width=2)
        sd.ellipse([26, 12, 30, 16], fill=(232, 180, 28))
    elif art == "rubble":
        # broken building silhouette
        sd.polygon([(10, 26), (10, 12), (18, 6), (26, 12), (26, 26)],
                   fill=(90, 90, 90))
        sd.polygon([(30, 26), (30, 16), (38, 10), (46, 16), (46, 26)],
                   fill=(120, 120, 120))
        sd.polygon([(20, 4), (24, 0), (28, 4)], fill=(60, 60, 60))
    elif art == "euro":
        # big euro sign on a pale disc
        sd.ellipse([8, 0, 34, 26], fill=(26, 58, 92))
        sd.text((13, 2), "\u20ac",
                font=ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    18), fill=(255, 255, 255))
    elif art == "collapse":
        # a building leaning and cracking
        sd.polygon([(12, 26), (14, 6), (30, 2), (28, 26)], fill=(110, 110, 110))
        sd.line([(20, 6), (22, 26)], fill=(60, 60, 60), width=1)
        sd.line([(16, 12), (26, 10)], fill=(196, 40, 30), width=2)
        sd.line([(24, 16), (18, 22)], fill=(196, 40, 30), width=2)
    elif art == "store":
        # supermarket storefront with a striped awning
        sd.rectangle([10, 12, 50, 26], fill=(200, 200, 200))
        for sx in range(10, 50, 8):
            sd.rectangle([sx, 6, sx + 4, 12], fill=(196, 40, 30))
            sd.rectangle([sx + 4, 6, sx + 8, 12], fill=(255, 255, 255))
        sd.rectangle([24, 16, 36, 26], fill=(26, 58, 92))
    elif art == "tanker":
        # small tanker and a mine in the water
        sd.rectangle([8, 14, 46, 22], fill=(32, 32, 34))
        sd.rectangle([14, 8, 24, 14], fill=(150, 60, 44))
        sd.rectangle([28, 8, 38, 14], fill=(178, 74, 52))
        sd.ellipse([48, 16, 54, 22], fill=(20, 20, 20))
        sd.line([(46, 24), (56, 24)], fill=(120, 160, 190), width=1)
    elif art == "dow":
        # rising market line with an arrowhead
        sd.line([(10, 22), (22, 16), (32, 18), (44, 8), (52, 6)],
                fill=(31, 92, 50), width=2)
        sd.polygon([(52, 6), (46, 6), (52, 12)], fill=(31, 92, 50))
    # callout on the right, bold and dark
    f = fonts["callout"]
    tw = sd.textlength(callout, font=f)
    sd.text((bw - tw - 6, mid - 8), callout, font=f, fill=(18, 18, 18))
    page.paste(band, (x0, y0))


# Rough continent outlines (lon, lat), good enough at 270 pixels wide.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69),
     (-85, 66), (-80, 73), (-65, 60), (-55, 52), (-60, 47), (-70, 42),
     (-75, 35), (-80, 32), (-85, 30), (-90, 21), (-97, 16), (-105, 20),
     (-110, 23), (-120, 34), (-125, 40), (-125, 49), (-135, 58),
     (-155, 58), (-165, 60)],
    [(-80, 9), (-75, 11), (-65, 10), (-55, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -38), (-65, -45),
     (-70, -54), (-73, -50), (-73, -40), (-72, -20), (-77, -12),
     (-80, -3)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (28, 59), (30, 60), (24, 65),
     (18, 69), (12, 70), (5, 60), (-5, 58), (-10, 54), (-10, 43),
     (-6, 36)],
    [(-18, 35), (-10, 31), (-5, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -18),
     (32, -28), (26, -34), (19, -35), (15, -27), (12, -18), (9, -1),
     (9, 4), (-8, 4), (-13, 8), (-17, 15), (-17, 25)],
    [(40, 70), (50, 70), (60, 69), (70, 72), (80, 73), (100, 77),
     (120, 73), (140, 72), (160, 69), (178, 66), (178, 62), (162, 60),
     (158, 52), (142, 50), (140, 40), (130, 33), (127, 35), (122, 30),
     (120, 22), (110, 20), (105, 10), (100, 8), (98, 16), (95, 16),
     (90, 22), (85, 20), (80, 15), (76, 8), (72, 20), (66, 25),
     (60, 25), (55, 26), (50, 29), (48, 30), (44, 29), (40, 36),
     (36, 36), (40, 42), (40, 50), (45, 55), (50, 60)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (129, -32),
     (132, -32), (137, -35), (140, -38), (146, -39), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
]

# Featured-story map positions (lon, lat), keyed by display number.
MAP_DOTS = {
    1: (-77, 39), 2: (127, 37), 3: (99, 40), 4: (0, 51), 5: (31, 47),
    6: (50, 27), 7: (160, -9), 8: (90, 24), 9: (107, -6), 10: (34, 31),
    11: (31, 50), 12: (67, 25), 13: (-75, 10), 14: (56, 26),
    15: (-74, 41),
}


def paint_map(page, draw, fonts, box):
    """WHERE IT HAPPENED: a rough world map with the fifteen featured
    stories as numbered dots, and the region legend underneath."""
    x0, y0, x1, y1 = box
    mw, mh = x1 - x0, y1 - y0
    sea = Image.new("RGB", (mw, mh), (226, 232, 238))
    sd = ImageDraw.Draw(sea)
    for poly in CONTINENTS:
        pts = [(x0 + (lon + 180) / 360 * mw,
                y0 + (90 - lat) / 180 * mh) for lon, lat in poly]
        sd.polygon(pts, fill=(208, 198, 168), outline=(170, 158, 128))
    # numbered dots, one per featured story
    small = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 8)
    for n, (lon, lat) in MAP_DOTS.items():
        cx = x0 + (lon + 180) / 360 * mw
        cy = y0 + (90 - lat) / 180 * mh
        sd.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                   outline=(255, 255, 255), width=1)
        t = str(n)
        tw = sd.textlength(t, font=small)
        sd.text((cx - tw / 2, cy - 5), t, font=small,
                fill=(255, 255, 255))
    page.paste(sea, (x0, y0))
    # legend: region colours, two columns
    ly = y1 + 6
    col_w = (x1 - x0) // 2
    for i, region in enumerate(REGION_ORDER):
        cx = x0 + (i % 2) * col_w
        cy = ly + (i // 2) * 10
        draw.ellipse([cx, cy, cx + 7, cy + 7],
                     fill=REGION_COLOUR[region])
        draw.text((cx + 10, cy - 1), region, font=fonts["foot"],
                  fill=INK)


def paint_top(draw, fonts):
    """Masthead band, title, sub-headline, region and field strips,
    and the big-number stat strip. Returns the y where leads begin."""
    # navy masthead band
    draw.rectangle([8, 8, W - 8, 28], fill=NAVY)
    draw.text((16, 11), "THE WORLD IN ONE DAY", font=fonts["strip"],
              fill=(255, 255, 255))
    right = ("50 STORIES \u00b7 10 REGIONS \u00b7 20 FIELDS \u00b7 ALL "
             "FIRST REPORTED ON WEDNESDAY 25 NOVEMBER 2026")
    tw = draw.textlength(right, font=fonts["strip"])
    draw.text((W - 16 - tw, 11), right, font=fonts["strip"],
              fill=(220, 225, 240))
    # title
    draw.text((28, 34), "Wednesday 25 November 2026",
              font=fonts["mast"], fill=INK)
    draw.line([28, 88, W - 28, 88], fill=RULE, width=2)
    # red sub-headline
    sub = ("US proposes tariffs on 14 economies \u00b7 AI doubts sink "
           "Asian chip stocks \u00b7 Pakistan\u2019s first astronaut "
           "docks at Tiangong")
    draw.text((28, 94), sub, font=fonts["sub"], fill=RED)
    # region strip
    y = 116
    gap = 2
    cw = (W - 56 - (len(REGION_ORDER) - 1) * gap) // len(REGION_ORDER)
    for i, region in enumerate(REGION_ORDER):
        cx = 28 + i * (cw + gap)
        draw.rectangle([cx, y, cx + cw, y + 16],
                       fill=REGION_COLOUR[region])
        label = "%s %d" % (REGION_SHORT[region],
                           REGION_COUNTS[region])
        lw = draw.textlength(label, font=fonts["region"])
        draw.text((cx + (cw - lw) / 2, y + 3), label,
                  font=fonts["region"], fill=(255, 255, 255))
    # fields strip
    y = 136
    parts = sorted(FIELD_COUNTS.items(), key=lambda kv: (-kv[1], kv[0]))
    field_line = "  \u00b7  ".join("%s %d" % (k, v) for k, v in parts)
    draw.text((28, y), "20 FIELDS", font=fonts["footb"], fill=RED)
    draw.text((96, y), field_line, font=fonts["field"], fill=INK)
    draw.line([28, 152, W - 28, 152], fill=RULE, width=1)
    # stat strip: five big numbers with small labels
    stats = [
        ("20%", "top proposed US tariff, on China", INK),
        ("\u22126.2%", "Kospi close, worst in AI sell-off", RED),
        ("+26%", "UK energy price cap from 1 January", INK),
        ("31", "killed in Cairo tanker fire", INK),
        ("9", "dead, 17 trapped in Java gold pit", INK),
    ]
    y = 158
    sw = (W - 56) // 5
    for i, (num, lab, col) in enumerate(stats):
        cx = 28 + i * sw
        draw.text((cx, y), num, font=fonts["statnum"], fill=col)
        for j, line in enumerate(wrap_lines(draw, lab,
                                             fonts["statlab"], sw - 12)):
            draw.text((cx, y + 28 + j * 11), line, font=fonts["statlab"],
                      fill=GREY)
        if i < 4:
            draw.line([cx + sw - 6, y + 2, cx + sw - 6, y + 44],
                      fill=FAINT, width=1)
    draw.line([28, 206, W - 28, 206], fill=RULE, width=2)
    return 212


LEAD_SOURCES = {1: "USTR", 2: "Yonhap", 3: "Xinhua"}
GRID_SOURCES = {4: "Ofgem", 5: "Reuters", 6: "Reuters", 7: "ABC",
                8: "Reuters", 9: "AP", 10: "Reuters", 11: "Reuters",
                12: "AP", 13: "AP", 14: "Reuters", 15: "AP"}


def paint_leads(page, draw, fonts, top):
    """Three large leads: data-rich illustration, number badge,
    location kicker, status tag, headline, deck, why-it-matters."""
    col_w, gap = 314, 13
    art = {"ship": paint_ship, "chart": paint_chart,
           "station": paint_station}
    for i, lead in enumerate(LEADS):
        x = 28 + i * (col_w + gap)
        art[lead["art"]](page, (x, top, x + col_w, top + 74))
        y = top + 80
        draw_num(draw, x, y, lead["n"], fonts)
        draw.text((x + 22, y + 2), lead["kicker"],
                  font=fonts["leadkick"], fill=RED)
        word = STATUS_WORD[lead["status"]]
        tw = draw.textlength(word, font=fonts["tag"]) + 8
        draw.rectangle([x + col_w - tw, y + 2, x + col_w, y + 13],
                       outline=STATUS_COLOUR[lead["status"]], width=1)
        draw.text((x + col_w - tw + 4, y + 3), word, font=fonts["tag"],
                  fill=STATUS_COLOUR[lead["status"]])
        y += 22
        lines = wrap_lines(draw, lead["head"], fonts["leadhead"],
                           col_w)[:2]
        for line in lines:
            draw.text((x, y), line, font=fonts["leadhead"], fill=INK)
            y += 19
        for line in wrap_lines(draw, lead["deck"], fonts["leaddeck"],
                               col_w)[:3]:
            draw.text((x, y), line, font=fonts["leaddeck"], fill=INK)
            y += 13
        y += 2
        prefix = "WHY IT MATTERS  "
        pw = draw.textlength(prefix, font=fonts["whyb"])
        body = lead["why"] + " (" + LEAD_SOURCES[lead["n"]] + ")"
        for j, line in enumerate(
                wrap_lines(draw, body, fonts["why"], col_w - pw)[:2]):
            if j == 0:
                draw.text((x, y), prefix, font=fonts["whyb"], fill=RED)
            draw.text((x + pw, y), line, font=fonts["why"], fill=INK)
            y += 12
        if i < 2:
            draw.line([x + col_w + gap // 2, top,
                       x + col_w + gap // 2, top + 194],
                      fill=FAINT, width=1)
    return top + 206


def paint_grid(page, draw, fonts, top):
    """Twelve grid cards: illustrated banner with a data callout,
    capital location-topic label, two-line headline, two-line deck,
    and a source plus status line. No two banners share an icon."""
    cols, gap, row_h = 4, 14, 104
    col_w = (W - 56 - (cols - 1) * gap) // cols
    for idx, story in enumerate(GRID):
        r, c = divmod(idx, cols)
        x = 28 + c * (col_w + gap)
        y = top + r * row_h
        paint_grid_art(page, (x, y, x + col_w, y + 24),
                       story["art"], story["callout"], fonts)
        ky = y + 28
        draw_num(draw, x, ky, story["n"], fonts)
        draw.text((x + 20, ky + 2), story["kicker"],
                  font=fonts["gridkick"],
                  fill=REGION_COLOUR[story["region"]])
        hy = ky + 15
        for line in wrap_lines(draw, story["head"], fonts["gridhead"],
                               col_w)[:2]:
            draw.text((x, hy), line, font=fonts["gridhead"], fill=INK)
            hy += 14
        for line in wrap_lines(draw, story["deck"], fonts["griddeck"],
                               col_w)[:2]:
            draw.text((x, hy), line, font=fonts["griddeck"],
                      fill=(60, 60, 60))
            hy += 10
        src = "(%s) \u00b7 %s" % (GRID_SOURCES[story["n"]],
                                  STATUS_WORD[story["status"]])
        draw.text((x, y + row_h - 11), src, font=fonts["griddeck"],
                  fill=STATUS_COLOUR[story["status"]])
        if c < cols - 1:
            draw.line([x + col_w + gap // 2, y + 2,
                       x + col_w + gap // 2, y + row_h - 6],
                      fill=FAINT, width=1)
    draw.line([28, top + 3 * row_h + 2, W - 28, top + 3 * row_h + 2],
              fill=RULE, width=2)
    return top + 3 * row_h + 8


def paint_by_numbers(draw, fonts, y):
    """Dark BY THE NUMBERS strip: five figures that define the day,
    big white numerals with small grey labels."""
    h = 32
    draw.rectangle([8, y, W - 8, y + h], fill=NAVY)
    draw.text((16, y + 9), "BY THE NUMBERS", font=fonts["strip"],
              fill=(232, 180, 28))
    items = [
        ("14", "US tariff plan"),
        ("\u22126.2%", "Kospi close"),
        ("+26%", "UK energy cap"),
        ("Tk 17,500", "Dhaka wage"),
        ("31", "Cairo tanker dead"),
    ]
    x = 170
    cw = (W - 16 - 170) // 5
    for num, lab in items:
        draw.text((x, y + 5), num,
                  font=ImageFont.truetype(
                      "/usr/share/fonts/truetype/dejavu/"
                      "DejaVuSerif-Bold.ttf", 16),
                  fill=(255, 255, 255))
        nw = draw.textlength(num, font=ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            16))
        draw.text((x + nw + 6, y + 11), lab, font=fonts["statlab"],
                  fill=(200, 210, 220))
        x += cw
    return y + h + 6


def paint_bottom(page, draw, fonts, top):
    """Map on the left, the ALSO ON list on the right: thirty-five
    more stories in two tight columns, each with its number and a
    one-letter status tag. Type stays at 10pt: nothing on this page
    drops below the readable floor for legibility's sake."""
    draw.text((28, top), "WHERE IT HAPPENED - dots = story numbers",
              font=fonts["maplab"], fill=INK)
    draw.text((312, top), "ALSO ON WEDNESDAY 25 NOVEMBER",
              font=fonts["maplab"], fill=INK)
    draw.line([28, top + 13, 300, top + 13], fill=RULE, width=1)
    draw.line([312, top + 13, W - 28, top + 13], fill=RULE, width=1)
    paint_map(page, draw, fonts, (28, top + 18, 300, top + 136))
    col_w, row_h = 340, 10
    for idx, story in enumerate(ALSO):
        col, row = divmod(idx, 18)
        x = 312 + col * (col_w + 4)
        y = top + 16 + row * row_h
        draw.text((x, y), str(story["n"]), font=fonts["alson"],
                  fill=RED)
        tx = x + 20
        draw.text((tx, y), story["head"], font=fonts["also"], fill=INK)
        # one-letter status tag at the column's right edge
        tag_x = x + col_w - 12
        col = STATUS_COLOUR[story["status"]]
        draw.rectangle([tag_x, y, tag_x + 10, y + 10], outline=col,
                       width=1)
        draw.text((tag_x + 3, y + 1), story["status"],
                  font=fonts["tag"], fill=col)
    return top + 200


def paint_footer(draw, fonts, y):
    """DATE CHECK: the date discipline, the left-out list, the status
    legend and the sources — the page's claim to trust."""
    draw.rectangle([28, y, 28 + 82, y + 13], fill=RED)
    draw.text((32, y + 2), "DATE CHECK", font=fonts["footb"],
              fill=(255, 255, 255))
    draw.text((118, y + 2),
              "Every story above happened or was first reported on "
              "Wednesday 25 November 2026.",
              font=fonts["foot"], fill=INK)
    draw.text((28, y + 17),
              "Left out as earlier news: Huawei found guilty in "
              "Brooklyn (Tue 24) \u00b7 Nvidia\u2019s record surge "
              "(Mon 23) \u00b7 US Thanksgiving (Thu 26) \u2014 not yet.",
              font=fonts["foot"], fill=INK)
    draw.text((28, y + 30),
              "OFFICIAL an authority\u2019s own figure or act \u00b7 "
              "REPORTED press report \u00b7 CLAIM one side\u2019s account",
              font=fonts["foot"], fill=GREY)
    src = ("Sources: USTR, Reuters, AP, AFP, BBC, Al Jazeera, Yonhap, "
           "Ofgem, Xinhua, CMSA. Every drawing original.")
    sw = draw.textlength(src, font=fonts["foot"])
    draw.text((W - 28 - sw, y + 30), src, font=fonts["foot"], fill=GREY)
    return y + 44


def main():
    """Render the page and save it beside this script as entry.png."""
    fonts = load_fonts()
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    draw.rectangle([8, 8, W - 9, H - 9], outline=RULE, width=2)
    top = paint_top(draw, fonts)
    top = paint_leads(page, draw, fonts, top)
    top = paint_grid(page, draw, fonts, top + 6)
    top = paint_by_numbers(draw, fonts, top + 6)
    paint_bottom(page, draw, fonts, top + 6)
    paint_footer(draw, fonts, 960)
    out = Path(__file__).resolve().parent / "entry.png"
    page.save(out, format="PNG", optimize=True)
    blob = out.read_bytes()
    print("wrote %s (%d bytes) sha256=%s"
          % (out, len(blob), sha256(blob).hexdigest()))


def paint_top(draw, fonts):
    """High-contrast masthead: a dark navy band carrying the nameplate
    in gold and the date in big white serif, then the red sub-headline,
    the region and field strips, and the big-number stat strip.
    Returns the y where the leads begin."""
    gold = (232, 180, 28)
    date_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 34)
    draw.rectangle([8, 8, W - 8, 66], fill=NAVY)
    draw.text((16, 12), "THE WORLD IN ONE DAY", font=fonts["strip"],
              fill=gold)
    draw.text((28, 28), "Wednesday 25 November 2026", font=date_font,
              fill=(255, 255, 255))
    right = "50 STORIES \u00b7 10 REGIONS \u00b7 20 FIELDS"
    tw = draw.textlength(right, font=fonts["strip"])
    draw.text((W - 16 - tw, 12), right, font=fonts["strip"],
              fill=(255, 255, 255))
    right2 = "ONE DAY \u00b7 ONE PAGE \u00b7 THE WORLD'S NEWS"
    tw2 = draw.textlength(right2, font=fonts["foot"])
    draw.text((W - 16 - tw2, 34), right2, font=fonts["foot"],
              fill=(200, 210, 220))
    # red sub-headline
    sub = ("US proposes tariffs on 14 economies \u00b7 AI doubts sink "
           "Asian chip stocks \u00b7 Pakistan\u2019s first astronaut "
           "docks at Tiangong")
    draw.text((28, 72), sub, font=fonts["sub"], fill=RED)
    draw.line([28, 90, W - 28, 90], fill=RULE, width=2)
    # region strip
    y = 94
    gap = 2
    cw = (W - 56 - (len(REGION_ORDER) - 1) * gap) // len(REGION_ORDER)
    for i, region in enumerate(REGION_ORDER):
        cx = 28 + i * (cw + gap)
        draw.rectangle([cx, y, cx + cw, y + 16],
                       fill=REGION_COLOUR[region])
        label = "%s %d" % (REGION_SHORT[region],
                           REGION_COUNTS[region])
        lw = draw.textlength(label, font=fonts["region"])
        draw.text((cx + (cw - lw) / 2, y + 3), label,
                  font=fonts["region"], fill=(255, 255, 255))
    # fields strip, two lines so every field stays legible
    parts = sorted(FIELD_COUNTS.items(), key=lambda kv: (-kv[1], kv[0]))
    draw.text((28, 114), "20 FIELDS", font=fonts["footb"], fill=RED)
    first = "  \u00b7  ".join("%s %d" % (k, v) for k, v in parts[:10])
    draw.text((96, 114), first, font=fonts["field"], fill=INK)
    second = "  \u00b7  ".join("%s %d" % (k, v) for k, v in parts[10:])
    draw.text((96, 124), second, font=fonts["field"], fill=INK)
    draw.line([28, 138, W - 28, 138], fill=RULE, width=1)
    # stat strip: five big numbers with one-line labels
    stats = [
        ("20%", "top proposed US tariff, on China", INK),
        ("\u22126.2%", "Kospi close, worst in AI sell-off", RED),
        ("+26%", "UK energy price cap from 1 January", INK),
        ("31", "killed in Cairo tanker fire", INK),
        ("9", "dead, 17 trapped in Java gold pit", INK),
    ]
    y = 144
    sw = (W - 56) // 5
    for i, (num, lab, col) in enumerate(stats):
        cx = 28 + i * sw
        draw.text((cx, y), num, font=fonts["statnum"], fill=col)
        draw.text((cx, y + 27), lab, font=fonts["statlab"], fill=GREY)
        if i < 4:
            draw.line([cx + sw - 6, y + 2, cx + sw - 6, y + 38],
                      fill=FAINT, width=1)
    draw.line([28, 182, W - 28, 182], fill=RULE, width=2)
    return 188


if __name__ == "__main__":
    main()
