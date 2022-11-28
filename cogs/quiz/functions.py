import asyncio
import datetime
from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4

import nextcord
from base.base_cog import MilkCog

from .ui import GiveAward, QuizQuestion, QuizQuestionStarter, QuizSelector


@dataclass
class Quiz:
    quiz_uuid: str
    topic: str
    leader: str
    task: Any


@dataclass
class QuizMember:
    name: str
    points: int


class QuizCog(MilkCog, name="Викторины"):
    """Организация викторин."""

    COG_EMOJI: str = "🎲"

    def __init__(self, bot):
        self.bot = bot
        self.quizes_dict = {}

    @MilkCog.slash_command(permission="editor")
    async def quiz(self, interaction: nextcord.Interaction):
        ...

    @quiz.subcommand(description="Список текущих викторин с возможностью остановки")
    async def stop(
        self,
        interaction: nextcord.Interaction,
        quiz_uuid: Optional[str] = nextcord.SlashOption(name="uuid", required=False),
    ):
        await interaction.response.defer()
        if quiz_uuid is not None:
            if interaction.guild.id in self.quizes_dict:
                if quiz_uuid in self.quizes_dict[interaction.guild.id]:
                    self.quizes_dict[interaction.guild.id][quiz_uuid].task.cancel()

                    await self.quizes_dict[interaction.guild.id][quiz_uuid].task
                    return await interaction.followup.send(
                        f"Викторина остановлена. ({interaction.user.mention})"
                    )
                else:
                    return await interaction.followup.send(
                        "Не найдено викторины с таким UUID"
                    )
            else:
                return await interaction.followup.send(
                    "Не найдено викторины с таким UUID"
                )

        embed: nextcord.Embed = nextcord.Embed(
            title="Текущие викторины сервера",
            timestamp=datetime.datetime.now(),
            colour=nextcord.Colour.random(),
        )

        if interaction.guild.id not in self.quizes_dict:
            self.quizes_dict[interaction.guild.id] = {}

        for num, uuid in enumerate(self.quizes_dict[interaction.guild.id]):
            embed.add_field(
                name=f"{num + 1}. {self.quizes_dict[interaction.guild.id][uuid].topic}",
                value=f"Ведущий: {self.quizes_dict[interaction.guild.id][uuid].leader}\n"
                + f"UUID: {self.quizes_dict[interaction.guild.id][uuid].quiz_uuid}",
                inline=False,
            )
        if embed.fields:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(
                "На сервере не запущено ни одной викторины!"
            )

    @quiz.subcommand(description="Запуск викторины")
    async def start(self, interaction: nextcord.Interaction):
        view = QuizSelector(interaction.user)
        message = await interaction.send(view=view)
        await view.wait()

        if not view.response["status"]:
            await message.edit(content="Старт отменён", view=None)
            return
        else:
            await message.edit(content="Подготовка вопросов", view=None)

        quiz_json = view.response["data"]

        if interaction.guild.id not in self.quizes_dict:
            self.quizes_dict[interaction.guild.id] = {}

        quiz_uuid = str(uuid4())

        self.quizes_dict[interaction.guild.id][quiz_uuid] = Quiz(
            quiz_uuid=quiz_uuid,
            topic=quiz_json["topic"],
            leader=str(interaction.user),
            task=asyncio.create_task(
                self.manual_quiz_process(interaction, quiz_json, quiz_uuid)
            ),
        )

    async def manual_quiz_process(
        self, interaction: nextcord.Interaction, quiz_json: dict, quiz_uuid: str
    ):
        try:
            quiz_members = {}

            starter_view = QuizQuestionStarter(interaction.user)

            starter_embed: nextcord.Embed = nextcord.Embed(
                title=quiz_json["topic"],
                colour=nextcord.Colour.random(),
                timestamp=datetime.datetime.now(),
                description=f"Ведуший: {interaction.user.mention}\nБлоки викторины:\n\n",
            )

            starter_embed.set_footer(text=f"UUID: {quiz_uuid}")

            correct_questions_block = 0

            questions_log = []

            for num, block in enumerate(quiz_json["questions_block"]):
                try:
                    starter_embed.description += (
                        f"{num + 1}. {block['topic']} - {len(block['questions'])} "
                        + ("вопрос" if len(block["questions"]) % 10 == 1 else "")
                        + ("вопроса" if 2 <= len(block["questions"]) % 10 <= 4 else "")
                        + ("вопросов" if 5 <= len(block["questions"]) % 10 else "")
                        + "\n"
                    )
                    correct_questions_block += 1
                except:
                    continue

            if correct_questions_block == 0:
                return await interaction.followup.send("Некорректный файл")

            await interaction.channel.send(
                embed=starter_embed,
                view=starter_view,
            )
            await starter_view.wait()

            for block_number, block in enumerate(quiz_json["questions_block"]):
                embed: nextcord.Embed = nextcord.Embed(
                    title=f"{block['topic']} (№{block_number + 1}/{len(quiz_json['questions_block'])})",
                    colour=nextcord.Colour.random(),
                )

                await interaction.channel.send(embed=embed)

                for question_number, question in enumerate(block["questions"]):
                    question_log = {}
                    if question_number % 5 == 0:
                        starter_view = QuizQuestionStarter(
                            interaction.user, button_text="Продолжаем"
                        )
                        await interaction.channel.send(
                            "Технический перерыв для обновления токена",
                            view=starter_view,
                        )
                        await starter_view.wait()

                    embed: nextcord.Embed = nextcord.Embed(
                        timestamp=datetime.datetime.now(),
                        title=f"Вопрос №{question_number + 1}/{len(block['questions'])}",
                        description="",
                        colour=nextcord.Colour.random(),
                    )

                    question_log["block"] = block["topic"]

                    embed.set_footer(text=f"Блок: {block['topic']}")

                    try:
                        right_answer = question["correct_answer"]
                    except:
                        right_answer = "Not found"

                    question_log["right_answer"] = right_answer

                    try:
                        embed.description += (
                            f"Количество баллов за вопрос: {question['points']}"
                            + "\n\n"
                        )
                    except:
                        pass

                    try:
                        embed.description += "**" + question["text"] + "**"
                    except:
                        continue

                    question_log["text"] = question["text"]

                    try:
                        embed.set_image(url=question["img"])
                        embed.description += (
                            "\n\nСсылка на изображение: " + question["img"]
                        )
                    except:
                        pass

                    if interaction.user.avatar:
                        embed.set_author(
                            name=interaction.user.display_name,
                            icon_url=interaction.user.avatar.url,
                        )
                    else:
                        embed.set_author(
                            name=interaction.user.display_name,
                            icon_url=f"https://cdn.discordapp.com/embed/avatars/{int(interaction.user.discriminator) % 5}.png",
                        )

                    quiz_view = QuizQuestion(
                        interaction.user, starter_view.author_interaction, question
                    )

                    message = await interaction.channel.send(
                        embed=embed, view=quiz_view
                    )

                    await quiz_view.wait()

                    await message.edit(view=None)

                    if "correct_answer" in question:
                        await interaction.channel.send(
                            f"Правильный ответ: {question['correct_answer']}"
                        )

                    question_log["answers"] = {}

                    if quiz_view.answers.items():
                        embed: nextcord.Embed = nextcord.Embed(
                            title="Ответы пользователей в порядке фиксации",
                            colour=nextcord.Colour.brand_green(),
                            description="",
                        )

                        for num, answer in enumerate(quiz_view.answers.items()):
                            embed.description += (
                                f"{num + 1}. **{answer[0]}** - {answer[1]}"
                                + (" (верный)" if answer[1] == right_answer else "")
                                + "\n"
                            )

                            question_log["answers"][answer[0]] = answer[1] + (
                                " (верный)" if answer[1] == right_answer else ""
                            )

                        if interaction.guild.icon:
                            embed.set_thumbnail(url=interaction.guild.icon.url)

                        await interaction.channel.send(embed=embed)

                    for user in quiz_view.answers:
                        if user not in quiz_members:
                            quiz_members[user] = QuizMember(name=user, points=0)

                    if quiz_view.answers.values():
                        await interaction.channel.send(
                            "Пожалуйста, подождите окончания выдачи баллов"
                        )

                        award_view = GiveAward(
                            quiz_members,
                            quiz_view.answers,
                            question_log,
                            interaction.channel,
                        )

                        await starter_view.author_interaction.followup.send(
                            view=award_view, ephemeral=True
                        )
                        await award_view.wait()

                    questions_log.append(question_log)

                if (block_number + 1) != len(quiz_json["questions_block"]):
                    embed: nextcord.Embed = nextcord.Embed(
                        title="Текущие баллы участников",
                        colour=nextcord.Colour.brand_green(),
                        description="",
                    )

                    quiz_members_list = list(quiz_members.values())
                    quiz_members_list.sort(
                        key=lambda member: member.points, reverse=True
                    )

                    for pos, member in enumerate(quiz_members_list):
                        embed.description += (
                            f"{pos + 1}. **{member.name}** - {member.points}\n"
                        )

                    if interaction.guild.icon:
                        embed.set_thumbnail(url=interaction.guild.icon.url)

                    await interaction.channel.send(embed=embed)

            embed: nextcord.Embed = nextcord.Embed(
                title="Результаты викторины",
                colour=nextcord.Colour.brand_green(),
                description="",
            )

            quiz_members_list: list[QuizMember] = list(quiz_members.values())
            quiz_members_list.sort(key=lambda member: member.points, reverse=True)

            quiz_members_points: list[int] = list(
                {member.points for member in quiz_members_list}
            )
            quiz_members_points.sort(reverse=True)

            if len(quiz_members_points) >= 1:
                quiz_winner_points: int = quiz_members_points[0]

            else:
                quiz_winner_points: int = -1
                quiz_prize_i_points: int = -1
                quiz_prize_ii_points: int = -1

            if len(quiz_members_points) >= 2:
                quiz_prize_i_points: int = quiz_members_points[1]
            else:
                quiz_prize_i_points: int = -1

            if len(quiz_members_points) >= 3:
                quiz_prize_ii_points: int = quiz_members_points[2]
            else:
                quiz_prize_ii_points: int = -1

            question_log = {}
            question_log["block"] = "Итоговые баллы"
            question_log["right_answer"] = ""
            question_log["text"] = ""
            question_log["answers"] = {}

            for pos, member in enumerate(quiz_members_list):
                place_str: str = (
                    (
                        " Победитель"
                        if member.points == quiz_winner_points and member.points != 0
                        else ""
                    )
                    + (
                        " Призёр I"
                        if member.points == quiz_prize_i_points and member.points != 0
                        else ""
                    )
                    + (
                        " Призёр II"
                        if member.points == quiz_prize_ii_points and member.points != 0
                        else ""
                    )
                )

                embed.description += (
                    f"{pos + 1}. **{member.name}** - {member.points}" + place_str + "\n"
                )

                question_log["answers"][member.name] = str(member.points) + place_str

            questions_log.append(question_log)

            embed.set_footer(text="Спасибо всем участникам!")

            if interaction.guild.icon:
                embed.set_thumbnail(url=interaction.guild.icon.url)

            await interaction.channel.send(embed=embed)

        except asyncio.CancelledError:
            await interaction.channel.send("Принудительная остановка викторины")
        finally:
            await interaction.channel.send(f"Викторина окончена\nUUID: {quiz_uuid}")
            del self.quizes_dict[interaction.guild.id][quiz_uuid]


def setup(bot):
    bot.add_cog(QuizCog(bot))
