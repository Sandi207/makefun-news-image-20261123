#!/usr/bin/env python3
"""Draw a fixed, offline newspaper front page at 2x resolution with Pillow."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCALE = 2
PAPER = "#f5f1e8"
INK = "#20262b"
RED = "#843c3c"
BLUE = "#637d89"
PALE_BLUE = "#dce4e5"
LAND = "#b8c5c8"
RULE = "#b4b7b2"
PANEL = "#ebece5"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONTS = {
    "serif": "DejaVuSerif.ttf",
    "headline": "DejaVuSerif-Bold.ttf",
    "sans": "DejaVuSans.ttf",
    "bold": "DejaVuSans-Bold.ttf",
}
# Explicit palette: paper/ink shades, dark-red shades, muted blue/grey shades.
# A fixed palette preserves small red labels as well as large coloured shapes.
PALETTE = (
    245, 241, 232,
    32, 38, 43,
    59, 64, 67,
    85, 89, 91,
    112, 115, 115,
    139, 140, 139,
    165, 165, 162,
    192, 190, 185,
    218, 216, 208,
    132, 60, 60,
    151, 86, 82,
    170, 111, 103,
    189, 137, 128,
    208, 163, 152,
    226, 195, 181,
    71, 86, 95,
    99, 125, 137,
    124, 147, 155,
    148, 169, 174,
    172, 190, 193,
    184, 197, 200,
    220, 228, 229,
    235, 236, 229,
    180, 183, 178,
)

# Ordered down each column, then across to the next column.
# Each record is one brief: region, one headline, one detail line.
BRIEFS = (
    ("MIDDLE EAST", "Hormuz: two tankers burn", "Sunday mines; worst shipping attacks since Feb."),
    ("MIDDLE EAST", "Bahrain seeks UN action", "Iran strikes: compensation sought under Res. 2817."),
    ("MIDDLE EAST", "Lebanon seizes 264 kg explosives", "From Syria: 203 kg C4, 61 kg TNT; three arrested."),
    ("MIDDLE EAST", "Gaza food-vehicle strike kills 3", "Israeli strike Saturday; WCK says vehicle not its own."),
    ("MIDDLE EAST", "West Bank: 12 vehicles torched", "Settlers leave graffiti in four villages near Ramallah."),
    ("MIDDLE EAST", "Israeli checkpoint in Quneitra", "Set up Saturday; Turkey warns of a Syria operation."),
    ("MIDDLE EAST", "Coalition intercepts Houthi missile", "Saudi-led coalition; western region on Sunday."),
    ("EUROPE", "Poland confirms Russian missiles", "Three fell Friday; NATO is to meet."),
    ("EUROPE", "Sparta II still burns off Finland", "Saturday drone strike; crew evacuated."),
    ("EUROPE", "Gen Z protests in 25 countries", "Italy: 1m+; France: 82,500; Lisbon marches in rain."),
    ("EUROPE", "Brussels plans general strike", "Action scheduled for Monday, 23 November."),
    ("EUROPE", "Thousands protest in Istanbul", "Sunday rallies against opposition and media crackdown."),
    ("EUROPE", "France beats Argentina 45–17", "Nations final: South Africa on 29 November."),
    ("AMERICAS", "Trump: no rush to strike Iran", "US hawks urge action; president holds back."),
    ("AMERICAS", "Trump calls Schumer ties difficult", "On cooperation with Schumer as Senate majority leader."),
    ("AMERICAS", "Seattle ICE pair bound for baptism", "Detained father and daughter, their lawyer says."),
    ("AMERICAS", "Mexico confirms Chapo-capture toll", "Four soldiers and seven gunmen dead."),
    ("AMERICAS", "Boca wins Sudamericana 2–0", "Over Atlético Mineiro; Paredes collapses in TV interview."),
    ("AMERICAS", "Liverpool routs Man United 4–0", "Pochettino debut; Yoro sent off in eighth minute."),
    ("ASIA & PACIFIC", "Asian markets slide on Monday", "Kospi −3.7%, Taiex −0.9%; Taiwan bans short-selling."),
    ("ASIA & PACIFIC", "Nepal's Balen Shah arrives in Delhi", "Prime minister makes his first official visit."),
    ("ASIA & PACIFIC", "Cikande fire: 24 body bags", "Recovered Sunday from Indonesian candy factory."),
    ("ASIA & PACIFIC", "Lahore's air quality index hits 538", "Sunday: world's most polluted major city."),
    ("ASIA & PACIFIC", "Myanmar rejects ASEAN decision", "Army-backed government: ‘unfair and imbalanced’."),
    ("ASIA & PACIFIC", "Korean education minister quits", "South Korea: AI exam-cheating scandal."),
    ("ASIA & PACIFIC", "China's US metals-ban pause ends", "Gallium, germanium, antimony: 27 Nov; no extension."),
    ("AFRICA", "Libya: Russian corvette capsizes", "Suspected Ukrainian sea drones; Merkury, Benghazi; 10 hurt."),
    ("AFRICA", "Sudan drones damage UN facility", "Khartoum Sunday; at least three killed in Omdurman."),
    ("AFRICA", "South Sudan: 24 civilians killed", "Fresh violence claims two dozen civilian lives."),
    ("AFRICA", "Kano revenge attacks kill 35", "Nigeria: 35 Fulanis killed."),
    ("AFRICA", "Tinubu donates N250m in Bayelsa", "Monday donation to boat victims' families."),
    ("AFRICA", "ANC's worst local election result", "Most votes in only two of eight major South African cities."),
    ("AFRICA", "Ethiopia launches polio campaign", "Vaccinations for more than 11 million children."),
    ("AFRICA", "Kenya discharges last Ebola patient", "A 42-day countdown begins."),
    ("SPORT", "Verstappen wins Las Vegas GP", "Beats Norris by six-tenths of a second."),
    ("SPORT", "India declares record 720 for 9", "Highest total in NZ; first Test, day 5; NZ 157/4 at lunch."),
    ("SPORT", "Sindarov gets White in Game 1", "FIDE World Championship opening game."),
    ("SPORT", "FIA agrees V8 framework for 2030", "Formula 1 engine decision is unanimous."),
    ("SCIENCE & WORLD", "BepiColombo orbits Mercury", "Only the second mission ever to enter Mercury orbit."),
    ("SCIENCE & WORLD", "Kim: security, not supremacy", "North Korean leader states country's aim."),
)

TIMELINE = (
    ("00:18", "Asia opens; Kospi falls 3%"),
    ("01:04", "Tinubu: N250m for Bayelsa families"),
    ("01:22", "Kyiv region death toll rises to 11"),
    ("02:00", "Australia PM: difficult geopolitical times"),
    ("05:05", "Houthis claim Saudi strikes; at least 6 hurt"),
    ("05:37", "ICE lawyer: pair were bound for baptism"),
    ("06:32", "Suspected Ukraine drones hit ship, Benghazi"),
    ("06:33", "India–NZ, day 5: NZ 157/4 at lunch"),
    ("SUNDAY NIGHT", "Foxx concedes; Democrats seal 258 seats"),
    ("MONDAY MORNING", "COP31 collapse leads world front pages"),
)


class Page:
    def __init__(self):
        self.image = Image.new("RGB", (2048, 2048), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.fonts = {}
        self.text_boxes = []

    def font(self, face, size):
        key = (face, size)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(
                str(FONT_DIR / FONTS[face]), round(size * SCALE)
            )
        return self.fonts[key]

    def text(self, x, y, value, size=10, face="sans", color=INK,
             width=None, minimum=None, center=False, cell=None):
        font = self.font(face, size)
        if width is not None:
            while self.draw.textlength(value, font=font) > (width - 2) * SCALE:
                size = round(size - 0.25, 2)
                if minimum is not None and size < minimum:
                    raise ValueError(f"Text is too long: {value}")
                font = self.font(face, size)
        length = self.draw.textlength(value, font=font) / SCALE
        if center:
            x -= length / 2
        else:
            x += 1  # Leave room for the font's half-pixel glyph overhangs.
        position = (round(x * SCALE), round(y * SCALE))
        box = self.draw.textbbox(position, value, font=font, anchor="lt")
        bounds = tuple(v / SCALE for v in box)
        if bounds[0] < 0 or bounds[1] < 0 or bounds[2] > 1024 or bounds[3] > 1024:
            raise ValueError(f"Text leaves the page: {value}")
        if cell is not None:
            left, top, right, bottom = cell
            if (bounds[0] < left or bounds[1] < top or bounds[2] > right
                    or bounds[3] > bottom):
                raise ValueError(f"Text leaves its cell: {value}")
        self.text_boxes.append((value, bounds, size))
        self.draw.text(position, value, font=font, fill=color, anchor="lt")

    def rect(self, box, fill=None, outline=None, width=1):
        self.draw.rectangle(tuple(round(v * SCALE) for v in box),
                            fill=fill, outline=outline, width=round(width * SCALE))

    def line(self, points, fill=RULE, width=1):
        self.draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                       fill=fill, width=round(width * SCALE))

    def polygon(self, points, fill, outline=None):
        self.draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                          fill=fill, outline=outline)

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.draw.ellipse(tuple(round(v * SCALE) for v in box),
                          fill=fill, outline=outline, width=round(width * SCALE))

    def arc(self, box, start, end, fill=BLUE, width=1):
        self.draw.arc(tuple(round(v * SCALE) for v in box), start, end,
                      fill=fill, width=round(width * SCALE))


def masthead(p):
    p.text(22, 20, "WORLD", 10, "bold", RED)
    p.text(22, 35, "DAILY BRIEFING", 7.8, "sans")
    p.text(910, 20, "44 STORIES", 9, "bold", RED)
    p.text(910, 35, "7 REGIONS · UTC", 7.8, "sans")
    p.text(512, 8, "THE WORLD TODAY", 51, "headline", center=True,
           width=754, minimum=47)
    p.text(512, 65, "MONDAY, 23 NOVEMBER 2026", 16, "bold", RED, center=True)
    p.line([(20, 87), (1004, 87)], INK, 1.5)


def lead(p):
    p.rect((20, 94, 1004, 360), PANEL)
    p.rect((20, 94, 26, 360), RED)
    p.text(38, 104, "CLIMATE  /  ANTALYA, TURKEY", 9, "bold", RED)
    p.text(36, 129, "COP31 COLLAPSES", 53, "headline", width=670, minimum=49)
    p.text(38, 195, "UN climate talks end on Sunday with no deal.", 17, "serif")
    facts = (
        "EU, UK, Panama, Marshall Islands and Norway rejected the draft.",
        "The final text made no mention of fossil fuels.",
        "Two days into overtime: the longest COP on record.",
        "Guterres: ‘deeply disappointed’; first no-deal COP since 2009.",
        "Next: COP32 in Addis Ababa, November 2027.",
    )
    for index, fact in enumerate(facts):
        p.rect((39, 228 + index * 21, 42, 231 + index * 21), RED)
        p.text(50, 223 + index * 21, fact, 12.8, "sans", width=630, minimum=12)
    p.text(38, 338, "FIRST WITHOUT AN OVERARCHING DEAL SINCE COPENHAGEN, 2009", 8.5, "bold", RED)

    # A globe under a visibly broken summit arc; every mark is a flat shape.
    p.ellipse((754, 165, 924, 335), PALE_BLUE, BLUE, 2)
    p.ellipse((792, 165, 886, 335), outline=BLUE, width=1)
    p.ellipse((820, 165, 858, 335), outline=BLUE, width=1)
    p.ellipse((757, 197, 921, 303), outline=BLUE, width=1)
    p.ellipse((755, 225, 923, 275), outline=BLUE, width=1)
    p.line([(755, 250), (924, 250)], BLUE, 1)
    p.polygon([(774, 218), (785, 204), (803, 207), (810, 222),
               (804, 237), (819, 253), (811, 273), (794, 260),
               (788, 237), (779, 237)], LAND)
    p.polygon([(852, 203), (871, 192), (898, 210), (909, 232),
               (891, 244), (875, 234), (867, 258), (851, 248),
               (858, 228), (843, 216)], LAND)
    p.polygon([(875, 280), (895, 282), (902, 297), (882, 306)], LAND)
    p.arc((730, 139, 948, 357), 185, 253, RED, 5)
    p.arc((730, 139, 948, 357), 287, 355, RED, 5)
    p.line([(804, 144), (813, 137), (807, 128)], RED, 2)
    p.line([(866, 145), (858, 138), (865, 130)], RED, 2)
    p.rect((882, 301, 944, 307), INK)
    p.polygon([(873, 281), (887, 265), (908, 283), (894, 299)], RED)
    p.line([(891, 282), (927, 313)], INK, 5)
    p.rect((894, 317, 951, 324), INK)
    p.text(833, 343, "NO DEAL", 10, "bold", RED, center=True)


def gulf_map(p):
    p.rect((30, 448, 337, 510), PALE_BLUE)
    # Schematic Gulf coasts, with labelled geographic pins and two tankers.
    p.polygon([(31, 449), (100, 449), (91, 456), (107, 464),
               (141, 476), (194, 488), (247, 496), (257, 510),
               (31, 510)], LAND)
    p.polygon([(119, 449), (337, 449), (337, 498), (302, 484),
               (274, 479), (244, 470), (207, 466), (169, 454)], LAND)
    p.line([(100, 449), (91, 456), (107, 464), (141, 476),
            (194, 488), (247, 496), (257, 510)], BLUE, 1)
    p.line([(169, 454), (207, 466), (244, 470), (274, 479),
            (302, 484), (337, 498)], BLUE, 1)
    p.text(39, 453, "GULF · SCHEMATIC", 6.5, "bold", BLUE)
    p.ellipse((129, 474, 135, 480), PAPER, BLUE, 1)
    for x, y in ((134, 477), (276, 485)):
        p.ellipse((x - 3, y - 7, x + 3, y - 1), RED)
        p.polygon([(x - 2, y - 2), (x + 2, y - 2), (x, y + 2)], RED)
    p.line([(133, 479), (111, 490)], RED, 0.5)
    p.text(42, 494, "BAHRAIN", 7, "bold", RED)
    p.line([(276, 486), (287, 503)], RED, 0.5)
    p.text(187, 499, "STRAIT OF HORMUZ", 7, "bold", RED)
    for x, y in ((186, 479), (240, 482)):
        p.polygon([(x - 8, y - 2), (x + 6, y - 2), (x + 9, y),
                   (x + 5, y + 3), (x - 8, y + 3)], INK)
        p.rect((x - 5, y - 5, x - 2, y - 2), INK)


def medium(p):
    for left, right in ((20, 347), (352, 674), (679, 1004)):
        p.rect((left, 366, right, 520), outline=RULE, width=0.6)
    p.text(30, 375, "US–IRAN WAR WIDENS", 16, "headline", width=307)
    p.text(30, 399, "Houthis claim Saudi refinery/radar strikes; ≥6 hurt.",
           9.4, width=307, minimum=8.5)
    p.text(30, 414, "Bahrain: two wounded Saturday; Pakistani resident critical.",
           9.4, width=307, minimum=8.5)
    p.text(30, 429, "US blockade: day 130. Iran's two-day ceasefire plan still on table.",
           9.4, width=307, minimum=8.5)
    gulf_map(p)

    p.text(362, 375, "DEMOCRATS' BIGGEST", 14.5, "headline", width=302)
    p.text(362, 393, "HOUSE MAJORITY SINCE 1992", 13.5, "headline", width=302)
    p.text(362, 416, "Hubbard beats Foxx by 330 of 287,000 votes; she concedes.",
           9.4, width=302, minimum=8.5)
    p.text(362, 431, "Gain of 44 seats; North Carolina: 11 of 14 Democratic.",
           9.4, width=302, minimum=8.5)
    p.text(362, 446, "Democrats control both chambers from 3 January.",
           9.4, width=302, minimum=8.5)
    p.text(362, 467, "258+", 31, "headline", BLUE)
    p.text(473, 472, "HOUSE SEATS", 8, "bold", BLUE)
    for row in range(3):
        for column in range(22):
            x = 475 + column * 8
            y = 488 + row * 6
            p.rect((x, y, x + 5, y + 3), BLUE)

    p.text(689, 375, "UKRAINE: DYMER TOLL 11", 15.5, "headline", width=305)
    p.text(689, 400, "Russian drone hit Dymer: 8 dead, one a teen; Kyiv region toll 11.",
           9.4, width=305, minimum=8.5)
    p.text(689, 415, "Vyshneve: two killed, eight hurt; Bila Tserkva: one killed.",
           9.4, width=305, minimum=8.5)
    p.text(689, 430, "Zelenskyy asks US to release Patriots already paid for via NATO.",
           9.4, width=305, minimum=8.5)
    # Five-storey block, a broken roofline, and a week-of-strikes graphic.
    p.text(697, 449, "SUNDAY", 6, "bold", RED)
    p.rect((697, 460, 755, 509), LAND)
    p.polygon([(697, 460), (697, 454), (718, 454), (725, 464),
               (731, 453), (742, 460), (755, 460)], BLUE)
    for row in range(5):
        for column in range(4):
            x = 703 + column * 12
            y = 463 + row * 9
            p.rect((x, y, x + 5, y + 4), PAPER)
    p.line([(730, 456), (724, 472), (733, 482), (727, 498)], RED, 1.5)
    p.text(770, 453, "RUSSIAN FIRE IN ONE WEEK", 7.5, "bold", BLUE)
    p.text(770, 466, "~2,700 drones · ~1,460 glide bombs", 9, width=221)
    p.text(770, 480, "165 missiles, Zelenskyy says", 9, width=221)
    p.text(770, 500, "ODESA POWER GRID DAMAGED", 7.5, "bold", RED)


def timeline(p):
    p.rect((20, 525, 1004, 595), PALE_BLUE)
    p.text(29, 530, "THE DAY IN UTC", 8.5, "bold", BLUE)
    for index, (time, label) in enumerate(TIMELINE):
        column = index % 5
        row = index // 5
        x = 29 + column * 196
        y = 545 + row * 25
        cell = (x, y, x + 188, y + 24)
        p.text(x, y, time, 8, "bold", cell=cell)
        p.text(x, y + 11, label, 7.8, width=188, minimum=7, cell=cell)
        if column:
            p.line([(x - 6, 545), (x - 6, 590)], "#b8c5c8", 0.5)


def briefs(p):
    if len(BRIEFS) != 40:
        raise ValueError("The newspaper must contain forty briefs")
    for column in range(4):
        x = 20 + column * 247
        if column:
            p.line([(x - 5, 600), (x - 5, 986)], RULE, 0.5)
        for row in range(10):
            index = column * 10 + row
            region, headline, detail = BRIEFS[index]
            y = 600 + row * 39
            cell = (x, y, x + 238, y + 38)
            p.text(x, y + 2, region, 6.5, "bold", RED, cell=cell)
            p.text(x, y + 12, headline, 10, "headline", width=238,
                   minimum=8.5, cell=cell)
            p.text(x, y + 26, detail, 8.4, width=238,
                   minimum=7.5, cell=cell)
            if row < 9:
                p.line([(x, y + 38), (x + 237, y + 38)], RULE, 0.4)


def footer(p):
    p.line([(20, 993), (1004, 993)], INK, 1)
    p.text(512, 1006,
           "THE WORLD TODAY — Monday 23 November 2026 — 44 stories from 7 regions — All times UTC.",
           10, "sans", center=True, width=984, minimum=9)


def render(output):
    p = Page()
    masthead(p)
    lead(p)
    medium(p)
    timeline(p)
    briefs(p)
    footer(p)
    # Validate every pair of actual glyph bounds before writing the image.
    for index, (value, box, _) in enumerate(p.text_boxes):
        for other, other_box, _ in p.text_boxes[index + 1:]:
            if (box[0] < other_box[2] and other_box[0] < box[2]
                    and box[1] < other_box[3] and other_box[1] < box[3]):
                raise ValueError(f"Overlapping text: {value!r} and {other!r}")
    final = p.image.resize((1024, 1024), Image.Resampling.LANCZOS)
    # Keep a small set of antialiasing shades without changing the RGB output.
    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(PALETTE)
    final = final.quantize(palette=palette_image,
                           dither=Image.Dither.NONE).convert("RGB")
    final.save(output, format="PNG", optimize=True, compress_level=9)
    print(f"Rendered {output}: 1024 × 1024 RGB; 44 stories, 7 regions")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().with_name("entry.png"))
    args = parser.parse_args()
    render(args.output)
