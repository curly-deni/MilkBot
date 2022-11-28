from datetime import datetime
from random import randint
from typing import Optional

import nextcord
import requests
from base.base_cog import MilkCog


class RPSlash(MilkCog, name="RolePlay [Slash Commands]"):
    """RolePlay команды"""

    COG_EMOJI: str = "🎭"

    def __init__(self, bot):
        self.bot = bot

    @MilkCog.slash_command(description="Обнять пользователя")
    async def hug(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=False
        ),
    ):
        await self.hug_action(interaction, user)

    @nextcord.user_command(guild_ids=[], force_global=True, name="Обнять")
    async def hug_button(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await self.hug_action(interaction, member)

    async def hug_action(
        self,
        interaction: nextcord.Interaction,
        member: Optional[nextcord.Member] = None,
    ):

        embed = nextcord.Embed(
            description=f"{interaction.user.display_name} обнимает ",
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.description += f"сам себя."
            mention = None
        else:
            embed.description += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        custom_gif = self.bot.database.get_hug_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/hug/gif"
            )
            embed.set_image(url=r.json()["link"])

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @MilkCog.slash_command(description="Улыбнуться")
    async def smile(
        self,
        interaction: nextcord.Interaction,
    ):

        emb = nextcord.Embed(
            title=f"{interaction.user.display_name} улыбается.",
            timestamp=datetime.now(),
        )

        custom_gif = self.bot.database.get_smile_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            emb.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/smile/gif"
            )
            emb.set_image(url=r.json()["link"])
        await interaction.followup.send(embed=emb)

    @MilkCog.slash_command(description="Тыкнуть пользователя")
    async def poke(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=False
        ),
    ):

        embed = nextcord.Embed(
            description=f"{interaction.user.display_name} тыкает ",
            timestamp=datetime.now(),
        )

        if user is None or user == interaction.user:
            embed.description += "сам себя."
            mention = None
        else:
            embed.description += user.display_name
            mention = user.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        custom_gif = self.bot.database.get_poke_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/poke/gif"
            )
            embed.set_image(url=r.json()["link"])
        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @MilkCog.slash_command(description="Дать пощёчину пользователю")
    async def slap(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=False
        ),
    ):
        await self.slap_action(interaction, user)

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

        embed = nextcord.Embed(
            description=f"{interaction.user.display_name} даёт пощёчину ",
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.description += f"самому себе."
            mention = None
        else:
            embed.description += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        custom_gif = self.bot.database.get_slap_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/slap/gif"
            )
            embed.set_image(url=r.json()["link"])

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @MilkCog.slash_command(description="Укусить пользователя")
    async def bite(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=False
        ),
    ):
        await self.bite_action(interaction, user)

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

        embed = nextcord.Embed(
            description=f"{interaction.user.display_name} кусает ",
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.description += f"сам себя."
            mention = None
        else:
            embed.description += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        custom_gif = self.bot.database.get_bite_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/bite/gif"
            )
            embed.set_image(url=r.json()["link"])

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @MilkCog.slash_command(description="Заплакать")
    async def cry(
        self,
        interaction: nextcord.Interaction,
    ):

        emb = nextcord.Embed(
            title=f"{interaction.user.display_name} плачет.", timestamp=datetime.now()
        )

        custom_gif = self.bot.database.get_cry_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            emb.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/cry/gif"
            )
            emb.set_image(url=r.json()["link"])
        await interaction.followup.send(embed=emb)

    @MilkCog.slash_command(description="Покраснеть")
    async def blush(
        self,
        interaction: nextcord.Interaction,
    ):

        emb = nextcord.Embed(
            title=f"{interaction.user.display_name} краснеет.", timestamp=datetime.now()
        )
        custom_gif = self.bot.database.get_blush_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            emb.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/blush/gif"
            )
            emb.set_image(url=r.json()["link"])
        await interaction.send(embed=emb)

    @MilkCog.slash_command(description="Поцеловать пользователя")
    async def kiss(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=False
        ),
    ):
        await self.kiss_action(interaction, user)

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

        embed = nextcord.Embed(
            description=f"{interaction.user.display_name} целует ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.description += f"сам себя."
            mention = None
        else:
            embed.description += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        custom_gif = self.bot.database.get_kiss_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/kiss/gif"
            )
            embed.set_image(url=r.json()["link"])

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @MilkCog.slash_command(description="Лизнуть пользователя")
    async def lick(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=False
        ),
    ):

        embed = nextcord.Embed(
            description=f"{interaction.user.display_name} облизывает ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if user is None or user == interaction.user:
            embed.description += f"сам себя."
            mention = None
        else:
            embed.description += user.display_name
            mention = user.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        custom_gif = self.bot.database.get_lick_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/lick/gif"
            )
            embed.set_image(url=r.json()["link"])

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @MilkCog.slash_command(description="Погладить пользователя")
    async def pat(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=False
        ),
    ):
        await self.pat_action(interaction, user)

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

        embed = nextcord.Embed(
            description=f"{interaction.user.display_name} гладит ",
            timestamp=datetime.now(),
        )

        if member is None or member == interaction.user:
            embed.description += f"сам себя."
            mention = None
        else:
            embed.description += member.display_name
            mention = member.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        custom_gif = self.bot.database.get_pat_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/pat/gif"
            )
            embed.set_image(url=r.json()["link"])
        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)

    @MilkCog.slash_command(description="Покормить пользователя")
    async def feed(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=False
        ),
    ):

        embed = nextcord.Embed(
            colour=nextcord.Colour.random(), timestamp=datetime.now()
        )

        if user is None or user == interaction.user:
            embed.description = f"{interaction.user.display_name} кушает."
            mention = None
        else:
            embed.description = (
                f"{interaction.user.display_name} кормит {user.display_name}"
            )
            mention = user.mention

        if mention is not None:
            message = await interaction.send(mention)
        else:
            message = None
            await interaction.response.defer()

        custom_gif = self.bot.database.get_feed_gif(interaction.guild.id)
        if custom_gif is not None and randint(0, 1):
            embed.set_image(url=custom_gif)
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/feed/gif"
            )
            embed.set_image(url=r.json()["link"])

        if message is None:
            await interaction.followup.send(embed=embed)
        else:
            await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(RPSlash(bot))
