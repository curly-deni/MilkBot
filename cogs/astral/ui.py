from math import floor
from typing import Optional, Union

import nextcord
from modules.ui import FieldModal

from .api import AstralGamePlayer, AstralGameSession


def spell_check(player: AstralGamePlayer, spell: str):
    if spell in player.spells:
        if (
            player.effects.find("фанатизм") != -1
            or player.effects.find("воля титана") != -1
            or player.effects.find("сфера пустоты") != -1
        ):
            return spell
        elif (
            player.effects.find("фанатизм") != -1
            or player.effects.find("воля титана") != -1
            or player.effects.find("сфера пустоты") != -1
        ):
            return spell
        elif player.effects.find("корни") != -1:
            if (
                int(player.mp) >= int(player.game.game_spells[spell]["mp"]) + 2
                or player.game.game_spells[spell]["mp"] == 0
            ):
                return spell
            else:
                return "Введите заклинание, на которое у вас хватает маны!"
        elif player.effects.find("контроль энергии") != -1:
            if int(player.mp) >= floor(float(player.game.game_spells[spell]["mp"]) / 2):
                return spell
            else:
                return "Введите заклинание, на которое у вас хватает маны!"
        elif (
            int(player.mp) >= int(player.game.game_spells[spell]["mp"])
            or player.game.game_spells[spell]["mp"] == 0
        ):
            return spell
        else:
            return "Введите заклинание, на которое у вас хватает маны!"
    else:
        return "Введите заклинание из таблицы!"


