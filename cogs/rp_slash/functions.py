import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
from typing import Optional
from random import randint
from faker import Faker
import requests
from random import choice
from .phrases import *
from .pictures import *
from datetime import datetime


def not_seals_check(ctx: Context) -> bool:
    return ctx.guild.id != 876474448126050394


def seals_check(ctx: Context) -> bool:
    return ctx.guild.id == 876474448126050394


def app_not_seals_check(interaction: nextcord.Interaction) -> bool:
    return interaction.guild.id != 876474448126050394


def app_seals_check(interaction: nextcord.Interaction) -> bool:
    return interaction.guild.id == 876474448126050394


class RPSlash(commands.Cog, name="RolePlay [Slash Commands]"):
    """RolePlay команды"""

    COG_EMOJI: str = "🎭"

    def __init__(self, bot):
        self.bot = bot

    # @nextcord.user_command(guild_ids=[], force_global=True, name="Совместимость")
    async def ship_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.ship_action(interaction, member)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Проверка совместимости"
    )
    async def ship(
        self,
        interaction: nextcord.Interaction,
        member_1: Optional[nextcord.Member] = nextcord.SlashOption(required=True),
        member_2: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        await self.ship_action(interaction, member_1, member_2)

    async def ship_action(
        self,
        interaction: nextcord.Interaction,
        пользователь: nextcord.Member,
        member: Optional[nextcord.Member] = None,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        if not isinstance(member, nextcord.Member):
            if пользователь != interaction.user:
                embed: nextcord.Embed = nextcord.Embed(
                    title=f"{interaction.user.display_name} совместим с {пользователь.display_name} на {randint(0, 100)}%.",
                    colour=nextcord.Colour.random(),
                )
                mention = f"{interaction.user.mention}+{пользователь.mention}"
            else:
                embed: nextcord.Embed = nextcord.Embed(
                    title=f"{interaction.user.display_name}, вы отлично совместимы с собой. Любите себя :)",
                    colour=nextcord.Colour.random(),
                )
                mention = f"{interaction.user.mention}"
        else:
            if пользователь != member:
                embed: nextcord.Embed = nextcord.Embed(
                    title=f"{пользователь.display_name} совместим с {member.display_name} на {randint(0, 100)}%.",
                    colour=nextcord.Colour.random(),
                )
                mention = f"{пользователь.mention}+{member.mention}"
            else:
                embed: nextcord.Embed = nextcord.Embed(
                    title=f"{пользователь.display_name} отлично совместим с собой",
                    colour=nextcord.Colour.random(),
                )
                mention = f"{пользователь.mention}"

        return await interaction.send(mention, embed=embed)

    @nextcord.slash_command(
        guild_ids=[],
        force_global=True,
        description="Шуточное разоблачение пользователя",
    )
    async def exposure(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        if isinstance(пользователь, nextcord.Member):
            user: nextcord.Member = пользователь
        else:
            user: nextcord.Member = interaction.user

        await self.exposure_action(interaction, user)

    # @nextcord.user_command(guild_ids=[], force_global=True, name="Разоблачить")
    async def exposure_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.exposure_action(interaction, member)

    async def exposure_action(
        self, interaction: nextcord.Interaction, user: nextcord.Member
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        message = await interaction.send(
            f"*Все данные случайны, а совпадения с реальностью непреднамеренные.*\n{user.mention} заранее извиняемся за доставленные неудобства"
        )

        faker = Faker("ru-RU")

        emb: nextcord.Embed = nextcord.Embed(
            title=f"Разоблачение пользователя *__{user.display_name}__*"
        )

        if randint(0, 1):
            emb.add_field(name="ФИО", value=faker.name_male(), inline=True)
        else:
            emb.add_field(name="ФИО", value=faker.name_female(), inline=True)

        emb.add_field(name="Дата рождения", value=faker.date_of_birth(), inline=True)
        emb.add_field(name="Место проживания", value=faker.address(), inline=False)
        emb.add_field(name="Профессия", value=faker.job(), inline=False)
        await message.edit(embed=emb)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Обнять пользователя"
    )
    async def hug(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        await self.hug_action(interaction, пользователь)

    @nextcord.user_command(guild_ids=[], force_global=True, name="Обнять")
    async def hug_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.hug_action(interaction, member)

    @staticmethod
    async def hug_action(
        interaction: nextcord.Interaction,
        member: Optional[nextcord.Member] = None,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} обнимает ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.title += f"сам себя. {alone}"
            mention = None
        else:
            embed.title += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        if app_seals_check(interaction) and randint(0, 1) == 0:
            embed.set_image(url=choice(hug))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/hug/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @nextcord.slash_command(guild_ids=[], force_global=True, description="Улыбнуться")
    async def smile(
        self,
        interaction: nextcord.Interaction,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} улыбается. {choice(smile_phrases)}"
        )

        r: requests.Response = requests.get(
            "https://purrbot.site/api/img/sfw/smile/gif"
        )

        emb.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await interaction.followup.send(embed=emb)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Тыкнуть пользователя"
    )
    async def poke(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        await self.poke_action(interaction, пользователь)

    # @nextcord.user_command(guild_ids=[], force_global=True, name="Тыкнуть")
    async def poke_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.poke_action(interaction, member)

    async def poke_action(
        self,
        interaction: nextcord.Interaction,
        member: Optional[nextcord.Member] = None,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} тыкает ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.title += "сам себя."
            mention = None
        else:
            embed.title += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/poke/gif")
        embed.set_image(url=r.json()["link"])
        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Дать пощёчину пользователю"
    )
    async def slap(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        await self.slap_action(interaction, пользователь)

    @nextcord.user_command(guild_ids=[], force_global=True, name="Дать пощёчину")
    async def slap_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.slap_action(interaction, member)

    async def slap_action(
        self,
        interaction: nextcord.Interaction,
        member: Optional[nextcord.Member] = None,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} даёт пощёчину ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.title += f"самому себе. {alone}"
            mention = None
        else:
            embed.title += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        if app_seals_check(interaction) and randint(0, 1) == 0:
            embed.set_image(url=choice(slap))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/slap/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Укусить пользователя"
    )
    async def bite(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        await self.bite_action(interaction, пользователь)

    @nextcord.user_command(guild_ids=[], force_global=True, name="Укусить")
    async def bite_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.bite_action(interaction, member)

    async def bite_action(
        self,
        interaction: nextcord.Interaction,
        member: Optional[nextcord.Member] = None,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} кусает ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.title += f"сам себя. {alone}"
            mention = None
        else:
            embed.title += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        if app_seals_check(interaction) and randint(0, 1) == 0:
            embed.set_image(url=choice(bite))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/bite/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @nextcord.slash_command(guild_ids=[], force_global=True, description="Заплакать")
    async def cry(
        self,
        interaction: nextcord.Interaction,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} плачет."
        )

        emb.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/cry/gif")

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await interaction.followup.send(embed=emb)

    @nextcord.slash_command(guild_ids=[], force_global=True, description="Покраснеть")
    async def blush(
        self,
        interaction: nextcord.Interaction,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} краснеет."
        )

        r: requests.Response = requests.get(
            "https://purrbot.site/api/img/sfw/blush/gif"
        )

        emb.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await interaction.followup.send(embed=emb)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Поцеловать пользователя"
    )
    async def kiss(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        await self.kiss_action(interaction, пользователь)

    @nextcord.user_command(guild_ids=[], force_global=True, name="Поцеловать")
    async def kiss_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.kiss_action(interaction, member)

    async def kiss_action(
        self,
        interaction: nextcord.Interaction,
        member: Optional[nextcord.Member] = None,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} целует ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.title += f"сам себя. {alone}"
            mention = None
        else:
            embed.title += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        if app_seals_check(interaction) and randint(0, 1) == 0:
            embed.set_image(url=choice(kiss))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/kiss/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Лизнуть пользователя"
    )
    async def lick(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} облизывает ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if пользователь is None or пользователь == interaction.user:
            embed.title += f"сам себя. {alone}"
            mention = None
        else:
            embed.title += пользователь.display_name
            mention = пользователь.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        if app_seals_check(interaction) and randint(0, 1) == 0:
            embed.set_image(url=choice(lick))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/lick/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Погладить пользователя"
    )
    async def pat(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        await self.pat_action(interaction, пользователь)

    @nextcord.user_command(guild_ids=[], force_global=True, name="Погладить")
    async def pat_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.pat_action(interaction, member)

    async def pat_action(
        self,
        interaction: nextcord.Interaction,
        member: Optional[nextcord.Member] = None,
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name} гладит ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.title += f"сам себя. {alone}"
            mention = None
        else:
            embed.title += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/pat/gif")
        embed.set_image(url=r.json()["link"])
        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Спать/уложить спать пользователя"
    )
    async def sleep(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            colour=nextcord.Colour.random(), timestamp=datetime.now()
        )

        if пользователь is None or пользователь == interaction.user:
            embed.title = f"{interaction.user.display_name} спит"
            embed.set_image(url=choice(sleep))
            mention = None
        else:
            embed.title = f"{interaction.user.display_name} укладывает спать {пользователь.display_name}"
            embed.set_image(url=choice(sleep_two))
            mention = пользователь.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Покормить пользователя"
    )
    async def feed(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")

        embed: nextcord.Embed = nextcord.Embed(
            colour=nextcord.Colour.random(), timestamp=datetime.now()
        )

        if пользователь is None or пользователь == interaction.user:
            embed.title = f"{interaction.user.display_name} кушает."
            mention = None
        else:
            embed.title = (
                f"{interaction.user.display_name} кормит {пользователь.display_name}"
            )
            mention = пользователь.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        if app_seals_check(interaction) and randint(0, 1) == 0:
            embed.set_image(url=choice(feed))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/feed/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(RPSlash(bot))
