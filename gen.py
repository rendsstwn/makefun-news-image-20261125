#!/usr/bin/env python3
"""Draw the 25 November 2026 one-page news front for make.fun.

Build-time tool only: it renders entry.png (1024x1024) in this folder
from the thirty verified stories below, using Pillow and the DejaVu
fonts on this machine. The shipped program, main.py, is a separate
small file that only copies the finished picture to /output. Nothing
here touches the network, the clock, or any random source, so the
picture it writes is the same on every run.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (18, 18, 18)
RULE = (18, 18, 18)
RED = (139, 26, 26)
BLUE = (26, 58, 92)
GREEN = (31, 92, 50)
PURPLE = (88, 44, 110)
SEA = (28, 68, 104)
SKY = (214, 228, 238)
# Depth palette for the lead scene: dusk sky, deep water, fire glow.
SKY_TOP = (176, 198, 220)
SKY_HORIZON = (238, 196, 148)
SEA_TOP = (38, 82, 116)
SEA_DEEP = (10, 32, 54)
FIRE = (232, 120, 28)
EMBER = (245, 196, 66)
SMOKE = (96, 96, 98)
SCENE_H = 110

LEAD = (
    "MIDDLE EAST",
    "TANKERS ABLAZE IN THE STRAIT OF HORMUZ",
    "Two oil tankers strike naval mines and catch fire off Iran early "
    "on Wednesday; Tehran says the ships took an unauthorised route "
    "through the strait, and oil markets brace for worse.",
)

# (kicker, headline, one-line deck) -- every item happened, or was
# first reported, on Wednesday 25 November 2026.
STORIES = [
    ("GULF",
     "Houthis claim strike on Saudi oil refinery",
     "Ras Tanura attacked, fires reported."),
    ("UKRAINE",
     "Ukraine drones set two Russian refineries ablaze",
     "Syzran, Kuibyshev hit; 1 killed."),
    ("KYIV",
     "Kyiv seeks 115bn euros aid for 2027",
     "US pauses Patriot missile supplies."),
    ("ODESA",
     "Russian strike kills two in Odesa",
     "Child among injured in apartment hit."),
    ("LIBYA",
     "Libya: two officers die in drone attack",
     "Kyiv claims warship sunk in Benghazi."),
    ("GAZA",
     "Israel kills Hamas security chief in Gaza",
     "Abuelouf dies with wife, two children."),
    ("SUDAN",
     "Sudan strikes kill 19 civilians",
     "Drones hit two cities; 20 wounded."),
    ("PACIFIC",
     "Australia signs Pacific security treaty",
     "Deal bars any foreign military base."),
    ("COLOMBIA",
     "Colombia frees supermarket hostages",
     "All captives freed; one captor killed."),
    ("INDONESIA",
     "Six dead in flooded Indonesia gold mine",
     "20 miners still trapped in Bogor."),
    ("ZIMBABWE",
     "Zimbabwe seeks Mugabe's son",
     "Warrant after a missed court date."),
    ("BANGLADESH",
     "Bangladesh garment workers win 36% rise",
     "Pay deal ends weeks of protests."),
    ("U.S.",
     "Abrego Garcia leaves US for Spain",
     "Departs voluntarily for Spain."),
    ("CLIMATE",
     "COP31 talks end with no deal",
     "Pope Leo warns of fiercer extremes."),
    ("MARKETS",
     "Asia's chip stocks plunge",
     "KOSPI falls 6.2%, Nikkei 2.8%."),
    ("MARKETS",
     "Dow tops 50,000 for first time",
     "Closes at 50,019; Nasdaq down 1.5%."),
    ("MARKETS",
     "Nvidia falls 5.9% after 31% surge",
     "Gives back a day after 31% surge."),
    ("MARKETS",
     "Dell posts record 54.9bn dollar quarter",
     "AI server sales jump 291% to $22bn."),
    ("MARKETS",
     "Eurozone inflation up to 4.0%",
     "Prices rise across the bloc."),
    ("MARKETS",
     "Australian inflation hits 4.9%",
     "Fuel drives prices; bank set to hold."),
    ("MARKETS",
     "EasyJet profit falls 89%",
     "Fuel bill jumps £244m; jets retired."),
    ("TECH",
     "Shenzhou-24 docks with Tiangong",
     "Carries Pakistan's first astronaut."),
    ("TECH",
     "Amazon buys chip rival Decart",
     "Bet to close the gap with Nvidia."),
    ("TECH",
     "Hackers' AI agents breach server",
     "Agents found a new flaw unaided."),
    ("TECH",
     "Anthropic shares fall below IPO price",
     "Stock drops under its listing price."),
    ("TECH",
     "CIA system 'breached by hackers'",
     "Intelligence platform reportedly hit."),
    ("TECH",
     "Roche cancer pill wins FDA nod",
     "Cancer drug wins 2nd FDA approval."),
    ("SPORT",
     "Senegal regain Africa Cup title",
     "Top court restores the trophy."),
    ("CULTURE",
     "GTA VI debuts at 3.79bn dollars",
     "Launch dwarfs every record ever."),
]

KICKER_COLOUR = {
    "WORLD": RED,
    "MARKETS": GREEN,
    "TECH": BLUE,
    "SPORT": PURPLE,
    "CULTURE": PURPLE,
    "MIDDLE EAST": RED,
    "CLIMATE": GREEN,
}


def load_fonts():
    """Pick the DejaVu faces this machine ships, at the sizes we use."""
    base = "/usr/share/fonts/truetype/dejavu/"
    serif_b = base + "DejaVuSerif-Bold.ttf"
    sans = base + "DejaVuSans.ttf"
    sans_b = base + "DejaVuSans-Bold.ttf"
    serif = base + "DejaVuSerif.ttf"
    return {
        "mast": ImageFont.truetype(serif_b, 54),
        "date": ImageFont.truetype(sans_b, 21),
        "lead": ImageFont.truetype(serif_b, 48),
        "deck": ImageFont.truetype(serif, 18),
        "kick": ImageFont.truetype(sans_b, 12),
        "head": ImageFont.truetype(serif_b, 16),
        "body": ImageFont.truetype(sans, 12),
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


def paint_hormuz(page, box):
    """The Strait at dusk: two tankers burning, a mine in the water.

    Depth comes from layered light, not more shapes: a dusk gradient
    sky, a glowing sun, blurred smoke and fire glow, hull shadows
    and firelight reflected in the water, and a mine with ripples.
    Every number is fixed, so the scene is byte-identical on
    every run.
    """
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    horizon = int(bh * 0.52)
    scene = Image.new("RGB", (bw, bh))
    sd = ImageDraw.Draw(scene)
    # sky: pale blue cooling into a warm band at the horizon
    for yy in range(horizon):
        t = yy / max(horizon - 1, 1)
        sd.line([(0, yy), (bw, yy)], fill=tuple(
            int(SKY_TOP[i] + (SKY_HORIZON[i] - SKY_TOP[i]) * t)
            for i in range(3)))
    # sea: lighter at the horizon, deepening toward the viewer
    for yy in range(horizon, bh):
        t = (yy - horizon) / max(bh - horizon - 1, 1)
        sd.line([(0, yy), (bw, yy)], fill=tuple(
            int(SEA_TOP[i] + (SEA_DEEP[i] - SEA_TOP[i]) * t)
            for i in range(3)))
    # glow layer: sun, firelight and smoke all land here, blurred
    glow = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    soft_spot(glow, bw - 58, 26, 42, 42, (240, 214, 140), 110, 14)
    # low sun, disc drawn sharp over its own glow
    sd.ellipse([bw - 76, 8, bw - 40, 44], fill=(240, 214, 140))
    # far tanker, hull and containers, with a lit top edge
    sd.rectangle([52, horizon - 12, 252, horizon + 4], fill=(32, 32, 34))
    for cx in range(66, 240, 34):
        sd.rectangle([cx, horizon - 22, cx + 28, horizon - 12],
                     fill=(150, 60, 44))
        sd.line([(cx, horizon - 22), (cx + 28, horizon - 22)],
                fill=(196, 110, 92), width=1)
    # near tanker, bigger, bow to the right, bridge tower aft
    sd.polygon([(330, horizon), (640, horizon),
                (664, horizon + 12), (330, horizon + 12)],
               fill=(24, 24, 26))
    for cx in range(350, 620, 40):
        sd.rectangle([cx, horizon - 10, cx + 32, horizon],
                     fill=(178, 74, 52))
        sd.line([(cx, horizon - 10), (cx + 32, horizon - 10)],
                fill=(220, 130, 104), width=1)
    sd.rectangle([620, horizon - 30, 642, horizon], fill=(200, 200, 200))
    sd.line([(620, horizon - 26), (642, horizon - 26)],
            fill=(40, 40, 40), width=2)
    # hull shadows smeared on the water under each ship
    for hx0, hx1 in [(52, 252), (330, 664)]:
        soft_spot(glow, (hx0 + hx1) // 2, horizon + 9,
                  (hx1 - hx0) // 2, 6, (8, 16, 28), 120, 3)
    # flames: layered tongues over a warm glow, four deck fires
    for fx, fy, s in [(130, horizon - 22, 13),
                      (210, horizon - 22, 11),
                      (470, horizon - 10, 15),
                      (570, horizon - 10, 13)]:
        soft_spot(glow, fx, fy - 6, s + 12, s + 8, FIRE, 120, 8)
        sd.polygon([(fx - s, fy), (fx, fy - s * 2),
                    (fx + s // 2, fy - s // 2), (fx + s, fy)],
                   fill=FIRE)
        sd.polygon([(fx - s // 2, fy), (fx, fy - s),
                    (fx + s // 4, fy - s // 3), (fx + s // 2, fy)],
                   fill=EMBER)
        sd.polygon([(fx - s // 4, fy), (fx, fy - s // 2),
                    (fx + s // 6, fy - s // 4), (fx + s // 4, fy)],
                   fill=(252, 240, 190))
        # firelight shimmering on the water below each fire
        for k in range(3):
            yy = horizon + 6 + k * 6
            sd.line([(fx - 8 + k * 3, yy), (fx + 10 - k * 2, yy)],
                    fill=(216, 110, 40), width=1)
    # smoke columns: soft grey puffs, blurred so edges melt
    for sx, sy, r in [(130, horizon - 34, 11),
                      (150, horizon - 46, 9),
                      (470, horizon - 30, 12),
                      (494, horizon - 42, 10),
                      (516, horizon - 52, 8)]:
        soft_spot(glow, sx, sy, r, r, SMOKE, 175, 6)
    scene.paste(Image.alpha_composite(
        scene.convert("RGBA"), glow).convert("RGB"), (0, 0))
    sd = ImageDraw.Draw(scene)
    # water shimmer: short pale streaks catching the dusk light
    for yy in range(horizon + 16, bh - 24, 9):
        for sx in range(24, bw - 40, 52):
            sd.line([(sx, yy), (sx + 26, yy)], fill=(96, 132, 158),
                    width=1)
    # a naval mine in the foreground water, with ripple rings
    mx, my = 740, bh - 34
    for rr in (26, 18):
        sd.ellipse([mx - rr, my - rr // 2, mx + rr, my + rr // 2],
                   outline=(110, 150, 175), width=1)
    sd.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=(20, 20, 20))
    sd.ellipse([mx - 4, my - 6, mx + 2, my - 1], fill=(70, 70, 70))
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        sd.line([mx + dx * 9, my + dy * 9,
                 mx + dx * 16, my + dy * 16], fill=(20, 20, 20), width=2)
    # caption strip under the scene
    sd.rectangle([0, bh - 20, bw, bh], fill=(18, 18, 18))
    page.paste(scene, (x0, y0))


def paint_masthead(draw, fonts):
    """Nameplate, date line and rules across the top of the page."""
    draw.text((28, 18), "THE WORLD TODAY", font=fonts["mast"], fill=INK)
    draw.text((28, 92), "WEDNESDAY 25 NOVEMBER 2026",
              font=fonts["date"], fill=RED)
    right = "ONE DAY  •  ONE PAGE  •  THE WORLD'S NEWS"
    tw = draw.textlength(right, font=fonts["date"])
    draw.text((W - 28 - tw, 92), right, font=fonts["date"], fill=INK)
    draw.line([28, 124, W - 28, 124], fill=RULE, width=3)
    draw.line([28, 130, W - 28, 130], fill=RULE, width=1)


def paint_lead(page, draw, fonts):
    """Lead headline, the Hormuz scene, and its two-line deck."""
    kick, head, deck = LEAD
    draw.text((28, 138), kick, font=fonts["kick"], fill=RED)
    lines = wrap_lines(draw, head, fonts["lead"], W - 56)
    y = 156
    for line in lines:
        draw.text((28, y), line, font=fonts["lead"], fill=INK)
        y += 55
    scene_top = y + 4
    paint_hormuz(page, (28, scene_top, W - 28, scene_top + SCENE_H))
    cap = "TWO TANKERS BURN IN THE STRAIT OF HORMUZ AFTER STRIKING MINES"
    draw.text((36, scene_top + SCENE_H - 16), cap, font=fonts["kick"],
              fill=(248, 244, 233))
    y = scene_top + SCENE_H + 10
    for line in wrap_lines(draw, deck, fonts["deck"], W - 56):
        draw.text((28, y), line, font=fonts["deck"], fill=INK)
        y += 23
    draw.line([28, y + 6, W - 28, y + 6], fill=RULE, width=2)
    return y + 14


# Runner imports live here, beside the runner, so the drawing helpers
# above stay free of anything but Pillow.
from hashlib import sha256
from pathlib import Path


def shorten(draw, text, font, width):
    """Cut text to fit width, at a word boundary, with an ellipsis."""
    if draw.textlength(text, font=font) <= width:
        return text
    words = text.split()
    out = ""
    for word in words:
        trial = word if not out else out + " " + word
        if draw.textlength(trial + " ...", font=font) <= width:
            out = trial
        else:
            break
    return out + " ..." if out else text[:1] + " ..."


def paint_grid(draw, fonts, top):
    """Four columns of briefs: kicker, headline, one deck line."""
    cols = 4
    gap = 14
    margin = 28
    col_w = (W - 2 * margin - (cols - 1) * gap) // cols
    rows = (len(STORIES) + cols - 1) // cols
    bottom = 994
    row_h = (bottom - top) // rows
    for idx, (kick, head, deck) in enumerate(STORIES):
        r, c = divmod(idx, cols)
        x = margin + c * (col_w + gap)
        y = top + r * row_h
        draw.text((x, y), kick, font=fonts["kick"],
                  fill=KICKER_COLOUR.get(kick, RED))
        lines = wrap_lines(draw, head, fonts["head"], col_w)[:2]
        hy = y + 15
        for line in lines:
            draw.text((x, hy), line, font=fonts["head"], fill=INK)
            hy += 19
        short = shorten(draw, deck, fonts["body"], col_w)
        draw.text((x, hy + 1), short, font=fonts["body"], fill=(60, 60, 60))
        if c < cols - 1:
            draw.line([x + col_w + gap // 2, y + 2,
                       x + col_w + gap // 2, y + row_h - 6],
                      fill=(200, 194, 178), width=1)
    return top + rows * row_h


def main():
    """Render the page and save it beside this script as entry.png."""
    fonts = load_fonts()
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    draw.rectangle([8, 8, W - 9, H - 9], outline=RULE, width=2)
    paint_masthead(draw, fonts)
    top = paint_lead(page, draw, fonts)
    paint_grid(draw, fonts, top)
    foot = "THE WORLD TODAY  —  WEDNESDAY 25 NOVEMBER 2026  —  30 STORIES"
    fw = draw.textlength(foot, font=fonts["body"])
    draw.text(((W - fw) / 2, 999), foot, font=fonts["body"], fill=INK)
    out = Path(__file__).resolve().parent / "entry.png"
    page.save(out, format="PNG", optimize=True)
    blob = out.read_bytes()
    print("wrote %s (%d bytes) sha256=%s"
          % (out, len(blob), sha256(blob).hexdigest()))


if __name__ == "__main__":
    main()
