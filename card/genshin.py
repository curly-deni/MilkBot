from easy_pil import Editor, Canvas, load_image_async
from nextcord import File, Member
from PIL import ImageFont, Image, ImageColor, ImageDraw
import numpy as np
import textwrap

characters_info = {
    "Ёимия": {
        "оружие": "лук",
        "регион": "инадзума",
        "описание": """Выдающийся мастер фейерверков и владелица «Фейерверков Наганохары». Также известна как «Королева праздника лета». 
Девушка с пламенным характером. Сплетение детской невинности и одержимости мастера проявляет себя чудесной огненной реакцией.""",
    },
    "Альбедо": {
        "оружие": "меч",
        "регион": "мондштадт",
        "описание": """Альбедо - алхимик в Мондштадте на службе у Ордо Фавониус. 
«Гений», «Принц мела», «Старший исследователь»... Титулы и слава не значат для него ничего, когда кругом столько объектов для исследований. 
Ему не нужны ни богатства, ни связи. Его стремления подчинены одной цели - заполучить сокровенные знания всех поколений учёных.""",
    },
    "Аяка": {
        "оружие": "меч",
        "регион": "инадзума",
        "описание": """Дочь клана Камисато комиссии Ясиро. Благородна, изящна, мудра и сильна. 
Всегда честна и учтива. Обожаемая народом Инадзумы, она заслужила прозвище «Сирасаги Химэгими».""",
    },
    "Барбара": {
        "оружие": "катализатор",
        "регион": "мондштадт",
        "описание": """Пастор Ордо Фавониус, а также сияющая звёздочка, любимая всеми в Мондштадте. 
Жители Мондштадта больше привыкли к бардам, нежели к звёздочкам, но они всё равно без ума от Барбары. 
«Я в долгу перед духом свободы этого города». — Барбара, о своей популярности.""",
    },
    "Беннет": {
        "оружие": "меч",
        "регион": "мондштадт",
        "описание": """Молодой искатель приключений из Мондштата, известный своим чудовищным невезением. 
Он остался единственным членом группы искателей приключений, известной как «отряд Бенни». Остальные участники покинули отряд после череды неудач. Отряд находится на грани расформирования. 
Чтобы не ранить чувствительную душу юноши, Катерина сохраняет записи об «отряде Бенни» в книгах гильдии искателей приключений и скрывает от Беннета, что он последний член своего отряда.""",
    },
    "Бэй Доу": {
        "оружие": "двуручный меч",
        "регион": "ли юэ",
        "описание": """Капитан флота Южного Креста, пользующийся у жителей Ли Юэ всеобщим уважением. 
Рассказывают, что её мощь способная раскалывать горы и раздвигать моря. Другие говорят, что она одним взмахом меча призывает гром и молнию. А третьи утверждают, что даже самые кошмарные морские чудовища боятся Бэй Доу. 
Те, кто не знаком с Бэй Доу лично, примут эти истории за пьяный вымысел завсегдатаев таверны. Но те, кому посчастливилось сходить с Бэй Доу в плавание, в один голос скажут: 
«Если вдруг на наше судно нападёт ужасное чудовище из морских пучин, будьте уверены, наш капитан разрубит его пополам!»""",
    },
    "Венти": {
        "оружие": "лук",
        "регион": "мондштадт",
        "описание": """Неведомые ветра привели барда в наши земли. 
Порой его песни стары как свет, а иной раз он играет современные произведения. 
Любит яблоки и живую атмосферу, не любит сыры и всё липкое. 
Когда он управляет ветрами, его Анемо сила проявляется в виде перьев. 
Венти привлекает их лёгкость и беспечность.""",
    },
    "Гань Юй": {
        "оружие": "лук",
        "регион": "ли юэ",
        "описание": """Главный секретарь Цисин. В её жилах течёт кровь божественного зверя. 
Гань Юй от природы спокойна и грациозна, но мягкий характер мифического зверя цилиня решительности и трудолюбию нисколько не противоречит. 
В конце концов, Гань Юй убеждена, что её работа - следовать контракту с Властелином Камня, то есть стремиться к благополучию всех живых существ в Ли Юэ.""",
    },
    "Горо": {
        "оружие": "лук",
        "регион": "инадзума",
        "описание": """Генерал Ватацуми. Заслужив уважение и непререкаемый авторитет, он остаётся скромным лидером. 
Это генерал, которому безгранично доверяют подчинённые, тот, с кем можно без стыда поделиться чувствами.""",
    },
    "Джинн": {
        "оружие": "меч",
        "регион": "мондштадт",
        "описание": """Будучи действующим командиром Ордо Фавониус, Джинн всегда предана своему долгу поддерживать мир в Мондштадте. 
Конечно, она не самый одарённый боец, но её усердие и добросовестность сделали её одной из самых надёжных рыцарей ордена. 
Джинн приняла меры задолго до нападения Ужаса Бури на Мондштадт. 
Она поклялась охранять этот город своей жизнью.""",
    },
    "Дилюк": {
        "оружие": "двуручный меч",
        "регион": "мондштадт",
        "описание": """Будучи самым богатым холостяком Мондштадта, Дилюк всегда показывает себя только с самой благородной стороны. 
Однако под этой маской скрывается воин с закалённой в пламени железной волей, который не остановится ни перед чем ради защиты Мондштадта. 
Не стоит надеяться на пощаду, он будет безжалостен до самого конца.""",
    },
    "Диона": {
        "оружие": "лук",
        "регион": "мондштадт",
        "описание": """Невероятно популярный бармен таверны «Кошкин хвост», восходящая звезда винной индустрии Мондштадта и величайший бунтарь против традиционных устоев. 
Обладательница кошачьего хвоста и милых ушек родилась в Спрингвейле. Любой коктейль, который она готовит собственноручно, выходит божественно вкусным. 
Но, учитывая отвращение Дионы к алкоголю, талант её - благословение или проклятие?""",
    },
    "Итто": {
        "оружие": "двуручный меч",
        "регион": "инадзума",
        "описание": """Потомок óни бесстрашного духа и благородного сердца. 
Стремителен, как ветер, и ослепителен, словно молния.""",
    },
    "Кадзуха": {
        "оружие": "меч",
        "регион": "инадзума",
        "описание": """Странствующий самурай из Инадзумы, скромный и мягкий. 
За молодой и беззаботной внешностью скрывается полное невзгод прошлое. На первый взгляд беспечный юноша строго следует собственному кодексу поведения.""",
    },
    "Кли": {
        "оружие": "катализатор",
        "регион": "мондштадт",
        "описание": """Рыцарь Искорка из Ордо Фавониус! Повсюду за ней следуют вспышки и взрывы! 
Но весь огонь затухает, как только появляется Джинн. 
Одиночное заключение даёт время подумать над новыми формулами пороха... 
Но всё равно свобода – лучше!""",
    },
    "Кокоми": {
        "оружие": "катализатор",
        "регион": "инадзума",
        "описание": """Кокоми - Божественная Жрица и верховный глава Ватацуми. 
Она непревзойдённый мастер военного искусства, гениальный тактик. Она также обладает выдающимся талантом в области внутренней политики и дипломатии. 
Но у этого непостижимого лидера есть неизвестная сторона...""",
    },
    "Кэ Цин": {
        "оружие": "меч",
        "регион": "ли юэ",
        "описание": """Юй Хэн группировки Цисин в Ли Юэ. У неё есть что сказать против «Властелина камня, правящего Ли Юэ лишь словом», но, оказывается, боги любят таких скептиков, как она. 
Она твёрдо верит: судьбу человечества должно вершить само человечество, ведь человек лучше знает, что нужно его роду. 
Чтобы доказать это, она работает так усердно, как никто другой.""",
    },
    "Кэйа": {
        "оружие": "меч",
        "регион": "мондштадт",
        "описание": """В Ордо Фавониус Кэйа является доверенным помощником действующего командира Джинн. Он может справиться с любой неразрешимой, на первый взгляд, проблемой. 
Все в Мондштадте любят Кэйю, но никто не знает, в чём секрет этого остроумного и очаровательного рыцаря...""",
    },
    "Лиза": {
        "оружие": "катализатор",
        "регион": "мондштадт",
        "описание": """Она - интеллектуальная ведьма, которая никогда не может достаточно вздремнуть. 
Будучи библиотекарем Ордо Фавониус, Лиза всегда знает, что нужно делать, чтобы тебя перестали беспокоить. 
Как бы она ни любила спать, Лиза всегда находит время, чтобы содержать всё в спокойном духовном порядке.""",
    },
    "Мона": {
        "оружие": "катализатор",
        "регион": "мондштадт",
        "описание": """Таинственный молодой астролог, которая представляется как «великий астролог Мона», и на самом деле достойна этого звания. Эрудирована и горделива. 
Хотя у неё вечно нет денег и она живёт впроголодь, она решительно отказывается использовать астрологию для заработка... И из-за этой решительности постоянно беспокоится о завтрашнем дне.""",
    },
    "Нин Гуан": {
        "оружие": "катализатор",
        "регион": "ли юэ",
        "описание": """Самая влиятельная женщина Ли Юэ живёт в летающем дворце, а в уголках её губ всегда прячется загадочная улыбка. 
Как часть группировки Ли Юэ Цисин, она символизирует не только власть и закон, но также богатство и разум.""",
    },
    "Ноэлль": {
        "оружие": "двуручный меч",
        "регион": "мондштадт",
        "описание": """Как и многие молодые люди в Мондштадте, Ноэлль мечтает однажды облачиться в доспехи рыцарей Ордо Фавониус. 
Она не обескуражена отсутствием опыта и, как горничная Ордо Фавониус, она не упускает возвожности изучить все аспекты рыцарства.""",
    },
    "Путешественник": {
        "оружие": "меч",
        "регион": "тейват",
        "описание": """Путешественник из другого мира, разлученный со своей сестрой. Он отправляется в долгое путешествие, чтобы найти всех семерых Архонтов и вернуть родного человека.""",
    },
    "Райдэн": {
        "оружие": "копьё",
        "регион": "инадзума",
        "описание": """Сёгун Райдэн - самое могущественное и страшное воплощение Электро в этом мире, верховный правитель сёгуната Инадзумы. 
Обладая мощью грома и молний, она следует одиноким путём, носящим имя вечности.""",
    },
    "Розария": {
        "оружие": "копьё",
        "регион": "мондштадт",
        "описание": """Розария - сестра церкви Фавония в Мондштадте. 
Кроме одеяния Розарии ничто не напоминает о её принадлежности церкви. Холодна и остра, как клинок. 
Уходит, когда ей заблагорассудится, не сказав ни слова. У неё важная миссия, вот только никто не понимает какая...""",
    },
    "Рэйзор": {
        "оружие": "двуручный меч",
        "регион": "мондштадт",
        "описание": """В Мондштадте говорят, что он сирота, которого воспитали волки. Ещё говорят, что он волчий дух в человеческом обличье.
Этот мальчик комфортнее всего чувствует себя в дикой природе, сражаясь громом и когтями.
По сей день в лесной чаще мальчик охотится со стаей волков, полагаясь только на свои животные инстинкты.""",
    },
    "Сара": {
        "оружие": "лук",
        "регион": "инадзума",
        "описание": """Генерал комиссии Тэнрё. Смелая и стремительная, как ветер, девушка, которая всегда держит своё слово. 
Прозванная «Верной Божеству», она посвятила жизнь сёгуну Райдэн. 
Преследуемая сёгуном вечность и есть вера, за которую она готова сражаться.""",
    },
    "Сахароза": {
        "оружие": "катализатор",
        "регион": "мондштадт",
        "описание": """Алхимик с ненасытным любопытством к миру и всему, что в нём находится. Сахароза занимает должность помощника Альбедо в Ордо Фавониус. Её область исследования - биоалхимия. 
Она стремится обогатить мир, трансформируя живые существа силой алхимии. 
Конечно, результаты её исследований зачастую оказываются скорее странными, чем удивительными, но тем не менее она внесла огромный вклад в исследование биоалхимии.""",
    },
    "Саю": {
        "оружие": "двуручный меч",
        "регион": "инадзума",
        "описание": """Саю - особый ниндзя из тайной организации Сиюмацу-бан, которая изо всех сил старается побольше спать, чтобы вырасти. 
Она научилась мастерски скрываться и убегать от опасности, чтобы было больше возможностей поспать. 
Такие удивительные методы могут принести неожиданный результат.""",
    },
    "Син Цю": {
        "оружие": "меч",
        "регион": "ли юэ",
        "описание": """Син Цю - второй сын главы торговой гильдии Фэй Юнь. Все знают его как прилежного и хорошо воспитанного юношу. 
Но мало кому известна другая сторона его личности. Дерзкая, безбашенная и жаждущая приключений.""",
    },
    "Синь Янь": {
        "оружие": "двуручный меч",
        "регион": "ли юэ",
        "описание": """В гавани Ли Юэ зарождается новое искусство, и Синь Янь - исполнитель, сражающийся в первых рядах на этом фронте. 
С помощью музыки и пылких песен она борется с предвзятостью и жаждет разбудить погрязшие в рутине души этого мира. 
Если у вас будет возможность посетить её концерт, ни в коем случае не упускайте его.""",
    },
    "Сян Лин": {
        "оружие": "копьё",
        "регион": "ли юэ",
        "описание": """Новый шеф-повар ресторана «Вань Минь». Если её нет у печи, значит она разносит блюда в главном зале. Лучше всего ее мастерство проявляется в острых закусках. 
Несмотря на юный возраст, Сян Лин уже стала мастером поваром, а ее кулинарные шедевры высоко ценятся жителями горы Тигра. 
Если вам повезёт и Сян Лин пригласит вас посетить её ресторан, идите не сомневаясь. Удовольствие для вашего желудка гарантировано.""",
    },
    "Сяо": {
        "оружие": "копьё",
        "регион": "ли юэ",
        "описание": """Один из Адептов, защищающих Ли Юэ. Его также называют Защитником Якса. 
Хотя Сяо молодо выглядит, он упоминается в легендах, которым уже больше тысячи лет! 
Его любимое лакомство – миндальный тофу с постоялого двора «Ван Шу». 
Дело в том, что вкус миндального тофу напоминает Сяо о снах, которые он когда-то поглощал.""",
    },
    "Тарталья": {
        "оружие": "лук",
        "регион": "снежная",
        "описание": """Познакомьтесь с Тартальей, непредсказуемым воином из Снежной! 
Не питайте иллюзий, что вы понимаете его подлинные намерения. Не забывайте, что за этой невинной внешностью скрывается безжалостное орудие для убийства.""",
    },
    "Тома": {
        "оружие": "копьё",
        "регион": "инадзума",
        "описание": """Управляющий клана Камисато комиссии Ясиро. Известный в Инадзуме «местный авторитет». 
Дружелюбный и общительный, Тома легко вписывается в окружение, где бы он ни находился. 
На первый взгляд он кажется легкомысленным человеком, но на самом деле он очень ответственный. Он бывает необычайно серьёзным, будь то в работе или в общении.""",
    },
    "Фишль": {
        "оружие": "лук",
        "регион": "мондштадт",
        "описание": """Таинственная девушка, называющая себя «Принцессой осуждения». Она путешествует в сопровождении ворона по имени Оз. 
В текущий момент является агентом гильдии искателей приключений. 
Благодаря своим уникальным способностям, эксцентричному характеру и (она сама это не признаёт) трудолюбию, Фишль стала восходящей звездой гильдии, заслужив всеобщее признание.""",
    },
    "Ху Тао": {
        "оружие": "копьё",
        "регион": "ли юэ",
        "описание": """Ху Тао - хозяйка ритуального бюро «Ваншэн» в семьдесят седьмом поколении. Важная фигура в похоронном деле Ли Юэ. 
Изо всех сил она устраивает лучшие похороны для людей и оберегает границу между жизнью и смертью. 
А ещё она чудесный стихоплёт, чьи «шедевры» из уст в уста бродят по Ли Юэ.""",
    },
    "Ци Ци": {
        "оружие": "меч",
        "регион": "ли юэ",
        "описание": """Ученица и сборщица трав из хижины Бубу. 
Случайно оказавшись в сражении между Адептами и демонами, обрела бессмертное тело. Перед тем, как что-нибудь сделать, должна сама себе отдать приказ. 
С памятью у Ци Ци беда. Чтобы она не помешала нормальному ходу жизни, Ци Ци постоянно носит с собой блокнот, в котором ведёт записи на все случаи жизни. 
Но в самые неудачные дни она забывает заглянуть даже в свои записи...""",
    },
    "Чжун Ли": {
        "оружие": "копьё",
        "регион": "ли юэ",
        "описание": """Загадочный консультант ритуального бюро «Ваншэн». 
Красив, обладает изящными манерами и выдающимся интеллектом. 
Происхождение Чжун Ли неизвестно, но он отлично знаком с правилами этикета и хорошими манерами. 
В ритуальном бюро «Ваншэн» он занимается проведением церемоний любого рода.""",
    },
    "Чун Юнь": {
        "оружие": "двуручный меч",
        "регион": "ли юэ",
        "описание": """Обосновавшись в Ли Юэ, маг Чун Юнь принялся повсюду искоренять зло. 
Удивительный талант этого наследника знаменитого рода уничтожителей зла поражал всех с самого детства. 
Но его мастерство — вовсе не плод поучений мудрых наставников или чтения пыльных фолиантов. 
То, что зовётся «Энергией солнца», у него в крови.""",
    },
    "Шэнь Хэ": {
        "оружие": "копьё",
        "регион": "ли юэ",
        "описание": """И пусть родилась Шэнь Хэ в мире людей, она стала ученицей Адептов. Выросшая в горах вдали от Ли Юэ, красными верёвками связала она свою душу, совершенствуя тело и разум. 
Под изящным обличьем Адепта кроются тайны.""",
    },
    "Элой": {
        "оружие": "лук",
        "регион": "hzd",
        "описание": """В прошлом изгой, а теперь охотник с непревзойденным чутьем. Её лук всегда наготове раде правого дела.""",
    },
    "Эмбер": {
        "оружие": "лук",
        "регион": "мондштадт",
        "описание": """Наивная и задорная девушка, скаут Ордо Фавониус. 
Благодаря отличному владению планером она стала трехкратным чемпионом Мондштадта по полётам. 
Будучи восходящей звездой Ордо Фавониус, Эмбер всегда готова к задачам любой сложности.""",
    },
    "Эола": {
        "оружие": "двуручный меч",
        "регион": "мондштадт",
        "описание": """Эола - мятежный потомок аристократии, Рыцарь Морская пена, всегда на поле боя. 
Родившись в старом аристократическом клане и неся в себе родословную преступников, человек нуждается в уникальном подходе к миру, чтобы спокойно ориентироваться среди предрассудков. Конечно, это не помешало Эоле разорвать связь со своим кланом. Выдающийся Рыцарь Морская пена, она охотится на врагов Мондштадта в дикой природе, чтобы воплотить свою уникальную «месть».""",
    },
    "Юнь Цзинь": {
        "оружие": "копьё",
        "регион": "ли юэ",
        "описание": """Нынешняя руководительница оперной труппы Юнь Хань, прославленная оперная певица Ли Юэ, которая искусна как в написании пьес, так и в пении. Её изысканный и нежный стиль, единственный в своем роде, происходит из самых глубин её души.""",
    },
    "Янь Фэй": {
        "оружие": "катализатор",
        "регион": "ли юэ",
        "описание": """Янь Фэй - первоклассный консультант по юридическим вопросам, в чьих жилах течёт кровь Божественного зверя. 
Она нашла золотую середину между правилами и гибкостью. Своим уникальным статусом эксперта по правовым вопросам и профессиональным опытом она поддерживает равновесие контрактов в Ли Юэ.""",
    },
}


