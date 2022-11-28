import asyncio
import datetime
import traceback
from dataclasses import dataclass
from random import randint
from typing import Any, Optional, Union
from uuid import uuid4

import nextcord
from async_timeout import timeout
from base.base_cog import MilkCog
from nextcord.utils import format_dt

from .api import AstralGameSession
from .ui import GameMessage, GameStopperMessage


@dataclass
class GameTask:
    uuid: str
    guild: int
    channel: int
    task: Any
    members: list
    game_obj: Optional[AstralGameSession]


games = {}
players_alias = {}
arenas = {
    "0": "не выбрана",
    "1": "вулкан",
    "2": "джунгли",
    "3": "ледник",
    "4": "пустыня",
    "5": "арена магов",
    "6": "кладбище",
    "7": "атлантида",
    "8": "ад",
    "9": "пешера",
    "10": "новый год",
    "r": "случайная",
}


class Astral(MilkCog, name="Астрал"):
    """Стратегическая игра Астрал."""

    COG_EMOJI: str = "🌰"

    def __init__(self, bot):
        self.bot = bot

    @MilkCog.slash_command()
    async def astral(self, interaction):
        ...

    @MilkCog.slash_command(
        description="Список текущих игровых сессий Астрала с возможностью остановки",
        permission="moderator",
    )
    async def astral_stop(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        embed: nextcord.Embed = nextcord.Embed(
            title="Текущие игровые сессии Астрала на сервере",
            timestamp=datetime.datetime.now(),
            colour=nextcord.Colour.random(),
        )

        if interaction.guild.id not in games:
            games[interaction.guild.id] = {}

        for num, uuid in enumerate(games[interaction.guild.id]):
            game: GameTask = games[interaction.guild.id][uuid]
            game_players: str = " // VS // ".join(
                [
                    ", ".join([str(player) for player in team])
                    for team in game.game_obj.teams
                ]
            )
            game_round: int = game.game_obj.round
            game_channel: Union[str, nextcord.TextChannel] = (
                interaction.guild.get_channel(
                    games[interaction.guild.id][uuid].channel
                ).name
                if interaction.guild.get_channel(
                    games[interaction.guild.id][uuid].channel
                )
                is not None
                else games[interaction.guild.id][uuid].channel
            )

            embed.add_field(
                name=f"{num + 1}. {game_players}",
                value=f"**Раунд:** {game_round}\n"
                + f"**Канал:** {game_channel}\n"
                + f"**UUID:** {uuid}",
                inline=False,
            )

        view = GameStopperMessage(games, interaction.user)

        if embed.fields:
            message = await interaction.send(embed=embed, view=view)
            view.message = message
        else:
            await interaction.send("**На сервере не запущено ни одной игры**")

    @astral.subcommand(
        description="Старт игровой сессии с виртуальным противником",
    )
    async def bot(
        self,
        interaction: nextcord.Interaction,
        arena: str
        | None = nextcord.SlashOption(
            name="арена",
            description="арена для игры",
            choices={
                "Вне арены": "0",
                "Вулкан": "1",
                "Джунгли": "2",
                "Ледник": "3",
                "Пустыня": "4",
                "Арена Магов": "5",
                "Кладбище": "6",
                "Атлантида": "7",
                "Ад": "8",
                "Пешера": "9",
                "Новый год": "10",
                "Случайная": "r",
            },
            required=False,
        ),
    ):
        if arena is None:
            arena = "0"
        if arena == "r":
            arena = str(randint(1, 10))
        uuid = str(uuid4())
        embed = nextcord.Embed(
            title="Старт Астрала с ботом",
            description=f"Арена: {arenas.get(arena)}\n" + f"UUID игры: {uuid}",
            colour=nextcord.Colour.random(),
        )

        message = await interaction.send(embed=embed)
        game_obj = AstralGameSession(
            self.bot, interaction.channel, uuid, arena=arena, boss="AstralBot"
        )
        game_obj.status_message = message
        game_obj.append_player(interaction.user)

        if interaction.guild.id not in games:
            games[interaction.guild.id] = {}

        games[interaction.guild.id][uuid] = GameTask(
            uuid=uuid,
            guild=interaction.guild.id,
            channel=interaction.channel_id,
            task=asyncio.create_task(self.game_process(game_obj, uuid)),
            members=[],
            game_obj=None,
        )

        await games[interaction.guild.id][uuid].task

    @astral.subcommand(
        description="Старт игры с боссом",
    )
    async def boss(
        self,
        interaction: nextcord.Interaction,
        boss: str = nextcord.SlashOption(
            name="босс",
            description="имя босса",
            choices={
                "Тварь из бездны": "Тварь из бездны",
                "Первородный дракон": "Первородный дракон",
                "Кицунэ": "Кицунэ",
                "Кровавый пузырь": "Кровавый пузырь",
                "Читерный бот": "AstralBotLol",
            },
            required=True,
        ),
        boss_control: bool
        | None = nextcord.SlashOption(
            name="контроль",
            description="контроль босса осуществляет",
            choices={
                "игрок": True,
                "бот": False,
            },
            required=False,
        ),
        players: int
        | None = nextcord.SlashOption(
            name="игроки",
            description="количество игроков (если игрок не контроллирует босса, то минус 1)",
            choices={"2 игрока": 2, "4 игрока": 4, "6 игроков": 6},
            required=False,
        ),
        arena: str
        | None = nextcord.SlashOption(
            name="арена",
            description="арена для игры",
            choices={
                "Вне арены": "0",
                "Вулкан": "1",
                "Джунгли": "2",
                "Ледник": "3",
                "Пустыня": "4",
                "Арена Магов": "5",
                "Кладбище": "6",
                "Атлантида": "7",
                "Ад": "8",
                "Пешера": "9",
                "Новый год": "10",
                "Случайная": "r",
            },
            required=False,
        ),
    ):

        if boss_control is None:
            boss_control = False
        if players is None:
            players = 2
        if arena is None:
            arena = "0"
        if arena == "r":
            arena = str(randint(1, 10))
        uuid = str(uuid4())

        embed = nextcord.Embed(
            title="Старт Астрала с боссом",
            description=f"Количество игроков: {players if boss_control else players - 1}\n"
            + f"Босс: {boss}\n"
            + f"Контроль босса осуществляет: {'игрок' if boss_control else 'бот'}\n"
            + f"Арена: {arenas.get(arena)}\n"
            + f"UUID игры: {uuid}",
            colour=nextcord.Colour.random(),
        )

        message = await interaction.send(embed=embed)
        game_obj = AstralGameSession(
            self.bot,
            interaction.channel,
            uuid,
            dm=True,
            players=players,
            boss=boss,
            boss_control=boss_control,
            arena=arena,
        )
        game_obj.status_message = message
        game_obj.append_player(interaction.user)

        if players != 2 or game_obj.boss_control:
            new_view = nextcord.ui.View()
            new_view.add_item(
                nextcord.ui.Button(
                    style=nextcord.ButtonStyle.gray, label="Подсоединиться"
                )
            )
            await message.edit(
                content=f"Ожидаем игроков для игры с боссом {len(game_obj.players)}/{game_obj.players_count - 1 if not game_obj.boss_control else game_obj.players_count}",
                view=new_view,
                embed=None,
            )
            try:
                async with timeout(180):
                    while True:
                        inter: nextcord.Interaction = await self.bot.wait_for(
                            "interaction",
                            check=lambda m: m.user != interaction.user
                            and m.channel == interaction.channel,
                        )
                        await interaction.followup.send(
                            f"Игрок **{inter.user.display_name}** присоединился к игре!"
                        )
                        game_obj.append_player(inter.user)
                        if game_obj.ready_to_start():
                            await message.edit(content="Инициализация игры!", view=None)
                            break
                        else:
                            await message.edit(
                                content=f"Ожидаем игроков {len(game_obj.players)}/{game_obj.players_count - 1}",
                                view=new_view,
                            )
            except asyncio.TimeoutError:
                await message.edit(content="Старт отменён", view=None)
                return

        if interaction.guild.id not in games:
            games[interaction.guild.id] = {}

        games[interaction.guild.id][uuid] = GameTask(
            uuid=uuid,
            guild=interaction.guild.id,
            channel=interaction.channel_id,
            task=asyncio.create_task(self.game_process(game_obj, uuid)),
            members=[],
            game_obj=None,
        )

        await games[interaction.guild.id][uuid].task

    @astral.subcommand(
        description="Старт игровой сессии Астрала",
    )
    async def astral_start(
        self,
        interaction: nextcord.Interaction,
        players: int
        | None = nextcord.SlashOption(
            name="игроки",
            description="количество игроков",
            choices={"2 игрока": 2, "4 игрока": 4, "6 игроков": 6},
            required=False,
        ),
        dm: bool
        | None = nextcord.SlashOption(
            name="dm",
            description="death match (все игроки в разных командах)",
            choices={
                "включен": True,
                "улыбка": False,
            },
            required=False,
        ),
        arena: str
        | None = nextcord.SlashOption(
            name="арена",
            description="арена для игры",
            choices={
                "Вне арены": "0",
                "Вулкан": "1",
                "Джунгли": "2",
                "Ледник": "3",
                "Пустыня": "4",
                "Арена Магов": "5",
                "Кладбище": "6",
                "Атлантида": "7",
                "Ад": "8",
                "Пешера": "9",
                "Новый год": "10",
                "Случайная": "r",
            },
            required=False,
        ),
    ):

        if dm is None:
            dm = False

        if players is None:
            players = "2"

        if arena is None:
            arena = "0"
        if arena == "r":
            arena = str(randint(1, 10))
        uuid = str(uuid4())

        embed = nextcord.Embed(
            title="Старт Астрала",
            description=f"Количество игроков: {players}\n"
            + f"Deathmatch: {'включен' if dm else 'отключен'}\n"
            + f"Арена: {arenas.get(arena)}\n"
            + f"UUID игры: {uuid}",
            colour=nextcord.Colour.random(),
        )

        message = await interaction.send(embed=embed)

        game_obj = AstralGameSession(
            self.bot,
            interaction.channel,
            uuid,
            dm=dm,
            players=int(players),
            arena=arena,
        )
        game_obj.status_message = message
        game_obj.append_player(interaction.user)
        new_view = nextcord.ui.View()
        new_view.add_item(
            nextcord.ui.Button(style=nextcord.ButtonStyle.gray, label="Подсоединиться")
        )

        await message.edit(
            content=f"Ожидаем игроков {len(game_obj.players)}/{game_obj.players_count}",
            view=new_view,
            embed=None,
        )
        try:
            async with timeout(180):
                while True:
                    inter: nextcord.Interaction = await self.bot.wait_for(
                        "interaction",
                        check=lambda m: m.user != interaction.user
                        and m.channel == interaction.channel,
                    )
                    await interaction.followup.send(
                        f"Игрок **{inter.user.display_name}** присоединился к игре!"
                    )
                    game_obj.append_player(inter.user)
                    if game_obj.ready_to_start():
                        await message.edit(content="Инициализация игры!", view=None)
                        break
                    else:
                        await message.edit(
                            content=f"Ожидаем игроков {len(game_obj.players)}/{game_obj.players_count}",
                        )
        except asyncio.TimeoutError:
            await message.edit(content="Старт отменён", view=None)
            return

        if interaction.guild.id not in games:
            games[interaction.guild.id] = {}

        games[interaction.guild.id][uuid] = GameTask(
            uuid=uuid,
            guild=interaction.guild.id,
            channel=interaction.channel_id,
            task=asyncio.create_task(self.game_process(game_obj, uuid)),
            members=[],
            game_obj=None,
        )

        await games[interaction.guild.id][uuid].task

    async def game_process(self, game: AstralGameSession, uuid: str):
        embed_color = nextcord.Colour.random()

        for player in game.players:
            if player.member is not None:
                players_alias[player.member.id] = game.channel.guild

        time_mark = datetime.datetime.now()
        if not self.bot.dev:
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

        premove_time_mark = datetime.datetime.now()
        postmove_time_mark = datetime.datetime.now()

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
                            text=f"Инструкция по игре в Астрал для новичков: https://clck.ru/YXKHB\n"
                            + f"UUID: {uuid}\nВремя старта: {f'{datetime.datetime.now() - time_mark}'[:-7]}"
                        )
                    else:
                        emb.set_footer(
                            text=f"Обработка хода: {f'{datetime.datetime.now() - time_mark}'[:-7]}\n"
                            + f"Время хода: {f'{postmove_time_mark - premove_time_mark}'[:-7]}"
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
                                f"Произошла ошибка: {round_change_status}\nПовтор раунда!"
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
            if game.tables is not None:
                await game.tables.delete_temp_astral_table(game.spread_sheet_url)
            del games[game.channel.guild.id][uuid]


def setup(bot):
    bot.add_cog(Astral(bot))
