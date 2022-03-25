from easy_pil import Editor, Canvas, load_image_async
from nextcord import File, Member
from PIL import ImageFont, Image, ImageColor, ImageDraw
import numpy as np
import textwrap
import time


class love_compatibility:
    def __init__(self):
        self.avatar1: str = None
        self.comp: int = 100
        self.avatar2: str = None
        self.color = (241, 149, 149)

    async def create(self):
        # changes after 1.0.9

        background = Editor("./card/layout/rp/love_compatibility.png")

        if self.avatar1 != None:
            profile = await load_image_async(str(self.avatar1))
            profile = Editor(profile).resize((237, 237))
            background.paste(profile.image, (208, 77))

        if self.avatar2 != None:
            profile = await load_image_async(str(self.avatar2))
            profile = Editor(profile).resize((237, 237))
            background.paste(profile.image, (761, 77))

        myriad = ImageFont.truetype("./card/fonts/myriad-pro.OTF", 60, encoding="unic")

        if self.comp < 10:
            background.text(
                (560, 144),
                f"{self.comp}%",
                font=myriad,
                color=self.color,
            )
        elif 10 <= self.comp < 100:
            background.text(
                (539, 144),
                f"{self.comp}%",
                font=myriad,
                color=self.color,
            )
        else:
            background.text(
                (520, 144),
                f"{self.comp}%",
                font=myriad,
                color=self.color,
            )

        file = File(fp=background.image_bytes, filename="card.png")
        return file