def hex_to_rgb(hex):
    rgb = []
    for i in (0, 2, 4):
        decimal = int(hex[i : i + 2], 16)
        rgb.append(decimal)

    return tuple(rgb)


class rank:
    def __init__(self):
        self.name: str = None
        self.avatar: str = None
        self.color: str = "white"
        self.namecolor: str = "black"
        self.statcolor: str = "red"
        self.path: str = "https://raw.githubusercontent.com/I-dan-mi-I/images/main/banners/%D0%BD%D0%BE%D0%B2%D1%8B%D0%B9%20%D0%BC%D0%B8%D1%80.png"

        self.ar: str = None
        self.genshinname: str = None

        # genshin
        self.achievements: str = None
        self.active_days: str = None
        self.characters: str = None
        self.spiral_abyss: str = None
        self.anemoculi: str = None
        self.geoculi: str = None
        self.electroculi: str = None
        self.common_chests: str = None
        self.exquisite_chests: str = None
        self.precious_chests: str = None
        self.luxurious_chests: str = None
        self.unlocked_waypoints: str = None
        self.unlocked_domains: str = None

    async def create(self):
        if isinstance(ImageColor.colormap[self.color], str):
            x = ImageColor.colormap[self.color].lstrip(("#"))
            rgbs = hex_to_rgb(x)
        else:
            rgbs = ImageColor.colormap[self.color]

        im = Image.open("./card/layout/genshin/rank.png")
        im = im.convert("RGBA")

        data = np.array(im)  # "data" is a height x width x 4 numpy array
        red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

        # Replace white with red... (leaves alpha values alone...)
        black_areas = (red == 0) & (blue == 0) & (green == 0)
        data[..., :-1][black_areas.T] = (
            int(rgbs[0]),
            int(rgbs[1]),
            int(rgbs[2]),
        )  # Transpose back needed

        im2 = Image.fromarray(data)

        # background = await load_image_async(str(self.path))
        background = Editor(
            Image.open(
                self.path.replace(
                    r"https://raw.githubusercontent.com/I-dan-mi-I/images/main/banners/",
                    "./card/layout/banners/",
                )
            )
        ).resize((3360, 1600))
        if self.avatar != None:
            profile = await load_image_async(str(self.avatar))
            profile = Editor(profile).resize((719, 719)).circle_image()
            background.paste(profile.image, (50, 50))

        layout = Editor(im2).resize((3360, 1600))
        background.paste(layout.image, (0, 0))

        font240 = ImageFont.truetype("./card/fonts/plainoit.ttf", 240, encoding="unic")
        font180 = ImageFont.truetype("./card/fonts/plainoit.ttf", 180, encoding="unic")
        font130 = ImageFont.truetype("./card/fonts/plainoit.ttf", 130, encoding="unic")

        background.text((816, 179), str(self.name), font=font240, color=self.namecolor)
        background.text(
            (816, 401), str(self.genshinname), font=font180, color=self.namecolor
        )
        background.text((3142, 40), str(self.ar), font=font180, color=self.namecolor)

        background.rectangle((816, 381), width=1000, height=4, fill="violet")

        background.text(
            (969, 615),
            self.active_days,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (1410, 615),
            self.achievements,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (1906, 615),
            self.characters,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (2322, 615),
            self.unlocked_waypoints,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (2804, 615),
            self.anemoculi,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (969, 934),
            self.geoculi,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (1410, 934),
            self.electroculi,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (1906, 934),
            self.unlocked_domains,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (2322, 934),
            self.spiral_abyss,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (2804, 934),
            self.luxurious_chests,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (969, 1245),
            self.precious_chests,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (1410, 1245),
            self.exquisite_chests,
            font=font130,
            color=self.statcolor,
        )

        background.text(
            (1880, 1245),
            self.common_chests,
            font=font130,
            color=self.statcolor,
        )

        # img = Image.open(background.image_bytes)
        # img.save('gen.png')

        file = File(fp=background.image_bytes, filename="card.png")
        return file


