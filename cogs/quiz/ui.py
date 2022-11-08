import nextcord
import requests
from typing import Union, Optional
from nextcord.ext.commands import Context
from modules.ui import FieldModal


class QuizSelector(nextcord.ui.View):
    def __init__(self, author: nextcord.Member):
        super().__init__(timeout=60.0)
        self.author: nextcord.Member = author
        self.questions_json: Optional[dict] = None

        self.modalSpawnButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.blurple, label="Загрузка файла викторины"
        )
        self.startButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Старт"
        )
        self.cancelButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена"
        )

        self.add_item(self.modalSpawnButton)
        self.add_item(self.startButton)
        self.add_item(self.cancelButton)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.modalSpawnButton.custom_id:
                    modal = FieldModal(
                        title="MilkQuiz",
                        label="Введите ссылку на текстовый файл с викториной",
                        placeholder="Ссылка",
                    )

                    try:
                        await interaction.response.send_modal(modal)
                    except:
                        return True

                    await modal.wait()

                    try:
                        r: requests.Response = requests.get(modal.value())
                    except:
                        await interaction.send("Введена не ссылка", ephemeral=True)
                        return True

                    try:
                        self.questions_json = r.json()
                    except:
                        await interaction.send("Не верный файл", ephemeral=True)
                        return True

                case self.startButton.custom_id:
                    if self.questions_json is not None:
                        self.response = {"status": True, "data": self.questions_json}
                        self.stop()
                    else:
                        await interaction.send("Вы не добавили вопросы", ephemeral=True)
                case self.cancelButton.custom_id:
                    self.response = {"status": False, "data": ""}
                    self.stop()
        else:
            await interaction.send("У вас нет прав на это действие!", ephemeral=True)
        return True


class QuizQuestionStarter(nextcord.ui.View):
    def __init__(
        self, author: nextcord.Member, button_text: str = "Старт", timeout: float = 60.0
    ):
        super().__init__(timeout=timeout)
        self.author: nextcord.Member = author
        self.startButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label=button_text
        )
        self.add_item(self.startButton)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.startButton.custom_id:
                    self.author_interaction: nextcord.Interaction = interaction
                    self.stop()
        else:
            await interaction.send("У вас нет прав на это действие!", ephemeral=True)
        return True


class QuizQuestion(nextcord.ui.View):
    def __init__(
        self,
        author: nextcord.Member,
        author_interaction: nextcord.Interaction,
        question: dict,
        timeout: float = 60.0,
    ):
        super().__init__(timeout=timeout)
        self.author: nextcord.Member = author

        self.answers = {}
        self.question: dict = question

        self.author_interaction: nextcord.Interaction = author_interaction

        self.modalSpawnButton = nextcord.ui.Button(
            style=nextcord.ButtonStyle.gray, label="Ответить"
        )
        self.stopButton = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Стоп"
        )

        self.add_item(self.modalSpawnButton)
        self.add_item(self.stopButton)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user.display_name in self.answers:
            return True

        if (
            self.author == interaction.user
            and interaction.data["custom_id"] == self.stopButton.custom_id
        ):
            self.stop()
        elif (
            self.author != interaction.user
            and interaction.data["custom_id"] == self.modalSpawnButton.custom_id
        ):
            if "answers" not in self.question:
                modal = FieldModal(
                    title="MilkQuiz",
                    label="Введите ответ на вопрос",
                    placeholder="Ответ",
                )

                try:
                    await interaction.response.send_modal(modal)
                except:
                    return True

                await modal.wait()

                if modal.value() is not None:
                    await self.author_interaction.followup.send(
                        f"{interaction.user.display_name} ответил: {modal.value()}",
                        ephemeral=True,
                    )
                    self.answers[interaction.user.display_name] = modal.value()
            else:
                answer_view = QuizAnswerFields(self.question)

                await interaction.send(view=answer_view, ephemeral=True)

                await answer_view.wait()

                try:
                    ans = answer_view.answer
                except:
                    await interaction.followup.send("Вы не ответили", ephemeral=True)
                    return True

                await self.author_interaction.followup.send(
                    f"{interaction.user.display_name} ответил: {ans}",
                    ephemeral=True,
                )
                self.answers[interaction.user.display_name] = ans

        return True


class QuizAnswerFields(nextcord.ui.View):
    def __init__(self, question):
        super().__init__(timeout=60.0)

        self.question = question

        options = []

        for answer in self.question["answers"]:
            try:
                options.append(nextcord.SelectOption(label=answer, value=answer))
            except:
                continue

        self.selector = nextcord.ui.Select(
            placeholder="Варианты ответов", options=options
        )
        self.send_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Ответить"
        )

        self.add_item(self.selector)
        self.add_item(self.send_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.data["custom_id"] == self.send_button.custom_id:
            if not self.selector.values:
                await interaction.send("Вы не выбрали вариант ответа!", ephemeral=True)
                return True
            else:
                self.answer = self.selector.values[len(self.selector.values) - 1]
                await interaction.send("Ответ принят!", ephemeral=True)
                try:
                    await interaction.edit_original_message(view=None)
                except:
                    pass

            self.stop()

        return True


class GiveAward(nextcord.ui.View):
    def __init__(
        self, quiz: dict, answers: Union[dict, list], question_log: dict, ctx: Context
    ):
        super().__init__(timeout=60.0)

        self.quiz: dict = quiz
        if isinstance(answers, dict):
            self.answers: list = list(answers.keys())
        else:
            self.answers: list = answers
        self.ctx: Context = ctx
        self.question_log: dict = question_log

        options = []
        for player in self.answers:
            options.append(nextcord.SelectOption(label=player, value=player))

        self.selector: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Участники", options=options
        )
        self.send_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Наградить"
        )

        self.stopButton: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Закончить"
        )

        self.add_item(self.selector)
        self.add_item(self.send_button)
        self.add_item(self.stopButton)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.data["custom_id"] == self.send_button.custom_id:
            if not self.selector.values:
                await interaction.send("Вы не выбрали участника!", ephemeral=True)
                return True
            else:
                member = self.selector.values[len(self.selector.values) - 1]

            modal = FieldModal(
                title="MilkQuiz",
                label=f"Количество баллов для {member}",
                placeholder="Баллы",
            )

            try:
                await interaction.response.send_modal(modal)
            except:
                return True

            await modal.wait()

            try:
                points = int(modal.value())
            except:
                await interaction.send("Введено не число!", ephemeral=True)
                return True

            self.quiz[member].points += points

            await self.ctx.send(
                f"**{member}** получил {points} {'балл' if points == 1 else ''}{'балла' if 2 <= points <= 4 else ''}{'баллов' if points >= 5 else ''}"
            )

            self.question_log["answers"][member] += f" (+{points})"

            return True
        elif interaction.data["custom_id"] == self.stopButton.custom_id:
            self.stop()

        return True
