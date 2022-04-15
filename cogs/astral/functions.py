# for nextcord
import asyncio

import nextcord
from nextcord.ext import commands
from async_timeout import timeout


class FakeAstral(commands.Cog, name="Астрал"):
    """Стратегическая игра Астрал. Требуется MilkBot-Astral"""

    COG_EMOJI = "🌰"

    def __init__(self, bot):
        self.bot = bot

    # список изменений астрала
    @commands.command(brief="Список изменений Астрала")
    @commands.guild_only()
    async def астрал_изменения(self, ctx):
        pass

    # cписок боссов
    @commands.command(brief="Список боссов Астрала")
    @commands.guild_only()
    async def список_монстров(self, ctx):
        pass

    # список арен
    @commands.command(brief="Список арен Астрала")
    @commands.guild_only()
    async def список_арен(self, ctx):
        pass

    @commands.command(brief="Старт с выбранным монстром")
    @commands.guild_only()
    async def астрал_монстерстарт(self, ctx, *args):
        pass

    @commands.command(brief="Остановка игры администратором")
    @commands.guild_only()
    async def астрал_стоп(self, ctx):
        pass

    @commands.command(pass_content=True, brief="Старт игры с боссом")
    @commands.guild_only()
    async def астрал_бот2старт(self, ctx, *args):
        pass

    @commands.command(pass_content=True, brief="Старт игры")
    @commands.guild_only()
    async def астрал_старт2(self, ctx, *args):
        return
        view = nextcord.ui.View()
        modal = nextcord.ui.Modal(title="TEST")

        players_select = nextcord.ui.Select(
            placeholder="Количество игроков",
            options=[
                nextcord.SelectOption(label="2 игрока", value="2", default=True),
                nextcord.SelectOption(label="4 игрока", value="4"),
            ],
        )

        dm_select = nextcord.ui.Select(
            placeholder="DM",
            options=[
                nextcord.SelectOption(label="Включить DM", value="True"),
                nextcord.SelectOption(
                    label="Выключить DM", value="False", default=True
                ),
            ],
        )

        arenas_select = nextcord.ui.Select(
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

        startButton = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Старт"
        )
        cancelButton = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена"
        )

        view.add_item(players_select)
        view.add_item(dm_select)
        view.add_item(arenas_select)
        view.add_item(startButton)
        view.add_item(cancelButton)

        message = await ctx.send("Старт Астрала", view=view)
        players = 2
        dm = False
        arena = "0"

        try:
            async with timeout(180) as SetupTime:
                while True:

                    interaction: nextcord.Interaction = await self.bot.wait_for(
                        "interaction",
                        check=lambda m: m.user.id == ctx.author.id
                        and m.message.id == message.id
                        # and str(m.emoji) in submit,
                    )

                    match interaction.data["custom_id"]:
                        case cancelButton.custom_id:
                            await message.edit("Старт отменён!", view=None)
                            return
                        case startButton.custom_id:
                            break
                        case players_select.custom_id:
                            players = int(interaction.data["values"][0])
                        case dm_select.custom_id:
                            dm = interaction.data["values"][0] == "True"
                        case arenas_select.custom_id:
                            arena = interaction.data["values"][0]

                    print(players)
                    print(dm)
                    print(arena)
                    print(SetupTime.deadline)
        except asyncio.TimeoutError:
            await message.edit("Время вышло", view=None)
            return

        await message.edit(
            f'Ожидаем {"второго игрока!" if players == 2 else "игроков! 1/4"}',
            view=None,
        )

    @commands.command(
        pass_content=True, brief="Старт командной игры для четырёх игроков"
    )
    @commands.guild_only()
    async def астрал_стартк4(self, ctx, *args):
        pass


def setup(bot):
    bot.add_cog(FakeAstral(bot))
