import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
from uuid import uuid4
from async_timeout import timeout
from .api import *
from .ui import *
from typing import Any
from dataclasses import dataclass
import asyncio
import os
from modules.checkers import check_moderator_permission
import datetime

import requests
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


@dataclass
class GameTask:
    uuid: str
    guild: int
    channel: int
    task: Any


class Astral(commands.Cog, name="Астрал"):
    """Стратегическая игра Астрал."""

    COG_EMOJI: str = "🌰"

    def __init__(self, bot):
        self.bot = bot
        self.games: dict = {}

    @commands.command(
        brief="Список текущих игровых сессий Астрала с возможностью остановки"
    )
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def астрал_стоп(self, ctx: Context, game_uuid: str = ""):
        if game_uuid != "":
            if ctx.guild.id in self.games:
                if game_uuid in self.games[ctx.guild.id]:
                    self.games[ctx.guild.id][game_uuid].task.cancel()

                    await self.games[ctx.guild.id][game_uuid].task
                    return await ctx.send(f"Игра остановлена. ({ctx.author.mention})")
                else:
                    return await ctx.send("Не найдено игры с таким UUID")
            else:
                return await ctx.send("Не найдено игры с таким UUID")

        embed: nextcord.Embed = nextcord.Embed(
            title="Текущие игровые сессии Астрала на сервере",
            timestamp=datetime.datetime.now(),
            colour=nextcord.Colour.random(),
        )

        if ctx.guild.id not in self.games:
            self.games[ctx.guild.id] = {}

        for num, uuid in enumerate(self.games[ctx.guild.id]):
            embed.add_field(
                name=f"{num + 1}. {self.games[ctx.guild.id][uuid].uuid}",
                value=f"Канал: {ctx.guild.get_channel(self.games[ctx.guild.id][uuid].channel).name if ctx.guild.get_channel(self.games[ctx.guild.id][uuid].channel) is not None else self.games[ctx.guild.id][uuid].channel}",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(pass_content=True, brief="Старт игры с ботом")
    @commands.guild_only()
    async def астрал_бот(self, ctx):

        view = AstralBotStart(ctx.author)
        uuid = str(uuid4())

        embed: nextcord.Embed = nextcord.Embed(
            title="Старт Астрала с ботом",
            description=f"UUID игры: {uuid}",
            colour=nextcord.Colour.random(),
        )

        message = await ctx.send(embed=embed, view=view)
        await view.wait()

        if view.response is not None and not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            await message.edit("Подготовка таблицы!", view=None, embed=None)
            game_obj = await AstralGameSession.create(
                self.bot, ctx.channel, view.response, uuid
            )
            game_obj.append_player(ctx.author)

            await message.edit(
                f'Стартуем игру с ботом. {"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                view=None,
            )

            if ctx.guild.id not in self.games:
                self.games[ctx.guild.id] = {}

            self.games[ctx.guild.id][uuid] = GameTask(
                uuid=uuid,
                guild=ctx.guild.id,
                channel=ctx.channel.id,
                task=asyncio.create_task(self.game_process(game_obj, uuid)),
            )

    @commands.command(pass_content=True, brief="Старт игры с боссом")
    @commands.guild_only()
    async def астрал_босс(self, ctx):

        view = AstralBossStart(ctx.author)
        uuid = str(uuid4())

        embed: nextcord.Embed = nextcord.Embed(
            title="Старт Астрала с боссом",
            description=f"UUID игры: {uuid}",
            colour=nextcord.Colour.random(),
        )

        message = await ctx.send(embed=embed, view=view)
        await view.wait()

        if view.response is not None and not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            await message.edit("Подготовка таблицы!", view=None, embed=None)
            game_obj = await AstralGameSession.create(
                self.bot, ctx.channel, view.response, uuid
            )
            game_obj.append_player(ctx.author)

            await message.edit(
                f'Стартуем игру с боссом. {"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                view=None,
            )

            if ctx.guild.id not in self.games:
                self.games[ctx.guild.id] = {}

            self.games[ctx.guild.id][uuid] = GameTask(
                uuid=uuid,
                guild=ctx.guild.id,
                channel=ctx.channel.id,
                task=asyncio.create_task(self.game_process(game_obj, uuid)),
            )

    @commands.command(pass_content=True, brief="Старт игры")
    @commands.guild_only()
    async def астрал_старт(self, ctx):

        view = AstralPlayersStart(ctx.author)
        uuid = str(uuid4())

        embed: nextcord.Embed = nextcord.Embed(
            title="Старт Астрала",
            description=f"UUID игры: {uuid}",
            colour=nextcord.Colour.random(),
        )

        message = await ctx.send(embed=embed, view=view)
        await view.wait()

        if view.response is not None and not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            await message.edit("Подготовка таблицы!", view=None, embed=None)
            game_obj = await AstralGameSession.create(
                self.bot, ctx.channel, view.response, uuid
            )
            game_obj.append_player(ctx.author)
            new_view = nextcord.ui.View()
            new_view.add_item(
                nextcord.ui.Button(
                    style=nextcord.ButtonStyle.gray, label="Подсоединиться"
                )
            )

            await message.edit(
                f'Ожидаем игроков {"1/2" if view.response["players"] == 2 else "1/4"}. {"Режим DM. " if view.response["dm"] else ""}{"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                view=new_view,
                embed=None,
            )
            try:
                async with timeout(180):
                    while True:
                        interaction: nextcord.Interaction = await self.bot.wait_for(
                            "interaction", check=lambda m: m.user != ctx.author
                        )

                        game_obj.append_player(interaction.user)
                        if game_obj.ready_to_start():
                            await message.edit("Стартуем!", view=None)
                            break
                        else:
                            await message.edit(
                                f'Ожидаем игроков {len(game_obj.players)}/{game_obj.players_count} . {"Режим DM. " if view.response["dm"] else ""}{"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                                view=new_view,
                            )
            except asyncio.TimeoutError:
                await message.edit("Старт отменён", view=None)
                game_obj.spread_sheet.delete()
                return

            if ctx.guild.id not in self.games:
                self.games[ctx.guild.id] = {}

            self.games[ctx.guild.id][uuid] = GameTask(
                uuid=uuid,
                guild=ctx.guild.id,
                channel=ctx.channel.id,
                task=asyncio.create_task(self.game_process(game_obj, uuid)),
            )

    async def game_process(self, game: AstralGameSession, uuid: str):
        # os.mkdir(fr"{os.getcwd()}/cogs/astral/temp/{uuid.split('-')[0]}//")

        embed_color = nextcord.Colour.random()

        try:
            try:
                start_status = game.start()
                if "error" in start_status:
                    return await game.channel.send(
                        f"Произошла ошибка: {start_status['error']}"
                    )
            except TimeoutError:
                await asyncio.sleep(5)
                await game.channel.send(
                    "**ВНИМАНИЕ:** Соединение с Астралом не стабильно, корректная работа не гарантируется"
                )

            if not await game.put_links(0):
                await game.channel.send("Возникли проблемы с подключением к Астралу!")
                game.stop()
                return

            round = 0
            while True:
                info = await game.get_game_message()

                if not info and isinstance(info, bool):
                    await game.channel.send("Игра прервана из-за ошибки Астрала!")
                    return

                info_s = info[0]
                mentions = " ".join(
                    [
                        player.member.mention
                        for player in game.players
                        if player.member is not None
                    ]
                )

                emb = nextcord.Embed()
                emb.add_field(name=f"Раунд: {round}", value=info_s)
                emb.set_footer(
                    text=f"Инструкция по игре в Астрал для новичков: https://clck.ru/YXKHB\nUUID: {uuid}"
                )

                if info_s.find("Конец игры.") != -1:
                    emb.colour = nextcord.Colour.brand_red()

                    await game.channel.send(mentions, embed=emb)

                    try:
                        for art in info[1]:
                            await game.channel.send(art)
                    except:
                        pass

                    return
                else:
                    game.update_info()
                    emb.colour = embed_color
                    view = GameMessage(game)

                    message = await game.channel.send(mentions, embed=emb)

                    try:
                        for art in info[1]:
                            await game.channel.send(art)
                    except:
                        pass

                    await message.edit(view=view)
                    await view.wait()
                    response = view.response

                    for response_element in response:
                        for i in range(len(game.players)):
                            if response_element["name"] == game.players[i].name:
                                game.players[i].move = response_element["spell"]
                                game.players[i].move_direction = response_element[
                                    "direction"
                                ]

                    round_change_status = game.try_to_move()
                    if "error" not in round_change_status:
                        game.prepare_for_new_round()
                        round += 1
                    else:
                        error_counter = -1
                        game.round_replay()
                        while "error" in round_change_status and error_counter != 3:
                            error_counter += 1
                            await game.channel.send(
                                f"Произошла ошибка: {round_change_status['error']}\nПовтор раунда!"
                            )
                            view = GameMessage(game)

                            message = await game.channel.send(mentions, embed=emb)

                            try:
                                for art in info[1]:
                                    await game.channel.send(art)
                            except:
                                pass

                            await message.edit(view=view)
                            response = view.response

                            for response_element in response:
                                for i in range(len(game.players)):
                                    if response_element["name"] == game.players[i].name:
                                        game.players[i].move = response_element["spell"]
                                        game.players[
                                            i
                                        ].move_direction = response_element["direction"]

                            round_change_status = game.try_to_move()
                            if "error" not in round_change_status:
                                game.prepare_for_new_round()
                                round += 1
                                error_counter = 0
        except asyncio.CancelledError:
            await game.channel.send("Принудительная остановка игры!")
        finally:
            game.stop()
            game.spread_sheet.delete()
            del self.games[game.channel.guild.id][uuid]


def setup(bot):
    bot.add_cog(Astral(bot))
