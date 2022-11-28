from datetime import datetime
from random import randint
from typing import Optional

import nextcord
import requests
from base.base_cog import MilkCog
from faker import Faker
from nextcord.ext.commands import Context


class RP(MilkCog, name="RolePlay"):
    """RolePlay команды"""

    COG_EMOJI: str = "🎭"

    def __init__(self, bot):
        self.bot = bot

    @MilkCog.slash_command(description="Проверка совместимости")
    async def ship(
        self,
        interaction: nextcord.Interaction,
        member_1: Optional[nextcord.Member] = nextcord.SlashOption(
            name="первый",
            description="первый пользователь для шипа, в случае отсутствия второго, шипперится с автором",
            required=True,
        ),
        member_2: Optional[nextcord.Member] = nextcord.SlashOption(
            name="второй",
            description="второй пользователь для шипа",
            required=False,
        ),
    ):

        if not isinstance(member_2, nextcord.Member):
            if member_1 != interaction.user:
                embed = nextcord.Embed(
                    title=f"{interaction.user.display_name} совместим с {member_1.display_name} на {randint(0, 100)}%.",
                    timestamp=datetime.now(),
                )
                mention = f"{interaction.user.mention}+{member_1.mention}"
            else:
                embed = nextcord.Embed(
                    title=f"{interaction.user.display_name}, вы отлично совместимы с собой. Любите себя :)",
                    timestamp=datetime.now(),
                )
                mention = f"{interaction.user.mention}"
        else:
            if member_1 != member_2:
                embed = nextcord.Embed(
                    title=f"{member_1.display_name} совместим с {member_2.display_name} на {randint(0, 100)}%.",
                    timestamp=datetime.now(),
                )
                mention = f"{member_1.mention}+{member_2.mention}"
            else:
                embed = nextcord.Embed(
                    title=f"{member_1.display_name} отлично совместим с собой",
                    timestamp=datetime.now(),
                )
                mention = f"{member_1.mention}"

        return await interaction.send(mention, embed=embed)

    @MilkCog.slash_command(
        description="Шуточное разоблачение пользователя",
    )
    async def exposure(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь",
            description="пользователь для разоблачения",
            required=False,
        ),
    ):
        if not isinstance(user, nextcord.Member):
            user: nextcord.Member = interaction.user

        message = await interaction.send(
            f"*Все данные случайны, а совпадения с реальностью непреднамеренные.*\n{user.mention} заранее извиняемся за доставленные неудобства"
        )

        faker = Faker("ru-RU")

        emb = nextcord.Embed(
            title=f"Разоблачение пользователя *__{user.display_name}__*",
            timestamp=datetime.now(),
        )

        if randint(0, 1):
            emb.add_field(name="ФИО", value=faker.name_male(), inline=True)
        else:
            emb.add_field(name="ФИО", value=faker.name_female(), inline=True)

        emb.add_field(name="Дата рождения", value=faker.date_of_birth(), inline=True)
        emb.add_field(name="Место проживания", value=faker.address(), inline=False)
        emb.add_field(name="Профессия", value=faker.job(), inline=False)
        await message.edit(embed=emb)

    @MilkCog.message_command(
        name="обнять", brief="Обнять пользователя", aliases=["cuddle", "hug"]
    )
    async def hug(self, ctx: Context):

        embed = nextcord.Embed(
            description=f"{ctx.author.display_name} обнимает ",
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.description += f"сам себя."
        else:
            embed.description += ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        custom_gif = self.bot.database.get_hug_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/hug/gif"
            )
            embed.set_image(url=r.json()["link"])

        await ctx.send(embed=embed)

    @MilkCog.message_command(name="улыбнуться", brief="Улыбнуться", aliases=["smile"])
    async def smile(self, ctx: Context):

        emb = nextcord.Embed(
            description=f"{ctx.author.display_name} улыбается.",
            timestamp=datetime.now(),
        )

        custom_gif = self.bot.database.get_smile_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            emb.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/smile/gif"
            )
            emb.set_image(url=r.json()["link"])
        await ctx.send(embed=emb)

    @MilkCog.message_command(name="тык", brief="Тыкнуть пользователя", aliases=["poke"])
    async def poke(self, ctx: Context):

        embed = nextcord.Embed(
            description=f"{ctx.author.display_name} тыкает ",
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.description += "сам себя."
        else:
            embed.description += ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        custom_gif = self.bot.database.get_poke_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/poke/gif"
            )
            embed.set_image(url=r.json()["link"])
        await ctx.send(embed=embed)

    @MilkCog.message_command(
        name="пощёчина", brief="Дать пощёчину пользователю", aliases=["slap"]
    )
    async def slap(self, ctx: Context):
        embed = nextcord.Embed(
            description=f"{ctx.author.display_name} даёт пощёчину ",
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.description += f"самому себе."
        else:
            embed.description += ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        custom_gif = self.bot.database.get_slap_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/slap/gif"
            )
            embed.set_image(url=r.json()["link"])

        await ctx.send(embed=embed)

    @MilkCog.message_command(
        name="ударить", brief="Ударить пользователю", aliases=["bite"]
    )
    async def bite(self, ctx: Context):

        embed = nextcord.Embed(
            description=f"{ctx.author.display_name} ударяет ",
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.description += f"сам себя."
        else:
            embed.description += ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        custom_gif = self.bot.database.get_bite_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/bite/gif"
            )
            embed.set_image(url=r.json()["link"])

        await ctx.send(embed=embed)

    @MilkCog.message_command(name="заплакать", brief="Заплакать", aliases=["cry"])
    async def cry(self, ctx: Context):

        emb = nextcord.Embed(
            description=f"{ctx.author.display_name} плачет.", timestamp=datetime.now()
        )

        custom_gif = self.bot.database.get_cry_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            emb.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/cry/gif"
            )
            emb.set_image(url=r.json()["link"])
        await ctx.send(embed=emb)

    @MilkCog.message_command(name="покраснеть", brief="Покраснеть", aliases=["blush"])
    async def blush(self, ctx):

        emb = nextcord.Embed(
            description=f"{ctx.author.display_name} краснеет.", timestamp=datetime.now()
        )

        custom_gif = self.bot.database.get_blush_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            emb.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/blush/gif"
            )
            emb.set_image(url=r.json()["link"])
        await ctx.send(embed=emb)

    @MilkCog.message_command(
        name="поцеловать", brief="Поцеловать пользователя", aliases=["kiss"]
    )
    async def kiss(self, ctx: Context):

        embed = nextcord.Embed(
            description=f"{ctx.author.display_name} целует ",
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.description += f"сам себя."
        else:
            embed.description += ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        custom_gif = self.bot.database.get_kiss_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/kiss/gif"
            )
            embed.set_image(url=r.json()["link"])

        await ctx.send(embed=embed)

    @MilkCog.message_command(
        name="лизнуть", brief="Лизнуть пользователя", aliases=["lick"]
    )
    async def lick(self, ctx: Context):
        embed = nextcord.Embed(
            description=f"{ctx.author.display_name} облизывает ",
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.description += f"сам себя."
        else:
            embed.description += ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        custom_gif = self.bot.database.get_lick_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/lick/gif"
            )
            embed.set_image(url=r.json()["link"])

        await ctx.send(embed=embed)

    @MilkCog.message_command(
        name="погладить", brief="Погладить пользователя", aliases=["pat"]
    )
    async def pat(self, ctx: Context):

        embed = nextcord.Embed(
            description=f"{ctx.author.display_name} гладит ",
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.description += f"сам себя."
        else:
            embed.description += ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        custom_gif = self.bot.database.get_pat_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/pat/gif"
            )
            embed.set_image(url=r.json()["link"])
        await ctx.send(embed=embed)

    @MilkCog.message_command(
        name="покормить", brief="Покормить пользователя", aliases=["feed"]
    )
    async def feed(self, ctx: Context):
        embed = nextcord.Embed(timestamp=datetime.now())

        if not ctx.message.mentions:
            embed.description = f"{ctx.author.display_name} кушает."
        else:
            embed.description = f"{ctx.author.display_name} кормит " + ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        custom_gif = self.bot.database.get_feed_gif(ctx.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/feed/gif"
            )
            embed.set_image(url=r.json()["link"])

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RP(bot))
