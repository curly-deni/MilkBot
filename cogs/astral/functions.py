import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
from uuid import uuid4
from async_timeout import timeout
from typing import Any, Optional
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
    get_spell_from_modal,
    get_direction_from_view,
)


@dataclass
class GameTask:
    uuid: str
    guild: int
    channel: int
    task: Any
    members: list
    game_obj: Any


games = {}


class Astral(commands.Cog, name="Астрал"):
    """Стратегическая игра Астрал."""

    COG_EMOJI: str = "🌰"

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=[], force_global=True, description="Сделать ход")
    async def move(self, interaction: nextcord.Interaction):
        if interaction.guild is None or interaction.guild.id not in games:
            return await interaction.response.send_message("Вы не находитесь в игре!")

        for uuid in games[interaction.guild.id]:
            if interaction.user.id in games[interaction.guild.id][uuid].members:
                game = games[interaction.guild.id][uuid].game_obj
                if interaction.user.id not in game.view.players_with_ability:
                    try:
                        await interaction.send(
                            "На вас наложен эффект, ограничивающий способности заклинателя.",
                            ephemeral=True,
                        )
                        return True
                    except:
                        return True

                spell: Optional[str] = await get_spell_from_modal(
                    interaction,
                    game.players[game.players_ids.index(interaction.user.id)],
                    "Введите номер заклинания",
                )

                if spell is not None:
                    if spell in game.game_spells:
                        if (
                            spell in ["119", "140", "168", "242", "245"]
                            or len(game.players) == 4
                        ):
                            direction = await get_direction_from_view(interaction, game)
                        else:
                            direction = None

                        game.view.response.append(
                            {
                                "name": game.players[
                                    game.players_ids.index(interaction.user.id)
                                ].name,
                                "spell": spell,
                                "direction": direction,
                            }
                        )

                        game.view.players_moved += 1

                        if (
                            game.players[
                                game.players_ids.index(interaction.user.id)
                            ].effects.find("стан")
                            == -1
                            and game.players[
                                game.players_ids.index(interaction.user.id)
                            ].effects.find("сон")
                            == -1
                        ):

                            try:
                                await interaction.send(
                                    f"Ход был сделан игроком **{interaction.user.display_name}**!"
                                )
                            except:
                                try:
                                    await game.channel.send(
                                        f"Ход был сделан игроком **{interaction.user.display_name}**!"
                                    )
                                except:
                                    pass

                        if (
                            game.view.players_moved
                            == game.view.players_with_ability_count
                        ):
                            await game.view.on_timeout()
                            game.view.stop()
                    else:
                        try:
                            await interaction.send(spell, ephemeral=True)
                        except:
                            try:
                                await game.channel.send(spell)
                            except:
                                pass
                else:
                    return True

        try:
            return await interaction.response.send_message("Вы не находитесь в игре!")
        except nextcord.InteractionResponded:
            pass

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Получить ссылку на таблицу"
    )
    async def table(self, interaction: nextcord.Interaction):
        if interaction.guild is None or interaction.guild.id not in games:
            return await interaction.response.send_message("Вы не находитесь в игре!")

        for uuid in games[interaction.guild.id]:
            if interaction.user.id in games[interaction.guild.id][uuid].members:
                game = games[interaction.guild.id][uuid].game_obj
                try:
                    await interaction.send(
                        game.players[game.players_ids.index(interaction.user.id)].link,
                        ephemeral=True,
                    )
                    return True
                except:
                    return True

        try:
            return await interaction.response.send_message("Вы не находитесь в игре!")
        except nextcord.InteractionResponded:
            pass

    @commands.command(
        brief="Список текущих игровых сессий Астрала с возможностью остановки"
    )
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def астрал_стоп(self, ctx: Context, game_uuid: str = ""):
        if game_uuid != "":
            if ctx.guild.id in games:
                if game_uuid in games[ctx.guild.id]:
                    games[ctx.guild.id][game_uuid].task.cancel()

                    await games[ctx.guild.id][game_uuid].task
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

        if ctx.guild.id not in games:
            games[ctx.guild.id] = {}

        for num, uuid in enumerate(games[ctx.guild.id]):
            embed.add_field(
                name=f"{num + 1}. {games[ctx.guild.id][uuid].uuid}",
                value=f"Канал: {ctx.guild.get_channel(games[ctx.guild.id][uuid].channel).name if ctx.guild.get_channel(games[ctx.guild.id][uuid].channel) is not None else games[ctx.guild.id][uuid].channel}",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(brief="Старт игры с ботом")
    @commands.guild_only()
    async def астрал_бот(self, ctx):

        astral_access: dict = self.bot.database.get_astral(ctx.guild.id)

        if astral_access["table"] == "" or astral_access["script"] == "":
            return await ctx.send("Астрал не настроен для данного сервера!")

        if ctx.guild.id in games:
            if games[ctx.guild.id]:
                return await ctx.send("Игра уже запущена для данного сервера!")

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

    @commands.command(brief="Старт игры с боссом")
    @commands.guild_only()
    async def астрал_босс(self, ctx):

        astral_access: dict = self.bot.database.get_astral(ctx.guild.id)

        if astral_access["table"] == "" or astral_access["script"] == "":
            return await ctx.send("Астрал не настроен для данного сервера!")

        if ctx.guild.id in games:
            if games[ctx.guild.id]:
                return await ctx.send("Игра уже запущена для данного сервера!")

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
            game_obj = AstralGameSession(self.bot, ctx.channel, view.response, uuid)
            game_obj.status_message = message
            game_obj.append_player(ctx.author)

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

    @commands.command(brief="Старт игры")
    @commands.guild_only()
    async def астрал_старт(self, ctx):

        astral_access: dict = self.bot.database.get_astral(ctx.guild.id)

        if astral_access["table"] == "" or astral_access["script"] == "":
            return await ctx.send("Астрал не настроен для данного сервера!")

        if ctx.guild.id in games:
            if games[ctx.guild.id]:
                return await ctx.send("Игра уже запущена для данного сервера!")

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

    async def game_process(self, game: AstralGameSession, uuid: str):
        embed_color = nextcord.Colour.random()

        try:
            time_mark = datetime.datetime.now()
            try:
                start_status = await game.start()
                if "error" in start_status:
                    return await game.channel.send(
                        f"Произошла ошибка: {start_status['error']}"
                    )
            except TimeoutError:
                await asyncio.sleep(5)
                await game.channel.send(
                    "**ВНИМАНИЕ:** Соединение с Астралом не стабильно, корректная работа не гарантируется"
                )

            games[game.channel.guild.id][uuid].members = game.players_ids
            games[game.channel.guild.id][uuid].game_obj = game

            if not await game.put_links(0):
                await game.channel.send("Возникли проблемы с подключением к Астралу!")
                game.stop()
                return

            round = 0
            while True:
                info = await game.get_game_message()
                await game.channel.trigger_typing()

                if not info and isinstance(info, bool):
                    await game.channel.send("Игра прервана из-за ошибки Астрала!")
                    return

                info_s = info[0]
                mentions = (
                    " ".join(
                        [
                            player.member.mention
                            for player in game.players
                            if player.member is not None
                        ]
                    )
                    + "\n**Если дискорд выдаёт 'ошибку взаимодейтсвия', воспользуйтесь командами /move и /table - они доступны всегда. Не ждите, а используйте, не зря же я потратил 3 часа времени на переписывание механизма ходов**"
                )

                emb = nextcord.Embed()
                emb.add_field(name=f"Раунд: {round}", value=info_s)
                if round == 0:
                    emb.set_footer(
                        text=f"Инструкция по игре в Астрал для новичков: https://clck.ru/YXKHB\nUUID: {uuid}\nВремя старта: {f'{datetime.datetime.now() - time_mark}'[:-7]}"
                    )
                else:
                    emb.set_footer(
                        text=f"Обработка хода: {f'{datetime.datetime.now() - time_mark}'[:-7]}\nВремя хода: {f'{postmove_time_mark - premove_time_mark}'[:-7]}"
                    )

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
                    game.update_info()
                    emb.colour = embed_color
                    game.view = GameMessage(game)

                    try:
                        for art in info[1]:
                            await game.channel.send(art)
                    except:
                        pass

                    message = await game.channel.send(mentions, embed=emb)
                    game.view.message = message

                    premove_time_mark = datetime.datetime.now()
                    await message.edit(view=game.view)
                    await game.view.wait()
                    postmove_time_mark = datetime.datetime.now()
                    response = game.view.response

                    for response_element in response:
                        for i in range(len(game.players)):
                            if response_element["name"] == game.players[i].name:
                                game.players[i].move = response_element["spell"]
                                game.players[i].move_direction = response_element[
                                    "direction"
                                ]

                    time_mark = datetime.datetime.now()
                    round_change_status = game.try_to_move()
                    if "error" not in round_change_status:
                        game.prepare_for_new_round()
                        game.view = None
                        round += 1
                    else:
                        error_counter = -1
                        game.round_replay()
                        while "error" in round_change_status and error_counter != 3:
                            error_counter += 1
                            await game.channel.send(
                                f"Произошла ошибка: {round_change_status['error']}\nПовтор раунда!"
                            )
                            game.view = GameMessage(game)

                            message = await game.channel.send(mentions, embed=emb)
                            game.view.message = message

                            try:
                                for art in info[1]:
                                    await game.channel.send(art)
                            except:
                                pass

                            await message.edit(view=game.view)
                            await game.view.wait()
                            response = game.view.response

                            for response_element in response:
                                for i in range(len(game.players)):
                                    if response_element["name"] == game.players[i].name:
                                        game.players[i].move = response_element["spell"]
                                        game.players[
                                            i
                                        ].move_direction = response_element["direction"]

                            time_mark = datetime.datetime.now()
                            round_change_status = game.try_to_move()
                            if "error" not in round_change_status:
                                game.prepare_for_new_round()
                                game.view = None
                                round += 1
                                error_counter = 0
        except asyncio.CancelledError:
            await game.channel.send("Принудительная остановка игры!")
        finally:
            game.stop()
            del games[game.channel.guild.id][uuid]


def setup(bot):
    bot.add_cog(Astral(bot))