class board:
    def __init__(self, characters):
        self.avatar: str = None
        self.color: str = "black"
        self.namecolor: str = "black"
        self.statcolor: str = "black"
        self.path: str = "https://raw.githubusercontent.com/I-dan-mi-I/images/main/banners/%D0%BD%D0%BE%D0%B2%D1%8B%D0%B9%20%D0%BC%D0%B8%D1%80.png"

        self.ar: str = None
        self.genshinname: str = None

        self.characters = characters
        self.characters_card = []

    async def create(self):
        for x in self.characters:
            try:
                card = board_character(x)
                card.color = self.color
                card.statcolor = self.statcolor
                self.characters_card.append(await card.create())
            except:
                pass

        if isinstance(ImageColor.colormap[self.color], str):
            x = ImageColor.colormap[self.color].lstrip(("#"))
            rgbs = hex_to_rgb(x)
        else:
            rgbs = ImageColor.colormap[self.color]

        im = Image.open("./card/layout/genshin/board.png")
        im = im.convert("RGBA")

        data = np.array(im)  # "data" is a height x width x 4 numpy array
        red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

        # Replace white with red... (leaves alpha values alone...)
        black_areas = (red == 0) & (blue == 0) & (green == 0)
        data[..., :-1][black_areas.T] = (
            int(rgbs[0]),
            int(rgbs[1]),
            int(rgbs[2]),
        )  # Transpose back needed

        im2 = Image.fromarray(data)
        layout = Editor(im2).resize((3360, 1600))

        background = await load_image_async(str(self.path))
        background = Editor(background).resize((3360, 1600))
        if self.avatar != None:
            profile = await load_image_async(str(self.avatar))
            profile = Editor(profile).resize((180, 180)).circle_image()
            background.paste(profile.image, (50, 50))

        background.paste(layout.image, (0, 0))

        font180 = ImageFont.truetype("./card/fonts/plainoit.ttf", 180, encoding="unic")

        background.text(
            (250, 60), str(self.genshinname), font=font180, color=self.namecolor
        )
        background.text((3142, 40), str(self.ar), font=font180, color=self.namecolor)

        for count in range(len(self.characters_card)):
            if count == 0 or count == 4:
                width = 251
            elif count == 1 or count == 5:
                width = 1000
            elif count == 2 or count == 6:
                width = 1747
            elif count == 3 or count == 7:
                width = 2497
            if count < 4:
                height = 217
            else:
                height = 923

            card = Editor(self.characters_card[count])
            background.paste(card.image, (width, height))

            count += 1

        file = File(fp=background.image_bytes, filename="card.png")
        return file


