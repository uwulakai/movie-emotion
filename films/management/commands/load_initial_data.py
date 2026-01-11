from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from slugify import slugify

from emotions.models import Emotion
from films.models import Film, FilmEmotionRating
from users.models import UserProfile
from movie_emotion.config import env_settings

User = get_user_model()


class Command(BaseCommand):
    help = "Загрузка начальных данных для проекта"

    def handle(self, *args, **kwargs):
        self.stdout.write("Загрузка начальных данных...")

        # Создаем суперпользователя
        admin_username = env_settings.admin.ADMIN_USERNAME.get_secret_value()

        with transaction.atomic():
            # ОЧИСТКА СТАРЫХ ДАННЫХ (опционально, для разработки)
            self.stdout.write("Очистка старых данных...")
            FilmEmotionRating.objects.all().delete()
            Film.objects.all().delete()
            Emotion.objects.all().delete()
            UserProfile.objects.filter(user__is_superuser=False).delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write("Старые данные очищены")

            # Создаем суперпользователя
            if not User.objects.filter(username=admin_username).exists():
                admin_user = User.objects.create_superuser(
                    username=admin_username,
                    email=env_settings.admin.ADMIN_EMAIL.get_secret_value(),
                    password=env_settings.admin.ADMIN_PASSWORD.get_secret_value(),
                )
                self.stdout.write("Создан суперпользователь...")
            else:
                admin_user = User.objects.get(username=admin_username)
                self.stdout.write("Суперпользователь уже существует...")

            # Создаем профиль для админа
            try:
                profile = UserProfile.objects.get(user=admin_user)
                self.stdout.write("Профиль админа уже существует")
            except UserProfile.DoesNotExist:
                profile = UserProfile(
                    user=admin_user,
                    notification_frequency="daily",
                    email_notifications=True,
                )
                profile.save()
                self.stdout.write("Создан профиль для админа")

            # Создаем базовые эмоции
            emotions_data = [
                {
                    "name": "Радость",
                    "description": "Ощущение счастья, веселья и удовольствия",
                    "color": "#FFD166",
                    "icon": "fa-laugh",
                },
                {
                    "name": "Грусть",
                    "description": "Чувство печали, тоски и меланхолии",
                    "color": "#118AB2",
                    "icon": "fa-frown",
                },
                {
                    "name": "Страх",
                    "description": "Ощущение опасности, тревоги и ужаса",
                    "color": "#073B4C",
                    "icon": "fa-grimace",
                },
                {
                    "name": "Гнев",
                    "description": "Чувство злости, раздражения и ярости",
                    "color": "#FF6B6B",
                    "icon": "fa-angry",
                },
                {
                    "name": "Удивление",
                    "description": "Неожиданность, изумление и поразительность",
                    "color": "#4ECDC4",
                    "icon": "fa-flushed",
                },
                {
                    "name": "Любовь",
                    "description": "Чувство привязанности, нежности и страсти",
                    "color": "#EF476F",
                    "icon": "fa-heart",
                },
                {
                    "name": "Напряжение",
                    "description": "Ощущение тревожного ожидания и саспенса",
                    "color": "#7209B7",
                    "icon": "fa-grimace",
                },
                {
                    "name": "Вдохновение",
                    "description": "Чувство воодушевления и мотивации",
                    "color": "#06D6A0",
                    "icon": "fa-star",
                },
                {
                    "name": "Ностальгия",
                    "description": "Тоска по прошлому",
                    "color": "#FF9E6D",
                    "icon": "fa-history",
                },
                {
                    "name": "Сопереживание",
                    "description": "Чувство сочувствия к другим",
                    "color": "#A78BFA",
                    "icon": "fa-hands-helping",
                },
                {
                    "name": "Триумф",
                    "description": "Чувство победы и успеха",
                    "color": "#FFD700",
                    "icon": "fa-trophy",
                },
            ]

            created_emotions = 0
            for emo_data in emotions_data:
                name = emo_data["name"]
                slug = slugify(name)

                try:
                    emotion = Emotion.objects.get(name=name)
                    emotion.description = emo_data["description"]
                    emotion.color = emo_data["color"]
                    emotion.icon = emo_data["icon"]
                    if not emotion.slug or emotion.slug.strip() == "":
                        emotion.slug = slug
                    emotion.is_active = True
                    emotion.save()
                    self.stdout.write(f"Обновлена эмоция: {name}")
                except Emotion.DoesNotExist:
                    emotion = Emotion(
                        name=name,
                        slug=slug,
                        description=emo_data["description"],
                        color=emo_data["color"],
                        icon=emo_data["icon"],
                        is_active=True,
                    )
                    emotion.save()
                    created_emotions += 1
                    self.stdout.write(f"Создана эмоция: {name}")

            self.stdout.write(f"Создано {created_emotions} новых эмоций")

            films_data = [
                {
                    "title": "Интерстеллар",
                    "original_title": "Interstellar",
                    "year": 2014,
                    "duration": 169,
                    "country": "США",
                    "director": "Кристофер Нолан",
                    "genre": "sci_fi",
                    "description": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, коллектив исследователей и учёных отправляется сквозь червоточину (которая предположительно соединяет области пространства-времени через большое расстояние) в путешествие, чтобы превзойти прежние ограничения для космических путешествий человека и найти планету с подходящими для человечества условиями.",
                    "poster": "films/posters/interstellar.jpg",
                    "emotions_ratings": [
                        ("Вдохновение", 9),
                        ("Грусть", 7),
                        ("Удивление", 8),
                        ("Любовь", 8),
                        ("Напряжение", 7),
                    ],
                },
                {
                    "title": "1+1",
                    "original_title": "Intouchables",
                    "year": 2011,
                    "duration": 112,
                    "country": "Франция",
                    "director": "Оливье Накаш",
                    "genre": "drama",
                    "description": "Пострадав в результате несчастного случая, богатый аристократ Филипп нанимает в помощники человека, который менее всего подходит для этой работы, — молодого жителя предместья Дрисса, только что освободившегося из тюрьмы.",
                    "poster": "films/posters/intouchables.jpg",
                    "emotions_ratings": [
                        ("Радость", 9),
                        ("Вдохновение", 9),
                        ("Сопереживание", 8),
                        ("Любовь", 7),
                    ],
                },
                {
                    "title": "Побег из Шоушенка",
                    "original_title": "The Shawshank Redemption",
                    "year": 1994,
                    "duration": 142,
                    "country": "США",
                    "director": "Фрэнк Дарабонт",
                    "genre": "drama",
                    "poster": "films/posters/Shawshank.jpg",
                    "description": "Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Оказавшись в тюрьме под названием Шоушенк, он сталкивается с жестокостью и беззаконием, царящими по обе стороны решётки.",
                    "emotions_ratings": [
                        ("Вдохновение", 10),
                        ("Напряжение", 8),
                        ("Триумф", 9),
                        ("Грусть", 7),
                    ],
                },
                {
                    "title": "Джентльмены",
                    "original_title": "The Gentlemen",
                    "year": 2019,
                    "duration": 113,
                    "country": "США",
                    "director": "Гай Ричи",
                    "poster": "films/posters/gentlemen.jpg",
                    "genre": "thriller",
                    "description": "Талантливый выпускник Оксфорда, применив свой уникальный ум и невиданную дерзость, придумал нелегальную схему обогащения с использованием поместий обедневшей английской аристократии.",
                    "emotions_ratings": [
                        ("Удивление", 8),
                        ("Напряжение", 7),
                        ("Радость", 6),
                    ],
                },
                {
                    "title": "Зеленая миля",
                    "original_title": "The Green Mile",
                    "year": 1999,
                    "duration": 189,
                    "country": "США",
                    "director": "Фрэнк Дарабонт",
                    "poster": "films/posters/green_meel.jpeg",
                    "genre": "drama",
                    "description": "Пол Эджкомб — начальник блока смертников в тюрьме «Холодная гора», каждый из узников которого однажды проходит «зеленую милю» по пути к месту казни. Пол повидал много заключённых и надзирателей за время работы. Однако гигант Джон Коффи, обвинённый в страшном преступлении, стал одним из самых необычных обитателей блока.",
                    "emotions_ratings": [
                        ("Грусть", 9),
                        ("Сопереживание", 9),
                        ("Вдохновение", 8),
                        ("Напряжение", 7),
                    ],
                },
                {
                    "title": "Остров проклятых",
                    "original_title": "Shutter Island",
                    "year": 2009,
                    "duration": 138,
                    "country": "США",
                    "director": "Мартин Скорсезе",
                    "genre": "thriller",
                    "poster": "films/posters/shutter_island.jpg",
                    "description": "Два американских судебных пристава отправляются на один из островов в штате Массачусетс, чтобы расследовать исчезновение пациентки клиники для умалишенных преступников.",
                    "emotions_ratings": [
                        ("Страх", 8),
                        ("Напряжение", 9),
                        ("Удивление", 8),
                    ],
                },
                {
                    "title": "Форрест Гамп",
                    "original_title": "Forrest Gump",
                    "year": 1994,
                    "duration": 142,
                    "country": "США",
                    "director": "Роберт Земекис",
                    "poster": "films/posters/forrest_gump.jpg",
                    "genre": "drama",
                    "description": "От лица главного героя Форреста Гампа, слабоумного безобидного человека с благородным и открытым сердцем, рассказывается история его необыкновенной жизни.",
                    "emotions_ratings": [
                        ("Радость", 8),
                        ("Грусть", 7),
                        ("Вдохновение", 9),
                        ("Ностальгия", 8),
                    ],
                },
                {
                    "title": "Властелин колец: Возвращение короля",
                    "original_title": "The Lord of the Rings: The Return of the King",
                    "year": 2003,
                    "duration": 201,
                    "country": "Новая Зеландия",
                    "director": "Питер Джексон",
                    "poster": "films/posters/lord_of_the_rings_king.jpg",
                    "genre": "fantasy",
                    "description": "Повелитель сил Тьмы Саурон направляет свою бесчисленную армию под стены Минас-Тирита, крепости Последней Надежды. Он предвкушает близкую победу, но именно это мешает ему заметить две крохотные фигурки — хоббитов, приближающихся к Роковой Горе, где им предстоит уничтожить Кольцо Всевластья.",
                    "emotions_ratings": [
                        ("Триумф", 9),
                        ("Вдохновение", 9),
                        ("Напряжение", 8),
                        ("Грусть", 6),
                    ],
                },
                {
                    "title": "Бойцовский клуб",
                    "original_title": "Fight Club",
                    "year": 1999,
                    "duration": 139,
                    "country": "США",
                    "director": "Дэвид Финчер",
                    "poster": "films/posters/fight_club.jpg",
                    "genre": "thriller",
                    "description": "Сотрудник страховой компании страдает хронической бессонницей и отчаянно пытается вырваться из мучительно скучной жизни. Он посещает группы поддержки для тяжело больных, чтобы хоть как-то избавиться от отчаяния.",
                    "emotions_ratings": [
                        ("Гнев", 8),
                        ("Удивление", 9),
                        ("Напряжение", 8),
                    ],
                },
                {
                    "title": "Терминатор 2: Судный день",
                    "original_title": "Terminator 2: Judgment Day",
                    "year": 1991,
                    "duration": 137,
                    "country": "США",
                    "director": "Джеймс Кэмерон",
                    "genre": "sci_fi",
                    "poster": "films/posters/terminator_2_judge.jpg",
                    "description": "Прошло более десяти лет с тех пор, как киборг-терминатор из 2029 года пытался уничтожить Сару Коннор — женщину, чей будущий сын выиграет войну человечества против машин.",
                    "emotions_ratings": [
                        ("Напряжение", 9),
                        ("Вдохновение", 7),
                        ("Триумф", 8),
                    ],
                },
                {
                    "title": "Зеленая книга",
                    "original_title": "Green Book",
                    "year": 2018,
                    "duration": 130,
                    "country": "США",
                    "director": "Питер Фаррелли",
                    "genre": "drama",
                    "poster": "films/posters/green_book.jpg",
                    "description": "1960-е годы. После закрытия нью-йоркского ночного клуба на ремонт вышибала Тони по прозвищу Болтун ищет подработку на пару месяцев.",
                    "emotions_ratings": [
                        ("Радость", 8),
                        ("Сопереживание", 9),
                        ("Вдохновение", 8),
                    ],
                },
                {
                    "title": "Унесённые призраками",
                    "original_title": "Sen to Chihiro no kamikakushi",
                    "year": 2001,
                    "duration": 124,
                    "country": "Япония",
                    "director": "Хаяо Миядзаки",
                    "genre": "animation",
                    "poster": "films/posters/spirited_away.jpg",
                    "description": "10-летняя Тихиро переезжает в новый дом. Заблудившись по дороге, она оказывается в странном пустынном городе, где её родителей ждёт великолепный пир.",
                    "emotions_ratings": [
                        ("Удивление", 9),
                        ("Страх", 6),
                        ("Вдохновение", 8),
                    ],
                },
                {
                    "title": "Начало",
                    "original_title": "Inception",
                    "year": 2010,
                    "duration": 148,
                    "country": "США",
                    "director": "Кристофер Нолан",
                    "poster": "films/posters/beginning.jpg",
                    "genre": "sci_fi",
                    "description": "Кобб — талантливый вор, лучший из лучших в опасном искусстве извлечения: он крадет ценные секреты из глубин подсознания во время сна, когда человеческий разум наиболее уязвим.",
                    "emotions_ratings": [
                        ("Удивление", 10),
                        ("Напряжение", 9),
                        ("Вдохновение", 8),
                    ],
                },
                {
                    "title": "Властелин колец: Братство кольца",
                    "original_title": "The Lord of the Rings: The Fellowship of the Ring",
                    "year": 2001,
                    "duration": 178,
                    "country": "Новая Зеландия",
                    "director": "Питер Джексон",
                    "genre": "fantasy",
                    "poster": "films/posters/lord_of_the_rings_brotherhood.jpg",
                    "description": "Сказания о Средиземье — это хроника Великой войны за Кольцо, длившейся не одну тысячу лет. Тот, кто владел Кольцом, получал неограниченную власть.",
                    "emotions_ratings": [
                        ("Вдохновение", 9),
                        ("Напряжение", 8),
                        ("Триумф", 7),
                    ],
                },
                {
                    "title": "Криминальное чтиво",
                    "original_title": "Pulp Fiction",
                    "year": 1994,
                    "duration": 154,
                    "country": "США",
                    "director": "Квентин Тарантино",
                    "genre": "thriller",
                    "poster": "films/posters/pulp_fiction.jpg",
                    "description": "Двое бандитов Винсент Вега и Джулс Винфилд ведут философские беседы в перерывах между разборками и решением проблем с должниками криминального босса Марселласа Уоллеса.",
                    "emotions_ratings": [
                        ("Удивление", 9),
                        ("Напряжение", 8),
                        ("Гнев", 7),
                    ],
                },
                {
                    "title": "Властелин колец: Две крепости",
                    "original_title": "The Lord of the Rings: The Two Towers",
                    "year": 2002,
                    "duration": 179,
                    "country": "Новая Зеландия",
                    "director": "Питер Джексон",
                    "genre": "fantasy",
                    "poster": "films/posters/lord_of_the_rings_2_zamka.jpg",
                    "description": "Братство распалось, но Кольцо Всевластья должно быть уничтожено. Фродо и Сэм вынуждены довериться Голлуму, который берется провести их к вратам Мордора.",
                    "emotions_ratings": [
                        ("Напряжение", 9),
                        ("Вдохновение", 8),
                        ("Триумф", 7),
                    ],
                },
                {
                    "title": "Темный рыцарь",
                    "original_title": "The Dark Knight",
                    "year": 2008,
                    "duration": 152,
                    "country": "США",
                    "director": "Кристофер Нолан",
                    "genre": "action",
                    "poster": "films/posters/the_dark_knigth.jpg",
                    "description": "Бэтмен поднимает ставки в войне с криминалом. С помощью лейтенанта Джима Гордона и прокурора Харви Дента он намерен очистить улицы от преступности, отравляющей город.",
                    "emotions_ratings": [
                        ("Напряжение", 9),
                        ("Страх", 7),
                        ("Гнев", 8),
                    ],
                },
                {
                    "title": "Унесённые ветром",
                    "original_title": "Gone with the Wind",
                    "year": 1939,
                    "duration": 222,
                    "country": "США",
                    "director": "Виктор Флеминг",
                    "genre": "romance",
                    "poster": "films/posters/gone_with_the_wind.jpg",
                    "description": "История страстной, капризной, своенравной, но несгибаемой Скарлетт О'Хара, дочери богатого плантатора, пережившей войну между Севером и Югом и потерю всего, что она любила.",
                    "emotions_ratings": [
                        ("Любовь", 9),
                        ("Грусть", 8),
                        ("Ностальгия", 8),
                    ],
                },
                {
                    "title": "Волк с Уолл-стрит",
                    "original_title": "The Wolf of Wall Street",
                    "year": 2013,
                    "duration": 180,
                    "country": "США",
                    "director": "Мартин Скорсезе",
                    "poster": "films/posters/the_walf_of_wall_street.jpg",
                    "genre": "drama",
                    "description": "1987 год. Джордан Белфорт становится брокером в успешном инвестиционном банке. Вскоре банк закрывается после внезапного обвала индекса Доу-Джонса.",
                    "emotions_ratings": [
                        ("Радость", 8),
                        ("Удивление", 7),
                        ("Гнев", 6),
                    ],
                },
                {
                    "title": "Список Шиндлера",
                    "original_title": "Schindler's List",
                    "year": 1993,
                    "duration": 195,
                    "country": "США",
                    "director": "Стивен Спилберг",
                    "poster": "films/posters/shindler.jpg",
                    "genre": "drama",
                    "description": "История немецкого промышленника, спасшего жизни тысяч евреев во время Холокоста.",
                    "emotions_ratings": [
                        ("Грусть", 10),
                        ("Сопереживание", 9),
                        ("Вдохновение", 8),
                    ],
                },
                {
                    "title": "Леон",
                    "original_title": "Léon",
                    "year": 1994,
                    "duration": 133,
                    "country": "Франция",
                    "director": "Люк Бессон",
                    "poster": "films/posters/leon.jpg",
                    "genre": "action",
                    "description": "Профессиональный убийца Леон неожиданно для себя самого решает помочь 12-летней соседке Матильде, семью которой убили коррумпированные полицейские.",
                    "emotions_ratings": [
                        ("Сопереживание", 8),
                        ("Напряжение", 8),
                        ("Грусть", 7),
                    ],
                },
                {
                    "title": "Брат",
                    "year": 1997,
                    "duration": 96,
                    "country": "Россия",
                    "director": "Алексей Балабанов",
                    "genre": "drama",
                    "poster": "films/posters/Brat.jpg",
                    "description": "Демобилизовавшись, Данила Багров вернулся в родной городок. Но скучная жизнь российской провинции не устраивала его, и он решился податься в Петербург, где, по слухам, уже несколько лет процветает его старший брат.",
                    "emotions_ratings": [
                        ("Грусть", 7),
                        ("Гнев", 6),
                        ("Ностальгия", 8),
                    ],
                },
                {
                    "title": "Собачье сердце",
                    "year": 1988,
                    "duration": 136,
                    "country": "СССР",
                    "director": "Владимир Бортко",
                    "poster": "films/posters/sobachie.jpg",
                    "genre": "drama",
                    "description": "Москва, 1924 год. Выдающийся хирург профессор Преображенский проводит уникальный эксперимент по пересадке собаке гипофиза и семенных желез человека.",
                    "emotions_ratings": [
                        ("Удивление", 8),
                        ("Радость", 7),
                        ("Напряжение", 6),
                    ],
                },
                {
                    "title": "Достучаться до небес",
                    "original_title": "Knockin' on Heaven's Door",
                    "year": 1997,
                    "duration": 87,
                    "country": "Германия",
                    "director": "Томас Ян",
                    "poster": "films/posters/knockin.jpg",
                    "genre": "drama",
                    "description": "У двоих молодых людей, Мартина и Рудди, диагностируют неизлечимую болезнь, и жить им осталось совсем недолго. Вместо того чтобы дожидаться конца в больничной палате, они угоняют машину и отправляются к морю.",
                    "emotions_ratings": [
                        ("Радость", 8),
                        ("Грусть", 7),
                        ("Вдохновение", 8),
                    ],
                },
                {
                    "title": "Тайна Коко",
                    "original_title": "Coco",
                    "year": 2017,
                    "duration": 105,
                    "country": "США",
                    "director": "Ли Анкрич",
                    "poster": "films/posters/coco.jpg",
                    "genre": "animation",
                    "description": "12-летний Мигель мечтает стать музыкантом, как его кумир Эрнесто де ла Крус. Однако его семья запрещает музыку, потому что много лет назад его прапрадед оставил жену и дочь, чтобы отправиться на поиски славы.",
                    "emotions_ratings": [
                        ("Грусть", 7),
                        ("Радость", 8),
                        ("Любовь", 9),
                    ],
                },
                {
                    "title": "Крестный отец",
                    "original_title": "The Godfather",
                    "year": 1972,
                    "duration": 175,
                    "country": "США",
                    "director": "Фрэнсис Форд Коппола",
                    "genre": "drama",
                    "poster": "films/posters/godfather.jpg",
                    "description": "Криминальная сага, повествующая о нью-йоркской сицилийской мафиозной семье Корлеоне. Глава семьи, Дон Вито Корлеоне, выдаёт замуж свою дочь.",
                    "emotions_ratings": [
                        ("Напряжение", 9),
                        ("Гнев", 8),
                        ("Грусть", 7),
                    ],
                },
                {
                    "title": "Брат 2",
                    "year": 2000,
                    "duration": 127,
                    "country": "Россия",
                    "director": "Алексей Балабанов",
                    "genre": "action",
                    "poster": "films/posters/Brat2.jpg",
                    "description": "Данила Багров после смерти брата отправляется в США, чтобы разобраться с его убийцами.",
                    "emotions_ratings": [
                        ("Гнев", 7),
                        ("Триумф", 6),
                        ("Ностальгия", 8),
                    ],
                },
            ]

            created_films = 0
            for film_data in films_data:
                emotions_ratings = film_data.pop("emotions_ratings")

                try:
                    film = Film.objects.get(
                        title=film_data["title"], year=film_data["year"]
                    )
                    for key, value in film_data.items():
                        setattr(film, key, value)
                    film.save()
                    self.stdout.write(f"Обновлен фильм: {film_data['title']}")
                except Film.DoesNotExist:
                    film = Film(
                        title=film_data["title"],
                        original_title=film_data.get("original_title", ""),
                        year=film_data["year"],
                        duration=film_data["duration"],
                        country=film_data["country"],
                        director=film_data["director"],
                        genre=film_data["genre"],
                        description=film_data["description"],
                        created_by=profile,
                        is_published=True,
                    )
                    film.save()
                    created_films += 1
                    self.stdout.write(f"Создан фильм: {film_data['title']}")

                    if film_data.get("poster"):
                        film.poster = film_data["poster"]
                        film.save(update_fields=["poster"])
                        self.stdout.write(f"  ✓ Указан постер: {film_data['poster']}")

                    # Создаем оценки эмоций для фильма
                    for emotion_name, intensity in emotions_ratings:
                        try:
                            emotion = Emotion.objects.get(name=emotion_name)
                            rating = FilmEmotionRating(
                                film=film,
                                emotion=emotion,
                                intensity=intensity,
                                rated_by=profile,
                            )
                            rating.save()
                        except Emotion.DoesNotExist:
                            self.stdout.write(
                                f"Ошибка: эмоция '{emotion_name}' не найдена"
                            )

            self.stdout.write(f"Создано {created_films} новых фильмов")
            self.stdout.write(
                self.style.SUCCESS("✅ Начальные данные успешно загружены!")
            )