class GameStopperMessage(nextcord.ui.View):
    def __init__(self, games, author: nextcord.Member):
        super().__init__(timeout=180.0)

        self.author: nextcord.Member = author
        self.games = games[self.author.guild.id]
        self.message: Optional[nextcord.Message] = None

        self.stop_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Остановить"
        )
        self.cancel_button: nextcord.ui.Button = nextcord.ui.Button(label="Отмена")

        options: list[nextcord.SelectOption] = []
        for uuid in self.games:
            game = self.games[uuid]
            game_players: str = " // VS // ".join(
                [
                    ", ".join([str(player) for player in team])
                    for team in game.game_obj.teams
                ]
            )
            game_round: int = game.game_obj.round
            options.append(
                nextcord.SelectOption(
                    label=f"{game_players} | Раунд: {game_round}", value=uuid
                )
            )

        self.selector: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Игровые сессии", options=options
        )

        if not options:
            self.stop()
        else:
            self.add_item(self.selector)
            self.add_item(self.stop_button)
            self.add_item(self.cancel_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.send("Недопустимое действие!", ephemeral=True)
            return True

        match interaction.data["custom_id"]:
            case self.cancel_button.custom_id:
                await self.on_timeout()
                self.stop()
            case self.stop_button.custom_id:
                if not self.selector.values:
                    return await interaction.send(
                        "Вы не выбрали игровую сессию для остановки.", ephemeral=True
                    )

                if self.selector.values[0] in self.games:
                    self.games[self.selector.values[0]].task.cancel()
                    await interaction.send(
                        "Выполняется попытка остановки игры!", ephemeral=True
                    )
                    await self.games[self.selector.values[0]].task
                    return await interaction.followup.send(
                        f"Игра остановлена! {interaction.user.display_name}",
                        ephemeral=True,
                    )
            case self.selector.custom_id:
                return True
        return True

    async def on_timeout(self) -> None:
        if isinstance(self.message, nextcord.Message):
            self.selector.disabled = True
            self.stop_button.disabled = True
            self.cancel_button.disabled = True
            try:
                await self.message.edit(view=self)
            except:
                pass


class GameMessage(nextcord.ui.View):
    def __init__(self, game: AstralGameSession):
        super().__init__(timeout=180.0)

        self.game: AstralGameSession = game

        self.message: Optional[nextcord.Message] = None

        self.table_button: nextcord.ui.Button = nextcord.ui.Button(label="Таблица")
        self.move_button: nextcord.ui.Button = nextcord.ui.Button(label="Сделать ход")

        self.response: list[dict] = []
        self.players_moved: int = 0

        self.players_with_ability: list[int] = [
            player.member.id
            for player in game.players
            if player.member is not None and player.ability and not player.moved
        ]

        self.players_with_ability_count: int = len(self.players_with_ability)

        self.players_need_direction: list = []
        self.players_moved_id: list = []
        self.players_temp_move: dict = {}

        self.add_item(self.table_button)
        self.add_item(self.move_button)

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if interaction.user.id not in self.game.players_ids:
            await interaction.send("Вы не находитесь в игре", ephemeral=True)
            return True

        if interaction.data["custom_id"] == self.table_button.custom_id:
            try:
                await interaction.send(
                    self.game.players[
                        self.game.players_ids.index(interaction.user.id)
                    ].link,
                    ephemeral=True,
                )
                return True
            except:
                return True

        if interaction.user.id not in self.players_with_ability:
            try:
                await interaction.send(
                    "На вас наложен эффект, ограничивающий способности заклинателя.",
                    ephemeral=True,
                )
                return True
            except:
                return True

        if interaction.user.id in self.players_moved_id:
            try:
                await interaction.send(
                    "Вы уже сделали ход!",
                    ephemeral=True,
                )
                return True
            except:
                return True

        spell: Optional[str] = await get_spell_from_modal(
            interaction,
            self.game.players[self.game.players_ids.index(interaction.user.id)],
            "Введите номер заклинания",
        )

        player = self.game.players[self.game.players_ids.index(interaction.user.id)]

        if spell is not None:
            if spell in self.game.game_spells:
                if self.game.game_spells[spell]["target"] == "направленное":
                    direction = await get_direction_from_view(interaction, self.game)
                elif self.game.game_spells[spell]["target"] not in [
                    "селф баф",
                    "массовое, все",
                    "массовое, враги",
                    "массовое, союзники",
                ]:
                    players = []
                    if self.game.game_spells[spell]["target"] == "направленное, враг":
                        for team in self.game.teams:
                            if player not in team:
                                players.extend(team)

                    else:
                        for team in self.game.teams:
                            if player in team:
                                players.extend(team)

                    if len(players) == 1:
                        direction = players[0].name
                    else:
                        direction = await get_direction_from_view(
                            interaction, self.game, players
                        )
                else:
                    direction = None

                self.response.append(
                    {
                        "id": interaction.user.id,
                        "spell": spell,
                        "direction": direction,
                    }
                )
                self.players_moved_id.append(interaction.user.id)

                self.players_moved += 1

                if (
                    player.effects.find("стан") == -1
                    and player.effects.find("сон") == -1
                ):

                    try:
                        await interaction.send(
                            f"Ход был сделан игроком **{interaction.user.display_name}{f' ({player.name})' if player.name != interaction.user.display_name else ''}**!"
                        )
                    except:
                        try:
                            await self.game.channel.send(
                                f"Ход был сделан игроком **{interaction.user.display_name}{f' ({player.name})' if player.name != interaction.user.display_name else ''}**!"
                            )
                        except:
                            pass

                if self.players_moved == self.players_with_ability_count:
                    await self.on_timeout()
                    self.stop()
            else:
                try:
                    await interaction.send(spell, ephemeral=True)
                except:
                    try:
                        await self.game.channel.send(spell)
                    except:
                        pass
        else:
            return True

    async def on_timeout(self) -> None:
        if isinstance(self.message, nextcord.Message):
            self.table_button.disabled = True
            self.move_button.disabled = True
            try:
                await self.message.edit(view=self)
            except:
                pass


async def get_spell_from_modal(
    interaction: nextcord.Interaction, player: AstralGamePlayer, label: str
) -> Optional[str]:
    modal = FieldModal(title="Астрал", label=label, placeholder="Заклинание")

    try:
        await interaction.response.send_modal(modal)
    except Exception as ex:
        try:
            await interaction.send(
                f"Дискорд выебывается, заебал!\n{ex}", ephemeral=True
            )
        except:
            return f"Дискорд выебывается, заебал!\n{ex}"

    await modal.wait()
    try:
        spell = modal.value().lower()
    except:
        return

    return spell_check(player, spell)


async def get_direction_from_view(
    interaction: nextcord.Interaction,
    game: AstralGameSession,
    players: Optional[list] = None,
) -> Optional[str]:
    view = NewDirectionMessage(game, players)

    try:
        message = await interaction.send(view=view, ephemeral=True)
    except:
        message = await interaction.followup.send(view=view, ephemeral=True)
    view.message = message
    await view.wait()

    if view.value is not None:
        return view.value
    else:
        return await get_direction_from_view(interaction, game)


class NewDirectionMessage(nextcord.ui.View):
    def __init__(self, game: AstralGameSession, players: Optional[list]):
        super().__init__(timeout=180.0)

        self.game: AstralGameSession = game
        self.value: Optional[str] = None

        self.message: Optional[
            Union[nextcord.PartialInteractionMessage, nextcord.WebhookMessage]
        ] = None

        self.direction_buttons: dict = {}
        if players is None:
            for player in self.game.players:
                self.direction_buttons[player.name] = nextcord.ui.Button(
                    label=player.name
                )
                self.add_item(self.direction_buttons[player.name])
        else:
            for player in players:
                if isinstance(player, str):
                    p_name = player
                else:
                    p_name = player.name
                self.direction_buttons[p_name] = nextcord.ui.Button(label=p_name)
                self.add_item(self.direction_buttons[player.name])

    async def interaction_check(self, interaction: nextcord.Interaction):
        for player_name in self.direction_buttons:
            if (
                self.direction_buttons[player_name].custom_id
                == interaction.data["custom_id"]
            ):
                self.value = player_name
                await self.on_timeout()
                self.stop()
                return True

    async def on_timeout(self) -> None:
        if isinstance(self.message, nextcord.PartialInteractionMessage) or isinstance(
            self.message, nextcord.WebhookMessage
        ):
            for button in self.direction_buttons:
                self.direction_buttons[button].disabled = True
            try:
                await self.message.edit(view=self)
            except:
                pass


class DirectionMessage(nextcord.ui.View):
    def __init__(self, game: AstralGameSession):
        super().__init__(timeout=180.0)

        self.game: AstralGameSession = game
        self.value: Optional[str] = None

        self.message: Optional[
            Union[nextcord.PartialInteractionMessage, nextcord.WebhookMessage]
        ] = None

        direction_options: list[nextcord.SelectOption] = []
        for player in self.game.players:
            direction_options.append(
                nextcord.SelectOption(label=player.name, value=player.name)
            )

        self.direction_selector: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Направление", options=direction_options
        )
        self.send_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Отправить"
        )

        self.add_item(self.direction_selector)
        self.add_item(self.send_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.data["custom_id"] != self.send_button.custom_id:
            return True
        else:
            if self.direction_selector.values is None:
                try:
                    await interaction.send("Вы не выбрали направление!", ephemeral=True)
                except:
                    await interaction.followup.send(
                        "Вы не выбрали направление!", ephemeral=True
                    )
                return True
            else:
                direction: Optional[str] = self.direction_selector.values[0]

            self.value = direction
            await self.on_timeout()
            self.stop()
            return True

    async def on_timeout(self) -> None:
        if isinstance(self.message, nextcord.PartialInteractionMessage) or isinstance(
            self.message, nextcord.WebhookMessage
        ):
            self.direction_selector.disabled = True
            self.send_button.disabled = True
            try:
                await self.message.edit(view=self)
            except:
                pass
