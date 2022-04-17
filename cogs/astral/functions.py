# for nextcord
import asyncio

import nextcord
from nextcord.ext import commands
from async_timeout import timeout

from .ui import AstralPlayersStart, AstralBotStart, AstralBossStart, GameMessage
from .api import AstralGameSession
from additional.check_permission import check_admin_permissions

from database.serversettings import getAstralTable

import requests
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Astral(commands.Cog, name="Астрал"):
    """Стратегическая игра Астрал."""

    COG_EMOJI = "🌰"

    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.command(brief="Остановка игры администратором")
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def астрал_стоп(self, ctx):
        try:
            game = self.games[ctx.guild.id]
            game.stop()
            del self.games[game.channel.guild.id]
            return await ctx.send(f"Игра остановлена by {ctx.author.mention}")
        except:
            return await ctx.send("Игра не запущена")

    @commands.command(pass_content=True, brief="Старт игры с ботом")
    @commands.guild_only()
    async def астрал_бот(self, ctx):
        if ctx.guild.id in self.games.keys():
            return await ctx.send("Игра уже запущена!")

        astral_table = getAstralTable(self.bot.databaseSession, ctx.guild.id)

        if astral_table[1] is None or astral_table[1] == "":
            await ctx.send("Астрал не инициализирован! Сообщите администрации сервера.")
            return

        view = AstralBotStart(ctx.author)

        message = await ctx.send("Старт Астрала. Сессия с ботом", view=view)
        await view.wait()

        try:
            view.response
        except:
            await message.edit("Старт отменён", view=None)
            return

        if not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            self.games[ctx.guild.id] = AstralGameSession(
                self.bot, ctx.channel, view.response, astral_table[0], astral_table[1]
            )
            self.games[ctx.guild.id].append_player(ctx.author)

            await message.edit(
                f'Стартуем игру с ботом. {"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                view=None,
            )

            await self.GameProcess(self.games[ctx.guild.id])

    @commands.command(pass_content=True, brief="Старт игры с боссом")
    @commands.guild_only()
    async def астрал_босс(self, ctx):
        if ctx.guild.id in self.games.keys():
            return await ctx.send("Игра уже запущена!")

        astral_table = getAstralTable(self.bot.databaseSession, ctx.guild.id)

        if astral_table[1] is None or astral_table[1] == "":
            await ctx.send("Астрал не инициализирован! Сообщите администрации сервера.")
            return

        view = AstralBossStart(ctx.author)

        message = await ctx.send("Старт Астрала. Сессия с боссом.", view=view)
        await view.wait()

        try:
            view.response
        except:
            await message.edit("Старт отменён", view=None)
            return

        if not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            self.games[ctx.guild.id] = AstralGameSession(
                self.bot, ctx.channel, view.response, astral_table[0], astral_table[1]
            )
            self.games[ctx.guild.id].append_player(ctx.author)

            await message.edit(
                f'Стартуем игру с боссом. {"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                view=None,
            )

            await self.GameProcess(self.games[ctx.guild.id])

    @commands.command(pass_content=True, brief="Старт игры")
    @commands.guild_only()
    async def астрал_старт(self, ctx):
        try:
            self.games[ctx.guild.id]
            await ctx.send("Игра уже запущена!")
            return
        except:
            pass

        astral_table = getAstralTable(self.bot.databaseSession, ctx.guild.id)

        if astral_table[1] is None or astral_table[1] == "":
            await ctx.send("Астрал не инициализирован! Сообщите администрации сервера.")
            return

        view = AstralPlayersStart(ctx.author)

        message = await ctx.send("Старт Астрала", view=view)
        await view.wait()

        try:
            view.response
        except:
            await message.edit("Старт отменён", view=None)
            return

        if not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            self.games[ctx.guild.id] = AstralGameSession(
                self.bot, ctx.channel, view.response, astral_table[0], astral_table[1]
            )
            self.games[ctx.guild.id].append_player(ctx.author)
            new_view = nextcord.ui.View()
            new_view.add_item(
                nextcord.ui.Button(
                    style=nextcord.ButtonStyle.gray, label="Подсоединиться"
                )
            )

            await message.edit(
                f'Ожидаем игроков {"1/2" if view.response["players"] == 2 else "1/4"}. {"Режим DM. " if view.response["dm"] else ""}{"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                view=new_view,
            )
            try:
                async with timeout(180):
                    while True:
                        interaction: nextcord.Interaction = await self.bot.wait_for(
                            "interaction", check=lambda m: m.user != ctx.author
                        )

                        self.games[ctx.guild.id].append_player(interaction.user)
                        if self.games[ctx.guild.id].ready_to_start():
                            await message.edit("Стартуем!", view=None)
                            break
                        else:
                            await message.edit(
                                f'Ожидаем игроков {len(self.games[ctx.guild.id].players)}/{self.games[ctx.guild.id].players_count} . {"Режим DM. " if view.response["dm"] else ""}{"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                                view=new_view,
                            )
            except asyncio.TimeoutError:
                await message.edit("Старт отменён", view=None)
                del self.games[game.channel.guild.id]
                return

            await self.GameProcess(self.games[ctx.guild.id])

    async def GameProcess(self, game):
        game.stop()
        game.start()
        # await asyncio.sleep(5)

        if not await game.putLinks(0):
            await game.channel.send("Возникли проблемы с подключением к Астралу!")
            return

        round = 0
        while True:

            info = await game.getGameMessage(0)

            try:
                if not info:
                    await game.channel.send("Игра прервана из-за ошибки Астрала!")
                    game.stop()
                    del self.games[channel.guild.id]
                    break
            except:
                pass

            info_s = info[0]
            mentions = ""
            if createImage(info[1]) == "Ok":
                file = nextcord.File("./cogs/astral/temp/art.png", filename="art.png")
            else:
                file = None

            for player in game.players:
                if player.member is not None:
                    mentions += f"{player.member.mention} "

            if info_s.find("Конец игры.") != -1:
                emb = nextcord.Embed(description=mentions)
                emb.color = nextcord.Colour.brand_red()
                emb.set_footer(text="Инструкция по игре в Астрал для новичков: https://clck.ru/YXKHB")
                emb.add_field(name=f"Раунд: {round}", value=info_s)

                if file is not None:
                    emb.set_image(url="attachment://art.png")
                    await game.channel.send(embed=emb, file=file)
                else:
                    await game.channel.send(embed=emb)

                game.stop()
                del self.games[game.channel.guild.id]
                break
            else:
                game.updateInfo()

                emb = nextcord.Embed(description=mentions)
                emb.color = nextcord.Colour.brand_green()
                emb.add_field(name=f"Раунд: {round}", value=info_s)
                emb.set_footer(text="Инструкция по игре в Астрал для новичков: https://clck.ru/YXKHB")
                view = GameMessage(game)

                if file is not None:
                    emb.set_image(url="attachment://art.png")
                    await game.channel.send(embed=emb, file=file, view=view)
                else:
                    await game.channel.send(embed=emb, view=view)

                await view.wait()
                response = view.response

                for response_element in response:
                    for i in range(len(game.players)):
                        if response_element["name"] == game.players[i].name:
                            game.players[i].move = response_element["spell"]
                            game.players[i].movedirection = response_element[
                                "direction"
                            ]

                game.move()
                round += 1


def setup(bot):
    bot.add_cog(Astral(bot))


def createImage(mas):
    if mas != []:
        r = 1
        massive = []
        for x in mas:
            ufr = requests.get(x)
            f = open(f"./cogs/astral/temp/{str(r)}.png", "wb")
            f.write(ufr.content)
            f.close()
            massive.append(f"./cogs/astral/temp/{str(r)}.png")
            r += 1

        try:
            images = [Image.open(x) for x in massive]
            widths, heights = zip(*(i.size for i in images))

            total_width = sum(widths)
            max_height = max(heights)

            new_im = Image.new("RGB", (total_width, max_height))

            x_offset = 0
            for im in images:
                new_im.paste(im, (x_offset, 0))
                x_offset += im.size[0]

            new_im.save("./cogs/astral/temp/art.png")
            return "Ok"
        except:
            return "Fail"
