import nextcord
import datetime

from nextcord.ext.commands import Context
from nextcord.ext import commands
import asyncio
from uuid import uuid4

from .ui import QuizSelector, QuizQuestionStarter, QuizQuestion, GiveAward
from checkers import check_editor_permission, check_admin_permissions

from dataclasses import dataclass
from typing import Any

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


class QuizCog(nextcord.ext.commands.Cog, name="Викторины"):
    """Организация викторин."""

    COG_EMOJI = "🎲"

    def __init__(self, bot):
        self.bot = bot
        self.quizes_dict = {}

    @commands.command(pass_content=True, brief="Список текущих викторин с возможностью остановки")
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def остановка_викторины(self, ctx: Context, quiz_uuid: str = ""):
        if quiz_uuid != "":
            if ctx.guild.id in list(self.quizes_dict.keys()):
                if quiz_uuid in list(self.quizes_dict[ctx.guild.id].keys()):
                    self.quizes_dict[ctx.guild.id][quiz_uuid].task.cancel()

                    await self.quizes_dict[ctx.guild.id][quiz_uuid].task
                    return await ctx.send(f"Викторина остановлена. ({ctx.author.mention})")
                else:
                    return await ctx.send("Не найдено викторины с таким UUID")
            else:
                return await ctx.send("Не найдено викторины с таким UUID")

        embed: nextcord.Embed = nextcord.Embed(
            title="Текущие викторины сервера",
            timestamp=datetime.datetime.now(),
            colour=nextcord.Colour.random()
        )

        if ctx.guild.id not in list(self.quizes_dict.keys()):
            self.quizes_dict[ctx.guild.id] = {}

        for num, uuid in enumerate(list(self.quizes_dict[ctx.guild.id].keys())):
            embed.add_field(
                name=f"{num+1}. {self.quizes_dict[ctx.guild.id][uuid].topic}",
                value=f"Ведущий: {self.quizes_dict[ctx.guild.id][uuid].leader}\nUUID: {self.quizes_dict[ctx.guild.id][uuid].quiz_uuid}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(pass_content=True, brief="Запуск викторины")
    @commands.check(check_editor_permission)
    @commands.guild_only()
    async def викторина(self, ctx: Context):
        view = QuizSelector(ctx.author)

        message = await ctx.send(view=view)
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
            await message.edit("Подготовка вопросов", view=None)

        quiz_json = view.response["data"]

        if ctx.guild.id not in list(self.quizes_dict.keys()):
            self.quizes_dict[ctx.guild.id] = {}

        quiz_uuid = str(uuid4())

        self.quizes_dict[ctx.guild.id][quiz_uuid] = Quiz(
            quiz_uuid=quiz_uuid,
            topic=quiz_json['topic'],
            leader=str(ctx.author),
            task=asyncio.create_task(self.manual_quiz_process(ctx, quiz_json, quiz_uuid))
        )

    async def manual_quiz_process(self, ctx: Context, quiz_json: dict, quiz_uuid: str):
        try:
            quiz_members = {}

            starter_view = QuizQuestionStarter(ctx.author)

            starter_embed: nextcord.Embed = nextcord.Embed(
                title=quiz_json['topic'],
                colour=nextcord.Colour.random(),
                timestamp=datetime.datetime.now(),
                description=f"Ведуший: {ctx.author.mention}\nБлоки викторины:\n\n"
            )

            starter_embed.set_footer(text=f"UUID: {quiz_uuid}")

            correct_questions_block = 0

            questions_log = []

            for num, block in enumerate(quiz_json['questions_block']):
                try:
                    starter_embed.description += (
                        f"{num+1}. {block['topic']} - {len(block['questions'])} "
                        + ("вопрос" if len(block['questions']) % 10 == 1 else "")
                        + ("вопроса" if 2 <= len(block['questions']) % 10 <= 4 else "")
                        + ("вопросов" if 5 <= len(block['questions']) % 10 else "")
                        + "\n"
                    )
                    correct_questions_block += 1
                except:
                    continue

            if correct_questions_block == 0:
                return await ctx.send("Некорректный файл")

            await ctx.send(
                embed=starter_embed,
                view=starter_view,
            )
            await starter_view.wait()

            for block_number, block in enumerate(quiz_json['questions_block']):
                embed: nextcord.Embed = nextcord.Embed(
                    title=f"{block['topic']} (№{block_number+1}/{len(quiz_json['questions_block'])})",
                    colour=nextcord.Colour.random()
                )

                await ctx.send(embed=embed)

                for question_number, question in enumerate(block['questions']):
                    question_log = {}
                    if question_number % 5 == 0:
                        starter_view = QuizQuestionStarter(ctx.author, button_text="Продолжаем")
                        await ctx.send("Технический перерыв для обновления токена",
                                       view=starter_view)
                        await starter_view.wait()

                    embed: nextcord.Embed = nextcord.Embed(
                        timestamp=datetime.datetime.now(),
                        title=f"Вопрос №{question_number+1}/{len(block['questions'])}",
                        description="",
                        colour=nextcord.Colour.random(),
                    )

                    question_log['block'] = block['topic']

                    embed.set_footer(text=f"Блок: {block['topic']}")

                    try:
                        right_answer = question['correct_answer']
                    except:
                        right_answer = "Not found"

                    question_log['right_answer'] = right_answer

                    try:
                        embed.description += (
                            f"Количество баллов за вопрос: {question['points']}"
                            + "\n\n"
                        )
                    except:
                        pass

                    try:
                        embed.description += question['text']
                    except:
                        continue

                    question_log['text'] = question['text']

                    try:
                        embed.set_image(url=question["img"])
                        embed.description += (
                            "\n\nСсылка на изображение: " + question["img"]
                        )
                    except:
                        pass

                    if ctx.author.avatar:
                        embed.set_author(
                            name=ctx.author.display_name, icon_url=ctx.author.avatar.url
                        )
                    else:
                        embed.set_author(
                            name=ctx.author.display_name,
                            icon_url=f"https://cdn.discordapp.com/embed/avatars/{int(ctx.author.discriminator) % 5}.png",
                        )

                    quiz_view = QuizQuestion(
                        ctx.author, starter_view.author_interaction, question
                    )

                    message = await ctx.send(embed=embed, view=quiz_view)

                    await quiz_view.wait()

                    await message.edit(view=None)

                    try:
                        await ctx.send(f"Правильный ответ: {question['correct_answer']}")
                    except:
                        pass

                    question_log['answers'] = {}

                    if list(quiz_view.answers.values()):
                        embed: nextcord.Embed = nextcord.Embed(
                            title="Ответы пользователей в порядке фиксации",
                            colour=nextcord.Colour.brand_green(),
                            description="",
                        )

                        for pos in range(len(quiz_view.answers.values())):
                            embed.description += (
                                f"{pos+1}. **{list(quiz_view.answers.keys())[pos]}** - {list(quiz_view.answers.values())[pos]}"
                                + (' (верный)' if list(quiz_view.answers.values())[pos] == right_answer else '')
                                + "\n"
                            )

                            question_log['answers'][list(quiz_view.answers.keys())[pos]] = (
                                list(quiz_view.answers.values())[pos]
                                + (' (верный)' if list(quiz_view.answers.values())[pos] == right_answer else '')
                            )

                        if ctx.guild.icon:
                            embed.set_thumbnail(url=ctx.guild.icon.url)

                        await ctx.send(embed=embed)

                    for user in list(quiz_view.answers.keys()):
                        if user not in list(quiz_members.keys()):
                            quiz_members[user] = QuizMember(name=user, points=0)

                    if list(quiz_view.answers.values()):
                        await ctx.send("Пожалуйста, подождите окончания выдачи баллов")

                        award_view = GiveAward(quiz_members, quiz_view.answers, question_log, ctx)

                        await starter_view.author_interaction.followup.send(
                            view=award_view, ephemeral=True
                        )
                        await award_view.wait()

                    questions_log.append(question_log)

                if (block_number + 1) != len(quiz_json['questions_block']):
                    embed: nextcord.Embed = nextcord.Embed(
                        title="Текущие баллы участников",
                        colour=nextcord.Colour.brand_green(),
                        description="",
                    )

                    quiz_members_list = list(quiz_members.values())
                    quiz_members_list.sort(key=lambda member: member.points, reverse=True)

                    for pos, member in enumerate(quiz_members_list):
                        embed.description += f"{pos + 1}. **{member.name}** - {member.points}\n"

                    if ctx.guild.icon:
                        embed.set_thumbnail(url=ctx.guild.icon.url)

                    await ctx.send(embed=embed)

            embed: nextcord.Embed = nextcord.Embed(
                title="Результаты викторины",
                colour=nextcord.Colour.brand_green(),
                description="",
            )

            quiz_members_list = list(quiz_members.values())
            quiz_members_list.sort(key=lambda member: member.points, reverse=True)

            quiz_members_points = list({member.points for member in quiz_members_list})
            quiz_members_points.sort(reverse=True)

            quiz_winner_points = -1
            quiz_prize_i_points = -1
            quiz_prize_ii_points = -1

            try:
                quiz_winner_points = quiz_members_points[0]
                quiz_prize_i_points = quiz_members_points[1]
                quiz_prize_ii_points = quiz_members_points[2]
            except:
                pass

            for pos, member in enumerate(quiz_members_list):
                embed.description += (
                    f"{pos+1}. **{member.name}** - {member.points}"
                    + (
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
                    + "\n"
                )

            embed.description += (
                "\n\nТаблица-отчет: " + self.bot.tables.generate_quiz_table(quiz_uuid, questions_log)
            )

            embed.set_footer(text="Спасибо всем участникам!")

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            await ctx.send(embed=embed)

        except asyncio.CancelledError:
            await ctx.send("Принудительная остановка викторины")
        finally:
            await ctx.send(f"Викторина окончена\nUUID: {quiz_uuid}")
            del self.quizes_dict[ctx.guild.id][quiz_uuid]


def setup(bot):
    bot.add_cog(QuizCog(bot))
