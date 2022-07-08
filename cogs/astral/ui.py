import nextcord
from math import floor
from typing import Optional
from .api import AstralGameSession, AstralGamePlayer

spells = {
    "11": "3",
    "12": "3",
    "13": "3",
    "14": "3",
    "15": "3",
    "16": "3",
    "17": "3",
    "18": "3",
    "19": "3",
    "110": "3",
    "111": "3",
    "112": "3",
    "113": "3",
    "114": "3",
    "115": "4",
    "116": "3",
    "117": "3",
    "118": "3",
    "119": "3",
    "120": "3",
    "121": "3",
    "122": "3",
    "123": "3",
    "124": "3",
    "125": "3",
    "126": "3",
    "127": "-100",
    "128": "4",
    "129": "3",
    "130": "-100",
    "131": "3",
    "132": "3",
    "133": "3",
    "134": "3",
    "135": "3",
    "136": "3",
    "137": "3",
    "138": "3",
    "139": "3",
    "140": "3",
    "141": "-100",
    "142": "4",
    "143": "3",
    "144": "3",
    "145": "3",
    "146": "-100",
    "147": "-100",
    "148": "3",
    "149": "3",
    "150": "3",
    "151": "3",
    "152": "-100",
    "153": "3",
    "154": "3",
    "155": "3",
    "156": "3",
    "157": "3",
    "158": "3",
    "159": "-100",
    "160": "3",
    "161": "4",
    "162": "3",
    "163": "3",
    "164": "3",
    "165": "3",
    "166": "3",
    "167": "3",
    "168": "3",
    "169": "3",
    "170": "3",
    "21": "8",
    "22": "8",
    "23": "8",
    "24": "8",
    "25": "8",
    "26": "9",
    "27": "8",
    "28": "8",
    "29": "-100",
    "210": "8",
    "211": "8",
    "212": "8",
    "213": "8",
    "214": "8",
    "215": "8",
    "216": "8",
    "217": "8",
    "218": "9",
    "219": "8",
    "220": "8",
    "221": "8",
    "222": "8",
    "223": "8",
    "224": "8",
    "225": "8",
    "226": "8",
    "227": "8",
    "228": "8",
    "229": "8",
    "230": "8",
    "231": "8",
    "232": "9",
    "233": "-100",
    "234": "-100",
    "235": "8",
    "236": "8",
    "237": "8",
    "238": "8",
    "239": "8",
    "240": "8",
    "241": "8",
    "242": "8",
    "243": "8",
    "244": "8",
    "245": "8",
    "246": "8",
    "247": "8",
    "248": "8",
    "249": "8",
    "250": "8",
    "251": "8",
    "252": "8",
    "253": "8",
    "254": "8",
    "255": "8",
    "256": "8",
    "257": "8",
    "258": "-100",
    "259": "8",
    "260": "8",
    "261": "8",
    "262": "8",
    "263": "8",
    "264": "8",
    "265": "8",
    "266": "8",
    "267": "8",
    "268": "8",
    "269": "8",
    "270": "8",
    "31": "15",
    "32": "15",
    "33": "15",
    "34": "15",
    "35": "15",
    "36": "15",
    "37": "15",
    "38": "15",
    "39": "15",
    "310": "15",
    "311": "15",
    "312": "15",
    "313": "15",
    "314": "15",
    "315": "15",
    "316": "15",
    "317": "15",
    "318": "15",
    "319": "15",
    "320": "15",
    "321": "15",
    "322": "15",
    "323": "15",
    "324": "15",
    "325": "15",
    "326": "15",
    "327": "15",
    "328": "15",
    "329": "15",
    "330": "15",
    "331": "15",
    "332": "15",
    "333": "15",
    "334": "15",
    "335": "15",
    "41": "20",
    "гг": "-100",
    "х": "-100",
    "б": "-100",
    "д": "-100",
    "ж": "-100",
    "л": "-100",
    "м": "-100",
    "о": "-100",
    "п": "-100",
    "с": "-100",
    "ф": "-100",
    "ч": "-100",
}


