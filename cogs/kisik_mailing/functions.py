import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
from modules.checkers import check_admin_permissions
import random


class KisikMailing(commands.Cog, name="Рассылка [Кисик]"):
    """Рассылка различных сообщений для администраторов"""

    COG_EMOJI: str = "✉"

    def __init__(self, bot):

        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.guild is None:
            return True
        else:
            return ctx.message.guild.id in [876474448126050394, 938461972448559116]

    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        if self.bot.bot_type == "helper":
            return

        if member.guild.id == 876474448126050394:
            roles: list[int] = [
                876494696153743450,
                876483834672189481,
                876483833841721434,
                876483833250320465,
                876483832205963315,
                879220481675362375,
                879220494321205278,
            ]
            if any(role.id in roles for role in member.roles):
                channel: nextcord.TextChannel = self.bot.get_channel(876474448126050397)
                responses: list[str] = ["Шлюпка {}({}) отчалила. Удачи."]
                await channel.send(
                    random.choice(responses).format(member.mention, member.name)
                )

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if self.bot.bot_type == "helper":
            return

        if message.channel.id == 876541671997837312:
            await message.add_reaction("✅")
            await message.add_reaction("❌")

    @commands.command(brief="Отправка правил")
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def rules(self, ctx: Context):
        await ctx.trigger_typing()

        embed: nextcord.Embed = nextcord.Embed(
            description="**Корабль котиков в первую очередь придерживается правил [Discord Terms of Service](https://discord.com/terms) и [Discord Community Guidelines](https://discord.com/guidelines), поэтому настоятельно рекомендуем для начала ознакомиться с ними.**",
            colour=0x91E1FE,
        )
        await ctx.send(embed=embed)

        embed: nextcord.Embed = nextcord.Embed(
            title="Общие правила",
            description="1.1 На сервере действует ограничение по возрасту __**16+**__. В связи с этим ограничением каждый участник обязан сообщить по требованию администрации свой настоящий возраст (можно в лс). Сокрытие возраста приведёт к бану на сервере.\n`Возможны исключения, обращаться к администрации.`\n\n1.2 Запрещается неадекватное/токсичное поведение. Запрещено оскорбление, унижение участников сервера. Запрещены аморальные действия по отношению к участникам сервера. (оскорбления, вывод на конфликт, угрозы и т. п.).\n\n1.3 Запрещается дискриминация по любому признаку: расовому, национальному, гражданскому, половому, религиозному, возрастному, роду занятий или сексуальной ориентации.\n\n1.4 Запрещается пропаганда наркотиков, терроризма, материала, содержащего сцены сексуального и шокирующего характера. Запрещено распространение 18+ контента вне NSFW канала, который в свою очередь также имеет ограничения, ознакомиться с ними можно в описании соответствующего канала.\n\n1.5 Запрещены ники, содержащие провокационные выражения, оскорбления, мат, завуалированный мат, а также те, которые могут дублировать роли администрации. Пользователи с аватарками/баннерами, содержащими провокационный/откровенный контент, должны удалить или сменить аватарку/баннер, в противном случае это будет расцениваться как нарушение правила ToS. Пользователи сервера со статусом, содержащим оскорбительные высказывания или провокационные выражения, должны удалить/сменить его.\n\n1.6 Запрещается распространение личной информации, без согласия её владельца (например: адреса, телефоны, фотографии, профилей в соцсетях и пр.).\n\n1.7 Запрещается использовать наш сервер для рекламы сторонних серверов, различных товаров и услуг.\n\n1.8 Запрещена намеренная помеха нормальной работе и развитию сервера, а также функционированию ботов.\n\n1.9 Запрещен обход любых блокировок на сервере.\n\n1.10 Запрещена рассылка чего-либо в лс участников.\n\n1.11 Запрещено использование твинк-аккаунтов на сервере.\n\n1.12 Запрещено выпрашивание чего-либо у администрации.\n\n1.13 Запрещено использование внешних эмодзи/стикеров (эмодзи/стикеров с других серверов), нарушающих правила данного сервера.\n\n1.14 Запрещено распространение спойлеров на сервере (исключение – картинки и текст с пометкой спойлер с заблаговременным оповещением участников об их содержании).\n\n1.15 Запрещено обсуждение в неуважительном ключе и неконструктивная критика действий администрации/модерации.",
            colour=0x9DD1FE,
        )
        await ctx.send(embed=embed)

        embed: nextcord.Embed = nextcord.Embed(
            title="Правила общения в текстовом чате",
            description="2.1 Запрещается обилие капса, спама и флуда в любых его проявлениях.\n\n2.2 Запрещаются беспричинные пинги.\n\n2.3 Запрещено излишнее/неуместное использование мата.\n\n2.4 Запрещено злоупотребление ветками чата.\n\n2.5 Запрещено использование чатов не по их назначению (тематике).",
            colour=0xACBDFE,
        )
        await ctx.send(embed=embed)

        embed: nextcord.Embed = nextcord.Embed(
            title="Правила общения в голосовом чате",
            description="3.1 Запрещено издавать какие-либо неприятные/раздражающие звуки (soundpad, voice changer, крики, чавканье, ор и тд). или мешать остальным участникам в голосовом канале каким-либо иным способом.\n\n3.2 Запрещена демонстрация порнографического или другого шокирующего контента через веб-камеру или стрим.\n\n3.3 Запрещена многократная смена голосовых каналов за короткий промежуток времени.\n\n3.4 Запрещено включать музыку без согласия всех присутствующих в голосовом канале.",
            colour=0xB6B0FE,
        )
        await ctx.send(embed=embed)

        embed: nextcord.Embed = nextcord.Embed(title="Автомодерация", colour=0xC69CFE)
        embed.set_footer(
            text="Использование эмодзи - 8 эмодзи подряд (удаление сообщения);\n\nCaps Lock - 8 символов (удаление сообщения);\n\nФлуд - 5 одинаковых сообщений (мут 10 минут);\n\nПинги участников/комнат - 8 пингов (мут 5 минут)."
        )
        await ctx.send(embed=embed)

        embed: nextcord.Embed = nextcord.Embed(title="Примечания", colour=0xD588FF)
        embed.set_footer(
            text="Незнание правил не освобождает от ответственности.\n\nПредупреждения могут быть выданы администрацией за нарушения настоящих правил. Получение трёх предупреждений приравнивается к муту на два дня.\n\nНастоящие правила сервера могут быть изменены или дополнены в любой момент с уведомлением участников.\n\nСрок, на который выдается предупреждение или мут, выбирается администрацией отдельно для каждого конкретного случая.\n\nПриватные голосовые и создаваемые с ними текстовые каналы не модерируются, однако возможны исключения по запросу участников сервера или при явном нарушении правил Discord.\n\nПраво на публикацию своих личных данных (фото/посты/сообщения/etc) остается за Пользователем. Администрация сервера не несет ответственности за них.\n\nАдминистрация имеет право удалять сообщения участников, не соответствующие пунктам правил.\n\nАдминистрация оставляет за собой право применять меры пресечения к особо проблемным (имеющим большое количество предупреждений) участникам на свое усмотрение. При возникновении конфликтных или нарушающих правила ситуаций обращаться к администрации и модерации.\n\nЕсли вы считаете, что модератор превышает свои полномочия, обращаться к администрации.\n\nПо поводу разбана обращаться к администрации."
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(KisikMailing(bot))
