from easy_pil import Editor, Canvas, load_image_async
from nextcord import File, Member
from PIL import ImageFont, Image, ImageColor, ImageDraw
import numpy as np
import textwrap
import time

levelsx = {
    0: 0,
    1: 100,
    2: 255,
    3: 475,
    4: 770,
    5: 1150,
    6: 1625,
    7: 2205,
    8: 2900,
    9: 3720,
    10: 4675,
    11: 5775,
    12: 7030,
    13: 8450,
    14: 10045,
    15: 11825,
    16: 13800,
    17: 15980,
    18: 18375,
    19: 20995,
    20: 23850,
    21: 26950,
    22: 30305,
    23: 33925,
    24: 37820,
    25: 42000,
    26: 46475,
    27: 51255,
    28: 56350,
    29: 61770,
    30: 67525,
    31: 73625,
    32: 80080,
    33: 86900,
    34: 94095,
    35: 101675,
    36: 109650,
    37: 118030,
    38: 126825,
    39: 136045,
    40: 145700,
    41: 155800,
    42: 166355,
    43: 177375,
    44: 188870,
    45: 200850,
    46: 213325,
    47: 226305,
    48: 239800,
    49: 253820,
    50: 268375,
    51: 283475,
    52: 299130,
    53: 315350,
    54: 332145,
    55: 349525,
    56: 367500,
    57: 386080,
    58: 405275,
    59: 425095,
    60: 445550,
    61: 466650,
    62: 488405,
    63: 510825,
    64: 533920,
    65: 557700,
    66: 582175,
    67: 607355,
    68: 633250,
    69: 659870,
    70: 687225,
    71: 715325,
    72: 744180,
    73: 773800,
    74: 804195,
    75: 835375,
    76: 867350,
    77: 900130,
    78: 933725,
    79: 968145,
    80: 1003400,
    81: 1039500,
    82: 1076455,
    83: 1114275,
    84: 1152970,
    85: 1192550,
    86: 1233025,
    87: 1274405,
    88: 1316700,
    89: 1359920,
    90: 1404075,
    91: 1449175,
    92: 1495230,
    93: 1542250,
    94: 1590245,
    95: 1639225,
    96: 1689200,
    97: 1740180,
    98: 1792175,
    99: 1845195,
    100: 1899250,
}


class oldstat:
    def __init__(self):
        self.balls: int = 0
        self.quote: str = None
        self.name: str = None
        self.avatar: str = None
        self.color: str = None
        self.path: str = "https://raw.githubusercontent.com/I-dan-mi-I/images/main/cards/%D0%B0%D0%BD%D0%B5%D0%BC%D0%BE%D0%BD%D0%B8%D1%8F.png"

    async def create(self):
        # changes after 1.0.9

        background = await load_image_async(str(self.path))
        background = Editor(background).resize((850, 140))

        if self.avatar != None:
            profile = await load_image_async(str(self.avatar))
            profile = Editor(profile).resize((124, 124)).circle_image()
            background.paste(profile.image, (8, 12))

        # ball = Editor('./stats/cards/ball.png').resize((34, 34))
        # background.paste(ball.image, (715, 92))

        plainoit = ImageFont.truetype(
            "./card/fonts/plainoit_ed.ttf", 60, encoding="unic"
        )
        plainoit_small = ImageFont.truetype(
            "./card/fonts/plainoit.ttf", 35, encoding="unic"
        )

        background.text((200, 12), self.name, font=plainoit, color=self.color)

        background.rectangle((200, 72), width=350, height=4, fill="violet")
        background.text(
            (200, 92),
            self.quote,
            font=plainoit_small,
            color=self.color,
        )

        # background.text(
        #     (754, 92),
        #     f": {self.balls}",
        #     font=plainoit_small,
        #     color=self.color,
        # )

        file = File(fp=background.image_bytes, filename="card.png")
        return file


class newstat:
    def __init__(self):
        self.coin: int = 0
        self.voicetime: int = 0
        self.cookie: int = 0
        self.xp: int = 0
        self.lvl: int = 3
        self.quote: str = None
        self.name: str = None
        self.avatar: str = None
        self.color: str = "white"
        self.path: str = "https://raw.githubusercontent.com/I-dan-mi-I/images/main/cards/%D0%B0%D0%BD%D0%B5%D0%BC%D0%BE%D0%BD%D0%B8%D1%8F.png"

    async def create(self):
        # changes after 1.0.9

        # background = await load_image_async(str(self.path))
        background = Editor(
            Image.open(
                self.path.replace(
                    r"https://raw.githubusercontent.com/I-dan-mi-I/images/main/cards/",
                    "./card/layout/cards/",
                )
            )
        ).resize((872, 140))

        if self.avatar != None:
            profile = await load_image_async(str(self.avatar))
            profile = Editor(profile).resize((124, 124)).circle_image()
            background.paste(profile.image, (8, 8))

        # ball = Editor('./stats/cards/ball.png').resize((34, 34))
        # background.paste(ball.image, (715, 92))

        plainoit60 = ImageFont.truetype(
            "./card/fonts/plainoit_ed.ttf", 60, encoding="unic"
        )
        plainoit24 = ImageFont.truetype(
            "./card/fonts/plainoit_ed.ttf", 24, encoding="unic"
        )

        background.text((140, 8), self.name, font=plainoit60, color=self.color)

        background.text(
            (145, 60),
            self.quote,
            font=plainoit24,
            color=self.color,
        )

        background.rectangle(
            (140, 83), width=704, height=44, fill="darkorange", radius=20
        )
        background.bar(
            (140, 83),
            max_width=704,
            height=44,
            percentage=(
                (int(self.xp) - levelsx[self.lvl])
                / (levelsx[self.lvl + 1] - levelsx[self.lvl])
            )
            * 100,
            fill="orange",
            radius=20,
        )

        # background.text(
        #     (754, 92),
        #     f"§: {self.coin}",
        #     font=plainoit_small,
        #     color=self.color,
        # )

        hours = self.voicetime // 3600
        minutes = (self.voicetime % 3600) // 60
        if minutes < 10:
            minutes = "0" + str(minutes)
        seconds = (self.voicetime % 3600) % 60
        if seconds < 10:
            seconds = "0" + str(seconds)

        img = Image.open(background.image_bytes)
        d = ImageDraw.Draw(img)
        d.multiline_text(
            (844, 32),
            f"§{self.coin} ©{self.cookie} ®{hours}:{minutes}:{seconds}\n{self.xp}/{levelsx[self.lvl+1]} XP LVL: {self.lvl}",
            font=plainoit24,
            fill=self.color,
            align="right",
            anchor="ra",
        )

        background = Editor(img)

        file = File(fp=background.image_bytes, filename="card.png")
        return file