class AstralPlayersStart(nextcord.ui.View):
    def __init__(self, author: nextcord.Member):
        super().__init__(timeout=60.0)
        self.author: nextcord.Member = author
        self.response: Optional[dict] = None

        self.players_select: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Количество игроков",
            options=[
                nextcord.SelectOption(label="2 игрока", value="2", default=True),
                nextcord.SelectOption(label="4 игрока", value="4"),
            ],
        )

        self.dm_select: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="DM",
            options=[
                nextcord.SelectOption(label="Включить DM", value="True"),
                nextcord.SelectOption(
                    label="Выключить DM", value="False", default=True
                ),
            ],
        )

        self.arenas_select: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Арена",
            options=[
                nextcord.SelectOption(label="Вне арены", value="0", default=True),
                nextcord.SelectOption(label="Вулкан", value="1"),
                nextcord.SelectOption(label="Джунгли", value="2"),
                nextcord.SelectOption(label="Ледник", value="3"),
                nextcord.SelectOption(label="Пустыня", value="4"),
                nextcord.SelectOption(label="Арена Магов", value="5"),
                nextcord.SelectOption(label="Кладбище", value="6"),
                nextcord.SelectOption(label="Атлантида", value="7"),
                nextcord.SelectOption(label="Ад", value="8"),
                nextcord.SelectOption(label="Пешера", value="9"),
                nextcord.SelectOption(label="Новый год", value="10"),
                nextcord.SelectOption(label="Случайная", value="R"),
            ],
        )

        self.startButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Старт"
        )
        self.cancelButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена"
        )

        self.add_item(self.players_select)
        self.add_item(self.dm_select)
        self.add_item(self.arenas_select)
        self.add_item(self.startButton)
        self.add_item(self.cancelButton)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.startButton.custom_id:
                    self.response: dict = {
                        "status": True,
                        "players": int(self.players_select.values[0])
                        if self.players_select.values != []
                        else 2,
                        "dm": bool(self.dm_select.values[0])
                        if self.dm_select.values != []
                        else False,
                        "arena": self.arenas_select.values[0]
                        if self.arenas_select.values != []
                        else "0",
                    }
                    self.stop()
                case self.cancelButton.custom_id:
                    self.response: dict = {"status": False}
                    self.stop()
        else:
            await interaction.send("У вас нет прав на это действие!", ephemeral=True)
        return True


class AstralBotStart(nextcord.ui.View):
    def __init__(self, author: nextcord.Member):
        super().__init__(timeout=60.0)
        self.author: nextcord.Member = author
        self.response: Optional[dict] = None

        self.arenas_select: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Арена",
            options=[
                nextcord.SelectOption(label="Вне арены", value="0", default=True),
                nextcord.SelectOption(label="Вулкан", value="1"),
                nextcord.SelectOption(label="Джунгли", value="2"),
                nextcord.SelectOption(label="Ледник", value="3"),
                nextcord.SelectOption(label="Пустыня", value="4"),
                nextcord.SelectOption(label="Арена Магов", value="5"),
                nextcord.SelectOption(label="Кладбище", value="6"),
                nextcord.SelectOption(label="Атлантида", value="7"),
                nextcord.SelectOption(label="Ад", value="8"),
                nextcord.SelectOption(label="Пешера", value="9"),
                nextcord.SelectOption(label="Новый год", value="10"),
                nextcord.SelectOption(label="Случайная", value="R"),
            ],
        )

        self.startButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Старт"
        )
        self.cancelButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена"
        )

        self.add_item(self.arenas_select)
        self.add_item(self.startButton)
        self.add_item(self.cancelButton)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.startButton.custom_id:
                    self.response: dict = {
                        "status": True,
                        "boss": "AstralBot",
                        "arena": self.arenas_select.values[0]
                        if self.arenas_select.values != []
                        else "0",
                    }
                    self.stop()
                case self.cancelButton.custom_id:
                    self.response: dict = {"status": False}
                    self.stop()
        else:
            await interaction.send("У вас нет прав на это действие!", ephemeral=True)
        return True