class board_character:
    def __init__(self, character):
        self.character = character
        self.color: str = "black"
        self.statcolor: str = "black"

        if character != None:
            self.name = character["name"]
            self.avatar = character["icon"]
            self.region = characters_info[f"{self.name}"]["регион"]
            self.weapon = characters_info[f"{self.name}"]["оружие"]
            self.about = characters_info[f"{self.name}"]["описание"]
            self.rarity = character["rarity"]
            self.element = character["element"]
            self.level = character["level"]
            self.friendship = character["friendship"]
        else:
            self.name = None
            self.avatar = None
            self.region = None
            self.weapon = None
            self.about = None
            self.rarity = None
            self.element = None
            self.level = None
            self.friendship = None

    async def create(self):
        if isinstance(ImageColor.colormap[self.statcolor], str):
            x = ImageColor.colormap[self.statcolor].lstrip(("#"))
            rgbs = hex_to_rgb(x)
        else:
            rgbs = ImageColor.colormap[self.color]

        im = Image.open("./card/layout/genshin/board_character.png")
        im = im.convert("RGBA")

        data = np.array(im)  # "data" is a height x width x 4 numpy array
        red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

        # Replace white with red... (leaves alpha values alone...)
        black_areas = (red == 0) & (blue == 0) & (green == 0)
        data[..., :-1][black_areas.T] = (
            int(rgbs[0]),
            int(rgbs[1]),
            int(rgbs[2]),
        )  # Transpose back needed

        im2 = Image.fromarray(data)

        background = Canvas(width=646, height=621)
        background = Editor(background).resize((646, 621))

        if self.avatar != None:
            profile = await load_image_async(str(self.avatar))
            profile = Editor(profile).resize((273, 267))
            background.paste(profile.image, (19, 25))

        layout = Editor(im2)
        background.paste(layout.image, (0, 0))

        img = Image.open(background.image_bytes)

        d = ImageDraw.Draw(img)

        font56 = ImageFont.truetype("./card/fonts/plainoit.ttf", 56, encoding="unic")
        if self.name != "Путешественник":
            names = [self.name, "⠀" * 27]
            name = ("\n").join(names)
            d.multiline_text(
                (292, 25), name, font=font56, fill=self.color, align="center"
            )
        else:
            font54 = ImageFont.truetype(
                "./card/fonts/plainoit.ttf", 50, encoding="unic"
            )
            names = [self.name, "⠀" * 22]
            name = ("\n").join(names)
            d.multiline_text(
                (292, 25), name, font=font54, fill=self.color, align="center"
            )

        font20 = ImageFont.truetype("./card/fonts/plainoit.ttf", 28, encoding="unic")

        lines = textwrap.wrap(self.about, width=47)
        lines.append("⠀" * 101)
        # lines.append('а' * 47)
        line = ("\n").join(lines)

        d.multiline_text((19, 298), line, font=font20, fill=self.color, align="center")
        background = Editor(img)

        element = Editor(
            Image.open(f"./card/layout/genshin/элементы/{self.element.lower()}.png")
        )
        background.paste(element.image, (0, 0))

        weapon = Editor(
            Image.open(f"./card/layout/genshin/оружие/{self.weapon.lower()}.png")
        )
        background.paste(weapon.image, (0, 0))

        region = Editor(
            Image.open(f"./card/layout/genshin/страны/{self.region.lower()}.png")
        )
        background.paste(region.image, (0, 0))

        rarity = Editor(
            Image.open(f"./card/layout/genshin/звезды/{str(self.rarity).lower()}.png")
        )
        background.paste(rarity.image, (0, 0))

        if self.level < 10:
            background.text((156, 520), str(self.level), font=font56, color=self.color)
        else:
            background.text((142, 527), str(self.level), font=font56, color=self.color)

        if self.friendship < 10:
            background.text(
                (458, 527), str(self.friendship), font=font56, color=self.color
            )
        else:
            background.text(
                (451, 527), str(self.friendship), font=font56, color=self.color
            )
        return background.image
