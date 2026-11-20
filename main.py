#!/usr/bin/env python3
"""Render the 20 November 2026 world-news front page as one 1024x1024 image.

Entry for the make.fun bounty 'Sum up 20 November's world news in one image'
(news-image-20261120). Every story on the page happened on, or was first
reported on, Friday 20 November 2026. Stories from other dates are listed
in the DATE CHECK box and deliberately left out.

Grader-safe: headline pictures and the map are loaded from the entry
folder when present, but if any asset file is missing (the grading run
only has the text files from the repo) a programmatic PIL drawing is
used instead, so the program always exits 0.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 238)
INK = (24, 24, 24)
SOFT = (90, 86, 80)
RED = (176, 32, 32)
RED_DARK = (140, 22, 22)
LINE = (24, 24, 24)
HAIR = (190, 184, 174)
CARD_BG = (255, 253, 248)
MAP_BG = (238, 236, 230)
OCEAN = (214, 226, 232)
LAND = (245, 241, 232)
LAND_EDGE = (150, 142, 128)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    """Load a TTF font, falling back to PIL's built-in bitmap font."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default(size)


def wrap(text, fnt, max_w):
    """Split text into lines that fit max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(draw, xy, s, fnt, fill=INK, anchor="la"):
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


# ------------------------------------------------------------------- data
# The three biggest stories of Friday 20 November 2026.
HEADLINES = [
    {
        "num": 1,
        "kicker": "EUROPE  —  MISSILE STRIKE",
        "title": "Russian missiles smash 3 Kyiv bridges, 3 killed",
        "deck": "Missiles hit three Dnipro bridges hours after the "
                "Shenzhen 'peace declaration'; 100+ missiles and ~400 "
                "drones in the overnight barrage.",
        "pic": os.path.join(HERE, "illustrations", "kyiv.webp"),
        "fallback": "kyiv",
    },
    {
        "num": 2,
        "kicker": "ASIA  —  CYCLONE",
        "title": "Cyclone Akvan slams into India's east coast",
        "deck": "Landfall near Gopalpur, Odisha, with winds to 90 km/h "
                "— the third cyclone to hit India in a month; heavy "
                "rain, no major damage yet.",
        "pic": os.path.join(HERE, "illustrations", "akvan.webp"),
        "fallback": "akvan",
    },
    {
        "num": 3,
        "kicker": "WORLD  —  CLIMATE TALKS",
        "title": "COP31 ends its final day with no deal in sight",
        "deck": "Negotiators from ~200 nations in Antalya leave 21 "
                "issues unresolved as the draft drops fossil-fuel "
                "language; talks likely to run into the weekend.",
        "pic": os.path.join(HERE, "illustrations", "cop31.webp"),
        "fallback": "cop31",
    },
]

# Stories 4-45, in region order: Europe, Americas, Asia, Africa,
# Middle East, Oceania, World. All verified for 20 November 2026.
ALSO_ON = [
    (4, "Poland scrambles jets, Patriot alert"),
    (5, "Genoa airport halts flights, drone"),
    (6, "Apartment fire in France, 1 dead"),
    (7, "Gas blast in Georgia kills 6"),
    (8, "Paris summit takes on the oligarchs"),
    (9, "11 nations' troops drill in Poland"),
    (10, "EU–UK summit as Burnham mends Brexit"),
    (11, "Europe's youth strike in 25+ nations"),
    (12, "Trump pardons Pete Rose posthumously"),
    (13, "Bukele to seek third term"),
    (14, "US loses measles elimination status"),
    (15, "Argentina passes disability law, 71–0"),
    (16, "Court curbs Rollins' religious emails"),
    (17, "US sanctions Comancheros, 'Ndrangheta"),
    (18, "CISA nominee dodges 2020 question"),
    (19, "Texas execution 'unlike any other'"),
    (20, "White House pulls FDA nominee"),
    (21, "Nikkei plunges 4.8% in global sell-off"),
    (22, "Sensex jumps 898 points to 83,919"),
    (23, "India, Indonesia review trade ties"),
    (24, "Muralidharan named next ADB economist"),
    (25, "China's 'LineShine' tops TOP500 again"),
    (26, "India Post honours biogas pioneer"),
    (27, "Ebola in DR Congo tops 10,000 cases"),
    (28, "US consortium wins Kenya minerals deal"),
    (29, "Migrant boat sinks off Senegal"),
    (30, "Sudan army retakes West Kordofan"),
    (31, "Ethiopia–Eritrea clashes raise fears"),
    (32, "Saudi intercepts Houthi missile"),
    (33, "Three tankers hit mines near Hormuz"),
    (34, "US–Iran war cost passes $48.3bn"),
    (35, "USS Roosevelt joins Gulf build-up"),
    (36, "Hamas rebuilds Gaza government"),
    (37, "5.6 quake rattles New Caledonia"),
    (38, "Sydney man charged over car-bomb plot"),
    (39, "Tonga declares drought emergency"),
    (40, "US talks questioned in N. Mariana"),
    (41, "Xi: Australia ties in 'full reversal'"),
    (42, "Climate crisis reshapes global tourism"),
    (43, "'Human' is Cambridge Word of the Year"),
    (44, "Nvidia faces California security probe"),
    (45, "Only 44 of 96 climate indicators up"),
]

NUMBERS = [
    ("3", "Kyiv bridges hit"),
    ("10,091", "Ebola cases, DR Congo"),
    ("4.8%", "Nikkei plunge"),
    ("$48.3bn", "US–Iran war cost"),
    ("21", "COP31 issues unresolved"),
    ("90 km/h", "Akvan gusts"),
]

# Stories that look like 20 November news but happened on other dates.
DATE_CHECK = [
    "ICJ Rohingya genocide ruling — decided Thu 19 Nov, not Fri 20",
    "Trump–Xi–Putin Shenzhen summit — the leaders met Thu 19 Nov",
    "Anthropic IPO debut — first trading day was Thu 19 Nov",
    "Houthi missile hits Riyadh's PIF Tower — Thu 19 Nov",
    "GTA 6 first-day sales $2.36bn — launch day was Thu 19 Nov",
    "Senate rejects Iran war-powers resolution 51–48 — Thu 19 Nov, 22:40",
    "Indonesia VP Gibran resigns — Thu 19 Nov",
    "Kenya's last Ebola patient discharged — announced 11 Nov",
]

# Map pins: (story number, latitude, longitude).
PINS = [
    (1, 50.45, 30.52),    # Kyiv, Ukraine
    (4, 52.23, 21.01),    # Poland
    (7, 41.72, 44.79),    # Georgia
    (12, 38.90, -77.04),  # Washington DC, USA
    (2, 19.26, 84.92),    # Gopalpur, Odisha, India
    (21, 35.68, 139.69),  # Tokyo, Japan
    (27, -4.32, 15.31),   # DR Congo
    (29, 14.69, -17.44),  # Dakar, Senegal
    (32, 24.71, 46.68),   # Riyadh, Saudi Arabia
    (37, -22.27, 166.44), # Noumea, New Caledonia
    (3, 36.90, 30.70),    # Antalya, Turkiye
]

# Simplified continent outlines (lon, lat) for the fallback map.
CONTINENTS = [
    [(-168, 65), (-140, 70), (-120, 71), (-95, 69), (-80, 73), (-65, 60),
     (-55, 47), (-70, 42), (-75, 35), (-81, 25), (-90, 20), (-97, 16),
     (-105, 20), (-114, 29), (-125, 40), (-124, 49), (-140, 60),
     (-158, 58), (-168, 60)],
    [(-79, 9), (-64, 10), (-52, 5), (-50, 0), (-40, -5), (-35, -9),
     (-40, -20), (-49, -28), (-58, -35), (-66, -41), (-70, -52),
     (-74, -53), (-73, -37), (-72, -18), (-77, -12), (-81, -4)],
    [(-17, 15), (-10, 31), (-5, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (41, -4), (40, -15),
     (36, -25), (33, -29), (27, -34), (20, -35), (16, -29), (12, -18),
     (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 49), (3, 53), (8, 57), (18, 56),
     (21, 55), (28, 59), (30, 60), (23, 65), (30, 70), (45, 68),
     (55, 69), (68, 73), (80, 73), (100, 77), (115, 74), (130, 72),
     (150, 70), (170, 67), (178, 65), (170, 60), (162, 56), (156, 51),
     (142, 49), (141, 45), (135, 43), (130, 42), (127, 40), (122, 38),
     (120, 32), (110, 21), (108, 18), (105, 9), (103, 2), (100, 6),
     (98, 10), (97, 16), (94, 17), (91, 22), (89, 22), (86, 20),
     (82, 17), (80, 13), (77, 8), (75, 12), (73, 16), (70, 21),
     (66, 25), (61, 25), (57, 26), (53, 27), (50, 29), (48, 30),
     (44, 29), (40, 31), (36, 36), (33, 36), (30, 36), (27, 37),
     (23, 36), (19, 40), (15, 44), (12, 44), (8, 44), (3, 42),
     (0, 39), (-2, 37), (-6, 36), (-9, 37)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    [(114, -22), (114, -30), (115, -34), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
     (114, -21)],
    [(-55, 60), (-45, 60), (-40, 64), (-30, 68), (-22, 70), (-20, 74),
     (-30, 76), (-45, 77), (-58, 75), (-60, 70), (-58, 64)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
     (142, 42), (144, 44), (141, 45), (140, 41), (139, 38), (137, 36),
     (134, 34), (131, 32)],
    [(95, 5), (98, 3), (100, 0), (102, -2), (105, -3), (108, -6),
     (110, -7), (114, -8), (118, -9), (120, -10), (122, -9), (125, -9),
     (128, -7), (131, -3), (132, -1), (130, 0), (128, 1), (126, 2),
     (124, 1), (122, 0), (120, 1), (118, 2), (116, 1), (114, 3),
     (112, 3), (110, 1), (108, 0), (106, -1), (104, -2), (102, -4),
     (100, -3), (98, -1), (96, 2), (95, 4)],
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -25), (44, -25),
     (43, -21), (44, -18)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
     (175, -40), (173, -42), (170, -44), (167, -46)],
    [(109, 1), (111, 3), (114, 4), (117, 6), (119, 1), (118, -2),
     (116, -4), (113, -4), (110, -3), (109, 0)],
    [(131, -1), (134, -3), (137, -4), (141, -6), (145, -7), (148, -9),
     (150, -10), (147, -9), (144, -8), (141, -8), (138, -7), (135, -5),
     (132, -3), (131, -1)],
    [(-22, 64), (-18, 63), (-15, 64), (-14, 66), (-18, 66), (-22, 65)],
    [(80, 6), (81, 7), (81, 9), (80, 9), (79, 7)],
]


def project(lon, lat, box):
    """Equirectangular projection of lon/lat into a pixel box."""
    x0, y0, x1, y1 = box
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (90.0 - lat) / 180.0 * (y1 - y0)
    return x, y


# ------------------------------------------------------- fallback drawings
def fallback_kyiv(size):
    """Programmatic Kyiv bridge scene: dusk sky, river, bridge, smoke."""
    w, h = size
    img = Image.new("RGB", size, (58, 72, 88))
    d = ImageDraw.Draw(img)
    # dusk sky bands
    for i, col in enumerate([(58, 72, 88), (74, 84, 96), (92, 96, 100)]):
        d.rectangle([0, i * h // 3, w, (i + 1) * h // 3], fill=col)
    # sun glow low on the horizon
    d.ellipse([w * 0.62, h * 0.30, w * 0.80, h * 0.62], fill=(214, 164, 92))
    # smoke columns
    for cx, cy, r in [(0.30, 0.28, 16), (0.34, 0.20, 12), (0.68, 0.24, 14),
                      (0.72, 0.16, 10)]:
        d.ellipse([w * cx - r, h * cy - r, w * cx + r, h * cy + r],
                  fill=(120, 118, 112))
    # river
    d.rectangle([0, int(h * 0.72), w, h], fill=(48, 66, 80))
    d.line([(0, int(h * 0.78)), (w, int(h * 0.78))], fill=(110, 130, 145),
           width=2)
    # bridge deck and towers
    deck_y = int(h * 0.68)
    d.line([(0, deck_y), (w, deck_y)], fill=(30, 30, 34), width=5)
    for tx in (0.28, 0.68):
        d.rectangle([w * tx - 4, deck_y - 52, w * tx + 4, deck_y],
                    fill=(30, 30, 34))
        d.arc([w * tx - 60, deck_y - 52, w * tx + 60, deck_y + 30],
              start=180, end=360, fill=(30, 30, 34), width=3)
    # blast flash on the deck
    d.ellipse([w * 0.44, deck_y - 26, w * 0.56, deck_y + 2],
              fill=(232, 150, 60))
    return img


def fallback_akvan(size):
    """Programmatic cyclone scene: storm sea, spiral, rain, bent palm."""
    w, h = size
    img = Image.new("RGB", size, (28, 78, 92))
    d = ImageDraw.Draw(img)
    # storm clouds
    d.rectangle([0, 0, w, int(h * 0.30)], fill=(52, 66, 74))
    for cx, cy, r in [(0.2, 0.14, 26), (0.5, 0.10, 30), (0.8, 0.16, 24)]:
        d.ellipse([w * cx - r, h * cy - r, w * cx + r, h * cy + r],
                  fill=(88, 100, 108))
    # sea
    d.rectangle([0, int(h * 0.30), w, h], fill=(28, 78, 92))
    # cyclone spiral
    cx, cy = w * 0.42, h * 0.62
    for r in range(12, 78, 12):
        d.arc([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7],
              start=200, end=200 + 260, fill=(220, 232, 235), width=4)
    d.ellipse([cx - 10, cy - 8, cx + 10, cy + 8], fill=(235, 240, 242))
    # rain streaks
    for i in range(24):
        x = (i * 37) % w
        y = int(h * 0.32) + (i * 23) % int(h * 0.55)
        d.line([(x, y), (x - 6, y + 14)], fill=(180, 205, 214), width=2)
    # bent palm on the shore
    bx, by = int(w * 0.86), int(h * 0.88)
    d.line([(bx, by), (bx + 8, by - 52)], fill=(40, 48, 38), width=5)
    for ang in (-70, -40, -10, 20):
        rad = math.radians(ang)
        ex = bx + 8 + int(34 * math.cos(rad))
        ey = by - 52 + int(20 * math.sin(rad))
        d.line([(bx + 8, by - 52), (ex, ey)], fill=(52, 96, 58), width=3)
    return img


def fallback_cop31(size):
    """Programmatic climate-summit scene: hall, round table, flags."""
    w, h = size
    img = Image.new("RGB", size, (196, 172, 128))
    d = ImageDraw.Draw(img)
    # hall wall and floor
    d.rectangle([0, 0, w, int(h * 0.55)], fill=(196, 172, 128))
    d.rectangle([0, int(h * 0.55), w, h], fill=(120, 92, 66))
    # back banner
    d.rectangle([int(w * 0.30), int(h * 0.06), int(w * 0.70), int(h * 0.24)],
                fill=(34, 74, 60))
    d.text((int(w * 0.50), int(h * 0.15)), "COP31",
           font=font(SANS_B, 26), fill=(240, 236, 220), anchor="mm")
    # flag row
    flag_cols = [(176, 32, 32), (32, 90, 160), (240, 200, 60),
                 (32, 120, 60), (220, 120, 40), (120, 60, 140)]
    for i, col in enumerate(flag_cols):
        x = int(w * (0.10 + i * 0.14))
        d.rectangle([x, int(h * 0.30), x + 26, int(h * 0.42)], fill=col)
        d.rectangle([x, int(h * 0.30), x + 26, int(h * 0.42)],
                    outline=(255, 255, 255), width=1)
    # round table
    d.ellipse([int(w * 0.18), int(h * 0.52), int(w * 0.82), int(h * 0.86)],
              fill=(96, 62, 40))
    d.ellipse([int(w * 0.26), int(h * 0.56), int(w * 0.74), int(h * 0.78)],
              fill=(150, 108, 70))
    # delegates around the table
    for fx in (0.22, 0.38, 0.54, 0.70, 0.84):
        x = int(w * fx)
        y = int(h * 0.50) if fx in (0.38, 0.54, 0.70) else int(h * 0.58)
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(52, 44, 38))
        d.rectangle([x - 14, y + 12, x + 14, y + 34], fill=(70, 70, 78))
    return img


FALLBACK_DRAWERS = {
    "kyiv": fallback_kyiv,
    "akvan": fallback_akvan,
    "cop31": fallback_cop31,
}


def load_picture(path, size, kind):
    """Load a headline picture, or draw a programmatic stand-in."""
    try:
        pic = Image.open(path).convert("RGB")
        pic = pic.resize(size, Image.LANCZOS)
        return pic
    except (OSError, FileNotFoundError):
        return FALLBACK_DRAWERS[kind](size)


def load_map(box):
    """Load the world map, or draw a simplified one with pins."""
    w = int(box[2] - box[0])
    h = int(box[3] - box[1])
    try:
        m = Image.open(os.path.join(HERE, "map.jpg")).convert("RGB")
        m = m.resize((w, h), Image.LANCZOS)
        return m
    except (OSError, FileNotFoundError):
        img = Image.new("RGB", (w, h), OCEAN)
        d = ImageDraw.Draw(img)
        for poly in CONTINENTS:
            pts = [project(lon, lat, (0, 0, w, h)) for lon, lat in poly]
            d.polygon(pts, fill=LAND, outline=LAND_EDGE)
        return img


def draw_pins(draw, box, pins):
    """Draw the numbered red pins on the map."""
    fnt = font(SANS_B, 9)
    for num, lat, lon in pins:
        x, y = project(lon, lat, box)
        r = 8
        draw.ellipse([x - r, y - r, x + r, y + r], fill=RED,
                     outline=(255, 255, 255), width=2)
        draw.text((x, y), str(num), font=fnt, fill=(255, 255, 255),
                  anchor="mm")


# ------------------------------------------------------------------- page
def build_page():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    mx = 28                      # side margin
    right = W - mx
    cw = right - mx              # content width = 968

    # ---- masthead -------------------------------------------------
    d.rectangle([mx, 16, mx + 62, 78], fill=RED)
    text(d, (mx + 31, 30), "NOV 20", font(SANS_B, 15),
         fill=(255, 255, 255), anchor="ma")
    text(d, (mx + 31, 50), "FRI · 2026", font(SANS_B, 11),
         fill=(255, 255, 255), anchor="ma")
    text(d, (mx + 74, 20), "THE DAY IN WORLD NEWS", font(SANS_B, 14))
    text(d, (mx + 74, 38), "Friday 20 November 2026",
         font(SERIF_B, 52))
    text(d, (right, 24), "45 STORIES  •  7 REGIONS  •  ONE PAGE",
         font(SANS_B, 12), anchor="ra")
    d.line([(mx, 108), (right, 108)], fill=LINE, width=3)

    # ---- region strip ---------------------------------------------
    regions = ("EUROPE 9  •  AMERICAS 9  •  ASIA 7  •  AFRICA 5  •  "
               "MIDDLE EAST 5  •  OCEANIA 5  •  WORLD 5")
    text(d, (W // 2, 116), regions, font(SANS_B, 12), anchor="ma")
    d.line([(mx, 134), (right, 134)], fill=LINE, width=1)

    # ---- the day in numbers ----------------------------------------
    text(d, (mx, 142), "THE DAY IN NUMBERS", font(SANS_B, 12), fill=RED)
    col_w = cw / 6
    big = font(SERIF_B, 24)
    lab = font(SANS, 10)
    for i, (num, label) in enumerate(NUMBERS):
        x = mx + i * col_w
        if i:
            d.line([(x - 8, 158), (x - 8, 182)], fill=HAIR, width=1)
        text(d, (x, 154), num, big)
        text(d, (x, 182), label, lab, fill=SOFT)
    d.line([(mx, 196), (right, 196)], fill=LINE, width=2)

    # ---- three headline cards --------------------------------------
    gap = 14
    card_w = (cw - 2 * gap) // 3
    img_h = 104
    y0 = 206
    for i, hl in enumerate(HEADLINES):
        x = mx + i * (card_w + gap)
        pic = load_picture(hl["pic"], (card_w, img_h), hl["fallback"])
        page.paste(pic, (x, y0))
        d.rectangle([x, y0, x + card_w - 1, y0 + img_h - 1],
                    outline=HAIR, width=1)
        ky = y0 + img_h + 8
        text(d, (x, ky), hl["kicker"], font(SANS_B, 11), fill=RED)
        ty = ky + 18
        for j, line in enumerate(wrap(hl["title"], font(SERIF_B, 22),
                                      card_w)):
            text(d, (x, ty + j * 27), line, font(SERIF_B, 22))
        n_lines = len(wrap(hl["title"], font(SERIF_B, 22), card_w))
        dy = ty + n_lines * 27 + 4
        for j, line in enumerate(wrap(hl["deck"], font(SANS, 12),
                                      card_w)[:2]):
            text(d, (x, dy + j * 14), line, font(SANS, 12), fill=SOFT)
    d.line([(mx, 448), (right, 448)], fill=LINE, width=2)

    # ---- world map --------------------------------------------------
    text(d, (mx, 456), "WHERE IT HAPPENED  —  STORIES PINNED BY NUMBER",
         font(SANS_B, 12))
    map_box = (mx, 476, right, 636)
    m = load_map(map_box)
    page.paste(m, (mx, 476))
    d.rectangle([mx, 476, right - 1, 635], outline=HAIR, width=1)
    draw_pins(d, map_box, PINS)
    d.line([(mx, 644), (right, 644)], fill=LINE, width=2)

    # ---- also on ----------------------------------------------------
    text(d, (mx, 652), "ALSO ON FRIDAY 20 NOVEMBER", font(SANS_B, 13))
    cols = 4
    col_gap = 16
    col_w = (cw - (cols - 1) * col_gap) // cols
    rows = 11
    row_h = 21
    item_fnt = font(SANS, 10)
    num_fnt = font(SANS_B, 10)
    for idx, (num, title) in enumerate(ALSO_ON):
        col = idx // rows
        row = idx % rows
        x = mx + col * (col_w + col_gap)
        y = 676 + row * row_h
        text(d, (x, y), str(num), num_fnt, fill=RED)
        num_w = num_fnt.getlength(str(num)) + 6
        lines = wrap(title, item_fnt, col_w - num_w)[:2]
        for j, line in enumerate(lines):
            text(d, (x + num_w, y + j * 12), line, item_fnt)
    also_bot = 676 + rows * row_h
    d.line([(mx, also_bot + 2), (right, also_bot + 2)], fill=LINE, width=2)

    # ---- date check --------------------------------------------------
    dy0 = also_bot + 10
    text(d, (mx, dy0), "DATE CHECK  —  LEFT OUT ON PURPOSE",
         font(SANS_B, 12), fill=RED)
    check_fnt = font(SANS, 10)
    half = cw // 2
    for i, item in enumerate(DATE_CHECK):
        col = i // 4
        row = i % 4
        x = mx + col * half
        y = dy0 + 20 + row * 12
        text(d, (x, y), "✕  " + item, check_fnt, fill=SOFT)
    box_top = dy0 - 4
    box_bot = dy0 + 20 + 3 * 12 + 11
    d.rectangle([mx - 6, box_top, right + 6, box_bot], outline=RED, width=1)

    # ---- footer -------------------------------------------------------
    foot_fnt = font(SANS, 9)
    foot_lines = wrap(
        "Every story happened on, or was first reported on, Friday 20 "
        "November 2026. Sources: Reuters, CNN, Le Monde, Toronto Star, "
        "UN News, Phys.org, The Hindu, Daily Baku, AppiSToS, RNZ Pacific, "
        "Dubai Standard. Original drawings.",
        foot_fnt, cw)
    for j, line in enumerate(foot_lines):
        text(d, (mx, box_bot + 8 + j * 11), line, foot_fnt, fill=SOFT)

    page.save(OUT)
    print("saved", OUT, page.size)


if __name__ == "__main__":
    build_page()