class AstralBossStart(nextcord.ui.View):
    def __init__(self, author: nextcord.Member):
        super().__init__(timeout=60.0)
        self.author: nextcord.Member = author
        self.response: Optional[dict] = None

        self.boss_select: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Босс",
            options=[
                nextcord.SelectOption(label="Тварь из бездны", value="Тварь из бездны"),
                nextcord.SelectOption(
                    label="Первородный дракон", value="Первородный дракон"
                ),
                nextcord.SelectOption(label="Кицунэ", value="Кицунэ"),
                nextcord.SelectOption(label="Кровавый пузырь", value="Кровавый пузырь"),
                nextcord.SelectOption(label="Читерный бот", value="AstralBotLol"),
            ],
        )

        self.arenas_select: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Арена",
            options=[
                nextcord.SelectOption(label="Вне арены", value="0", default=True),
                nextcord.SelectOption(label="Вулкан", value="1"),
                nextcord.SelectOption(label="Джунгли", value="2"),
                nextcord.SelectOption(label="Ледник", value="3"),
                nextcord.SelectOption(label="Пустыня", value="4"),
                nextcord.SelectOption(label="Арена Магов", value="5"),
                nextcord.SelectOption(label="Кладбище", value="6"),
                nextcord.SelectOption(label="Атлантида", value="7"),
                nextcord.SelectOption(label="Ад", value="8"),
                nextcord.SelectOption(label="Пешера", value="9"),
                nextcord.SelectOption(label="Новый год", value="10"),
                nextcord.SelectOption(label="Случайная", value="R"),
            ],
        )

        self.startButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Старт"
        )
        self.cancelButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена"
        )

        self.add_item(self.boss_select)
        self.add_item(self.arenas_select)
        self.add_item(self.startButton)
        self.add_item(self.cancelButton)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.startButton.custom_id:
                    self.response: dict = {
                        "status": True,
                        "boss": self.boss_select.values[0],
                        "arena": self.arenas_select.values[0]
                        if self.arenas_select.values != []
                        else "0",
                    }
                    self.stop()
                case self.cancelButton.custom_id:
                    self.response: dict = {"status": False}
                    self.stop()
        else:
            try:
                await interaction.send(
                    "У вас нет прав на это действие!", ephemeral=True
                )
            except:
                await interaction.followup.send(
                    "У вас нет прав на это действие!", ephemeral=True
                )
        return True


