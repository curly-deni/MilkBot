import nextcord
import traceback
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord.utils import format_dt
from uuid import uuid4
from async_timeout import timeout
from typing import Any, Union
from dataclasses import dataclass
import asyncio
from modules.checkers import check_moderator_permission
import datetime
from .api import AstralGameSession
from .ui import (
    AstralBotStart,
    AstralBossStart,
    AstralPlayersStart,
    GameMessage,
    GameStopperMessage,
)


@dataclass
class GameTask:
    uuid: str
    guild: int
    channel: int
    task: Any
    members: list
    game_obj: AstralGameSession


games = {}
players_alias = {}


class Astral(commands.Cog, name="Астрал"):
    """Стратегическая игра Астрал."""

    COG_EMOJI: str = "🌰"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Список текущих игровых сессий Астрала с возможностью остановки"
    )
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def астрал_стоп(self, ctx: Context):

        embed: nextcord.Embed = nextcord.Embed(
            title="Текущие игровые сессии Астрала на сервере",
            timestamp=datetime.datetime.now(),
            colour=nextcord.Colour.random(),
        )

        if ctx.guild.id not in games:
            games[ctx.guild.id] = {}

        for num, uuid in enumerate(games[ctx.guild.id]):
            game: GameTask = games[ctx.guild.id][uuid]
            game_players: str = " // VS // ".join(
                [
                    ", ".join([str(player) for player in team])
                    for team in game.game_obj.teams
                ]
            )
            game_round: int = game.game_obj.round
            game_channel: Union[str, nextcord.TextChannel] = (
                ctx.guild.get_channel(games[ctx.guild.id][uuid].channel).name
                if ctx.guild.get_channel(games[ctx.guild.id][uuid].channel) is not None
                else games[ctx.guild.id][uuid].channel
            )

            embed.add_field(
                name=f"{num + 1}. {game_players}",
                value=f"**Раунд:** {game_round}\n"
                + f"**Канал:** {game_channel}\n"
                + f"**UUID:** {uuid}",
                inline=False,
            )

        view = GameStopperMessage(games, ctx.author)

        if embed.fields:
            message = await ctx.send(embed=embed, view=view)
            view.message = message
        else:
            await ctx.send("**На сервере не запущено ни одной игры**")

    @commands.command(brief="Старт игры с ботом")
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

        if view.response is None or not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            game_obj = AstralGameSession(self.bot, ctx.channel, view.response, uuid)
            game_obj.status_message = message
            game_obj.append_player(ctx.author)

            await message.edit(
                f'Инициализация игры с ботом. {"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                view=None,
            )

            if ctx.guild.id not in games:
                games[ctx.guild.id] = {}

            games[ctx.guild.id][uuid] = GameTask(
                uuid=uuid,
                guild=ctx.guild.id,
                channel=ctx.channel.id,
                task=asyncio.create_task(self.game_process(game_obj, uuid)),
                members=[],
                game_obj=None,
            )

            await games[ctx.guild.id][uuid].task

    @commands.command(brief="Старт игры с боссом")
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
        view.message = message
        await view.wait()

        if view.response is None or not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            game_obj = AstralGameSession(self.bot, ctx.channel, view.response, uuid)
            game_obj.status_message = message
            game_obj.append_player(ctx.author)

            if view.response["players"] != 2 or game_obj.boss_control:
                new_view = nextcord.ui.View()
                new_view.add_item(
                    nextcord.ui.Button(
                        style=nextcord.ButtonStyle.gray, label="Подсоединиться"
                    )
                )
                await message.edit(
                    f'Ожидаем игроков для игры с боссом {len(game_obj.players)}/{game_obj.players_count-1 if not game_obj.boss_control else game_obj.players_count}. {"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                    view=new_view,
                    embed=None,
                )
                try:
                    async with timeout(180):
                        while True:
                            interaction: nextcord.Interaction = await self.bot.wait_for(
                                "interaction", check=lambda m: m.user != ctx.author
                            )
                            await ctx.send(
                                f"Игрок **{interaction.user.display_name}** присоединился к игре!"
                            )
                            game_obj.append_player(interaction.user)
                            if game_obj.ready_to_start():
                                await message.edit("Инициализация игры!", view=None)
                                break
                            else:
                                await message.edit(
                                    f'Ожидаем игроков {len(game_obj.players)}/{game_obj.players_count-1} . {"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                                    view=new_view,
                                )
                except asyncio.TimeoutError:
                    await message.edit("Старт отменён", view=None)
                    return

            else:
                await message.edit(
                    f'Инициализация игры с боссом. {"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                    view=None,
                )

            if ctx.guild.id not in games:
                games[ctx.guild.id] = {}

            games[ctx.guild.id][uuid] = GameTask(
                uuid=uuid,
                guild=ctx.guild.id,
                channel=ctx.channel.id,
                task=asyncio.create_task(self.game_process(game_obj, uuid)),
                members=[],
                game_obj=None,
            )

            await games[ctx.guild.id][uuid].task

    @commands.command(brief="Старт игры")
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

        if view.response is None or not view.response["status"]:
            await message.edit("Старт отменён", view=None)
            return
        else:
            game_obj = AstralGameSession(self.bot, ctx.channel, view.response, uuid)
            game_obj.status_message = message
            game_obj.append_player(ctx.author)
            new_view = nextcord.ui.View()
            new_view.add_item(
                nextcord.ui.Button(
                    style=nextcord.ButtonStyle.gray, label="Подсоединиться"
                )
            )

            await message.edit(
                f'Ожидаем игроков {"1/2" if view.response["players"] == 2 else "1/4"}. {"Режим DM. " if view.response["dm"] == "TRUE" else ""}{"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                view=new_view,
                embed=None,
            )
            try:
                async with timeout(180):
                    while True:
                        interaction: nextcord.Interaction = await self.bot.wait_for(
                            "interaction", check=lambda m: m.user != ctx.author
                        )
                        await ctx.send(
                            f"Игрок **{interaction.user.display_name}** присоединился к игре!"
                        )
                        game_obj.append_player(interaction.user)
                        if game_obj.ready_to_start():
                            await message.edit("Инициализация игры!", view=None)
                            break
                        else:
                            await message.edit(
                                f'Ожидаем игроков {len(game_obj.players)}/{game_obj.players_count} . {"Режим DM. " if view.response["dm"] else ""}{"Сражение пройдёт на арене." if view.response["arena"] != "0" else ""}',
                                view=new_view,
                            )
            except asyncio.TimeoutError:
                await message.edit("Старт отменён", view=None)

                return

            if ctx.guild.id not in games:
                games[ctx.guild.id] = {}

            games[ctx.guild.id][uuid] = GameTask(
                uuid=uuid,
                guild=ctx.guild.id,
                channel=ctx.channel.id,
                task=asyncio.create_task(self.game_process(game_obj, uuid)),
                members=[],
                game_obj=None,
            )

            await games[ctx.guild.id][uuid].task

    async def game_process(self, game: AstralGameSession, uuid: str):
        embed_color = nextcord.Colour.random()

        for player in game.players:
            if player.member is not None:
                players_alias[player.member.id] = game.channel.guild

        time_mark = datetime.datetime.now()
        if not self.bot.debug:
            await game.init_tables()
            time_status = datetime.datetime.now() + datetime.timedelta(
                minutes=1, seconds=10
            )
            time_finish = datetime.datetime.now() + datetime.timedelta(
                minutes=2, seconds=30
            )
            await game.status_message.edit(
                content=f"""> **__Запуск игровой сессии__**

**Текущий статус:** *создание выделенной игровой таблицы*
**Приблизительное время окончания текущего процесса:** {format_dt(time_status, "T")}
**Приблизительное время старта:** {format_dt(time_finish, "T")}""",
                view=None,
                embed=None,
            )
        else:
            time_finish = datetime.datetime.now() + datetime.timedelta(
                minutes=1, seconds=10
            )
        try:
            start_status = await game.start(time_finish)
            self.bot.logger.debug(start_status)
            if "error" in start_status:
                return await game.channel.send(f"Произошла ошибка: {start_status}")
        except TimeoutError:
            await asyncio.sleep(5)
            await game.channel.send(
                "**ВНИМАНИЕ:** Соединение с Астралом не стабильно, корректная работа не гарантируется"
            )

        games[game.channel.guild.id][uuid].members = game.players_ids
        games[game.channel.guild.id][uuid].game_obj = game

        if not await game.put_links(0):
            await game.channel.send("Возникли проблемы с подключением к Астралу!")
            await game.stop()
            return

        try:
            while True:
                info = await game.get_game_message()
                await game.channel.trigger_typing()

                if not info and isinstance(info, bool):
                    await game.channel.send("Игра прервана из-за ошибки Астрала!")
                    break

                info_s = info[0]
                mentions = " ".join(
                    [
                        player.member.mention
                        for player in game.players
                        if player.member is not None
                    ]
                )

                emb = nextcord.Embed()
                emb.add_field(name=f"Раунд: {game.round}", value=info_s)
                try:
                    if game.round == 0:
                        emb.set_footer(
                            text=f"Инструкция по игре в Астрал для новичков: https://clck.ru/YXKHB\nUUID: {uuid}\nВремя старта: {f'{datetime.datetime.now() - time_mark}'[:-7]}"
                        )
                    else:
                        emb.set_footer(
                            text=f"Обработка хода: {f'{datetime.datetime.now() - time_mark}'[:-7]}\nВремя хода: {f'{postmove_time_mark - premove_time_mark}'[:-7]}"
                        )
                except:
                    pass

                if info_s.find("Конец игры.") != -1:
                    emb.colour = nextcord.Colour.brand_red()

                    try:
                        for art in info[1]:
                            await game.channel.send(art)
                    except:
                        pass
                    await game.channel.send(mentions, embed=emb)
                    return
                else:
                    await game.update_info()
                    emb.colour = embed_color

                    try:
                        for art in info[1]:
                            await game.channel.send(art)
                    except:
                        pass

                    message = await game.channel.send(mentions, embed=emb)

                    players_with_ability: list[int] = [
                        player.member.id
                        for player in game.players
                        if player.member is not None
                        and player.ability
                        and not player.moved
                    ]
                    premove_time_mark = datetime.datetime.now()
                    if players_with_ability:
                        game.view = GameMessage(game)
                        game.view.message = message
                        await message.edit(view=game.view)
                        await game.view.wait()
                        postmove_time_mark = datetime.datetime.now()
                        response = game.view.response

                        for response_element in response:
                            for i in range(len(game.players)):
                                if game.players[i].member is not None:
                                    if (
                                        response_element["id"]
                                        == game.players[i].member.id
                                    ):
                                        game.players[i].move = response_element["spell"]
                                        game.players[
                                            i
                                        ].move_direction = response_element["direction"]

                    time_mark = datetime.datetime.now()
                    round_change_status = await game.try_to_move()
                    if "error" not in round_change_status:
                        game.prepare_for_new_round()
                        game.view = None
                        game.round += 1
                    else:
                        error_counter = -1
                        game.round_replay()
                        while "error" in round_change_status and error_counter != 3:
                            error_counter += 1
                            await game.channel.send(
                                f"Произошла ошибка: {round_change_status['error']}\nПовтор раунда!"
                            )

                            try:
                                for art in info[1]:
                                    await game.channel.send(art)
                            except:
                                pass

                            message = await game.channel.send(mentions, embed=emb)

                            players_with_ability: list[int] = [
                                player.member.id
                                for player in game.players
                                if player.member is not None
                                and player.ability
                                and not player.moved
                            ]
                            premove_time_mark = datetime.datetime.now()
                            if players_with_ability:
                                game.view = GameMessage(game)
                                game.view.message = message
                                await message.edit(view=game.view)
                                await game.view.wait()
                                postmove_time_mark = datetime.datetime.now()
                                response = game.view.response

                                for response_element in response:
                                    for i in range(len(game.players)):
                                        if game.players[i].member is not None:
                                            if (
                                                response_element["id"]
                                                == game.players[i].member.id
                                            ):
                                                game.players[i].move = response_element[
                                                    "spell"
                                                ]
                                                game.players[
                                                    i
                                                ].move_direction = response_element[
                                                    "direction"
                                                ]

                            time_mark = datetime.datetime.now()
                            round_change_status = await game.try_to_move()
                            if "error" not in round_change_status:
                                game.prepare_for_new_round()
                                game.view = None
                                game.round += 1
                                error_counter = 0
        except asyncio.CancelledError:
            await game.channel.send("Принудительная остановка игры!")
        except Exception as error:
            exception_str = "\n".join(traceback.format_exception(error))
            self.bot.logger.error(exception_str + "\n")
            try:
                owner: nextcord.User = await self.bot.fetch_user(
                    self.bot.settings.get("owner_id", None)
                )
                await owner.send("Astral Game Error: " + exception_str)
                self.bot.logger.debug(
                    f"Traceback have been sended to user. ID: {owner.id}"
                )
            except:
                self.bot.logger.debug(
                    f"Error was ocured when sending traceback to user. ID: {self.bot.settings.get('owner_id', None)}"
                )
            await game.channel.send(
                f"Произошла критическая ошибка: {exception_str}\nИгра остановлена!"
            )
        finally:
            for player in game.players:
                if player.member is not None:
                    try:
                        del players_alias[player.member.id]
                    except:
                        pass

            await game.stop()
            del games[game.channel.guild.id][uuid]


def setup(bot):
    bot.add_cog(Astral(bot))
