import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
import requests


class Events(commands.Cog, name="Активности"):
    """Организация активностей в голосовых каналах"""

    COG_EMOJI = "🎲"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["youtube", "yt"], brief="Совместный просмотр роликов с YouTube"
    )
    async def ютуб(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "880218394199220334",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(
            f"Приятного просмотра!\nhttps://discord.com/invite/{invite_id}",
            delete_after=35,
        )

    @ютуб.error
    async def youtube_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["chess"], brief="Шахматы для участников голосового канала"
    )
    async def шахматы(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "832012774040141894",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @шахматы.error
    async def chess_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(aliases=["poker"], brief="Покер для участников голосового канала")
    async def покер(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "755827207812677713",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @покер.error
    async def poker_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["fishing"], brief="Рыбалка для участников голосового канала"
    )
    async def рыбалка(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "814288819477020702",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @рыбалка.error
    async def fishing_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["among", "амонгус", "betrayal"],
        brief="Among Us для участников голосового канала",
    )
    async def among_us(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "773336526917861400",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @among_us.error
    async def betrayal_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["doodle", "doodlecrew", "dcrew"],
        brief="DoodleCrew для участников голосового канала",
    )
    async def doodle_crew(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "878067389634314250",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @doodle_crew.error
    async def doodle_crew_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["letter", "lettertile", "lt"],
        brief="LetterTile для участников голосовго канала",
    )
    async def letter_tile(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "879863686565621790",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @letter_tile.error
    async def letter_tile_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["spellcast", "sc"], brief="SpellCast для участников голосового канала"
    )
    async def spell_cast(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "852509694341283871",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @spell_cast.error
    async def spellcast_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(aliases=["checkers"], brief="Шашки для участников сервера")
    async def шашки(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "832013003968348200",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @шашки.error
    async def checkers_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["wordsnacks", "ws"],
        brief="WordSnacks для участников голосового канала",
    )
    async def word_snacks(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "879863976006127627",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @word_snacks.error
    async def wordsnacks_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["sh", "sketchheads", "sketch"],
        brief="SketchHeads для участников голосового канала",
    )
    async def sketch_heads(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "902271654783242291",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @sketch_heads.error
    async def sketch_heads_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["ll", "letterleague"],
        brief="Letter League для участников голосового канала",
    )
    async def letter_league(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "879863686565621790",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @letter_league.error
    async def letter_league_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["ocho", "blazing", "blazing8s", "Blazing8s"],
        brief="Blazing 8s для участников голосового канала",
    )
    async def blazing8(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "832025144389533716",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @blazing8.error
    async def blazing8_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(
        aliases=["sketchyartist", "sa", "sketchy"],
        brief="Sketchy Artist для участников голосового канала",
    )
    async def sketchy_artist(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "879864070101172255",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @sketchy_artist.error
    async def sketchy_artist_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")

    @commands.command(brief="Awkword для участников голосового канала")
    async def awkword(self, ctx: Context):
        api_endpoint = f"https://discord.com/api/v8/channels/{ctx.message.author.voice.channel.id}/invites"
        data = {
            "max_age": 86400,
            "max_uses": 0,
            "target_application_id": "879863881349087252",
            "target_type": 2,
            "temporary": False,
        }
        headers = {
            "Authorization": f"Bot {self.bot.settings['token']}",
            "Content-Type": "application/json",
        }
        r = requests.post(api_endpoint, json=data, headers=headers)
        r.raise_for_status()
        invite_id = r.json()["code"]
        await ctx.send(f"https://discord.com/invite/{invite_id}", delete_after=35)

    @awkword.error
    async def awkword_error(self, ctx: Context, error: commands.CommandError):
        await ctx.send("Вы не находитесь в голосовой канале.")


def setup(bot):
    bot.add_cog(Events(bot))