class GameMessage(nextcord.ui.View):
    def __init__(self, game: AstralGameSession):
        super().__init__(timeout=180.0)

        self.game: AstralGameSession = game

        self.table_button: nextcord.ui.Button = nextcord.ui.Button(label="Таблица")
        self.move_button: nextcord.ui.Button = nextcord.ui.Button(label="Сделать ход")

        self.add_item(self.table_button)
        self.add_item(self.move_button)

        self.response: list[dict] = []
        self.players_moved: int = 0
        self.players_with_ability_count: int = len(
            list(
                filter(lambda player: player.ability and not player.moved, game.players)
            )
        )

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.id in self.game.players_ids:
            if self.game.players[
                self.game.players_ids.index(interaction.user.id)
            ].ability:
                match interaction.data["custom_id"]:

                    case self.table_button.custom_id:
                        try:
                            await interaction.send(
                                self.game.players[
                                    self.game.players_ids.index(interaction.user.id)
                                ].link,
                                ephemeral=True,
                            )
                        except:
                            await interaction.followup.send(
                                self.game.players[
                                    self.game.players_ids.index(interaction.user.id)
                                ].link,
                                ephemeral=True,
                            )
                    case self.move_button.custom_id:
                        spell: Optional[str] = await get_spell_from_modal(
                            interaction,
                            self.game.players[
                                self.game.players_ids.index(interaction.user.id)
                            ],
                            "Введите номер заклинания",
                        )

                        if spell is not None:
                            if spell in spells:
                                if (
                                    spell in ["119", "140", "168", "242", "245"]
                                    or len(self.game.players) == 4
                                ):
                                    direction = await get_direction_from_view(
                                        interaction, self.game
                                    )
                                else:
                                    direction = None

                                self.response.append(
                                    {
                                        "name": self.game.players[
                                            self.game.players_ids.index(
                                                interaction.user.id
                                            )
                                        ].name,
                                        "spell": spell,
                                        "direction": direction,
                                    }
                                )

                                self.players_moved += 1

                                try:
                                    await interaction.send(
                                        f"Ход был сделан игроком **{interaction.user.display_name}**!"
                                    )
                                except:
                                    await interaction.followup.send(
                                        f"Ход был сделан игроком **{interaction.user.display_name}**!"
                                    )

                                if (
                                    self.players_moved
                                    == self.players_with_ability_count
                                ):
                                    try:
                                        await interaction.edit_original_message(
                                            view=None
                                        )
                                    except:
                                        pass
                                    self.stop()
                            else:
                                try:
                                    await interaction.send(spell, ephemeral=True)
                                except:
                                    await interaction.followup.send(
                                        spell, ephemeral=True
                                    )
                        else:
                            return True
            elif len(self.game.players) == 2 and self.game.with_bot():
                try:
                    await interaction.edit_original_message(view=None)
                except:
                    pass
                self.stop()
            else:
                try:
                    await interaction.send(
                        "На вас наложен эффект, ограничивающий способности заклинателя.",
                        ephemeral=True,
                    )
                except:
                    await interaction.followup.send(
                        "На вас наложен эффект, ограничивающий способности заклинателя.",
                        ephemeral=True,
                    )
        else:
            return True


async def get_spell_from_modal(
    interaction: nextcord.Interaction, player: AstralGamePlayer, label: str
) -> Optional[str]:
    modal = FieldModal(title="Астрал", label=label, placeholder="Заклинание")

    try:
        await interaction.response.send_modal(modal)
    except:
        return None

    await modal.wait()
    try:
        spell = modal.value().lower()
    except:
        return

    if spell in player.spells:
        if (
            player.effects.find("фанатизм") != -1
            or player.effects.find("воля титана") != -1
            or player.effects.find("сфера пустоты") != -1
        ):
            return spell
        elif player.effects.find("корни") != -1:
            if int(player.mp) >= int(spells[spell]) + 2:
                return spell
            else:
                return "Введите заклинание, на которое у вас хватает маны!"
        elif player.effects.find("контроль энергии") != -1:
            if int(player.mp) >= floor(float(spells[spell]) / 2):
                return spell
            else:
                return "Введите заклинание, на которое у вас хватает маны!"
        elif int(player.mp) >= int(spells[spell]):
            return spell
        else:
            return "Введите заклинание, на которое у вас хватает маны!"
    else:
        return "Введите заклинание из таблицы!"


async def get_direction_from_view(
    interaction: nextcord.Interaction, game: AstralGameSession
) -> Optional[str]:
    view = DirectionMessage(game)

    try:
        await interaction.send(view=view, ephemeral=True)
    except:
        await interaction.followup.send(view=view, ephemeral=True)
    await view.wait()

    if view.value is not None:
        return view.value
    else:
        return await get_direction_from_view(interaction, game)


class DirectionMessage(nextcord.ui.View):
    def __init__(self, game: AstralGameSession):
        super().__init__(timeout=180.0)

        self.game: AstralGameSession = game
        self.value: Optional[str] = None

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
            self.stop()
            return True


class FieldModal(nextcord.ui.Modal):
    def __init__(
        self,
        title: Optional[str] = None,
        label: Optional[str] = None,
        placeholder: Optional[str] = None,
    ):
        super().__init__(title=title, timeout=60.0)

        self.field = nextcord.ui.TextInput(
            label=label,
            placeholder=placeholder,
            required=True,
            min_length=1,
            max_length=3,
        )
        self.add_item(self.field)

    async def callback(self, interaction: nextcord.Interaction):
        self.stop()

    def value(self) -> Optional[str]:
        return self.field.value
