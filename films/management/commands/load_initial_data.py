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

            # Создаем профиль для админа (ЯВНО через save)
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

            # Создаем базовые эмоции (ЯВНО через save)
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
            ]

            created_emotions = 0
            for emo_data in emotions_data:
                name = emo_data["name"]
                slug = slugify(name)

                try:
                    # Пытаемся найти существующую эмоцию
                    emotion = Emotion.objects.get(name=name)
                    # Обновляем поля
                    emotion.description = emo_data["description"]
                    emotion.color = emo_data["color"]
                    emotion.icon = emo_data["icon"]
                    # Проверяем и обновляем slug если нужно
                    if not emotion.slug or emotion.slug.strip() == "":
                        emotion.slug = slug
                    emotion.is_active = True
                    emotion.save()
                    self.stdout.write(f"Обновлена эмоция: {name}")
                except Emotion.DoesNotExist:
                    # Создаем новую эмоцию ЯВНО
                    emotion = Emotion(
                        name=name,
                        slug=slug,
                        description=emo_data["description"],
                        color=emo_data["color"],
                        icon=emo_data["icon"],
                        is_active=True,
                    )
                    emotion.save()  # Вызовет метод save() модели
                    created_emotions += 1
                    self.stdout.write(f"Создана эмоция: {name}")

            self.stdout.write(f"Создано {created_emotions} новых эмоций")

            # Создаем тестовые фильмы (ЯВНО через save)
            films_data = [
                {
                    "title": "Назад в будущее",
                    "year": 1985,
                    "duration": 116,
                    "country": "США",
                    "director": "Роберт Земекис",
                    "genre": "sci_fi",
                    "description": "Подросток Марти с помощью машины времени попадает из 80-х в 50-е годы, где встречает своих будущих родителей.",
                    "emotions_ratings": [
                        ("Радость", 9),
                        ("Удивление", 8),
                        ("Вдохновение", 7),
                    ],
                },
                {
                    "title": "Крестный отец",
                    "year": 1972,
                    "duration": 175,
                    "country": "США",
                    "director": "Фрэнсис Форд Коппола",
                    "genre": "drama",
                    "description": "Эпическая сага о сицилийской мафиозной семье Корлеоне и их борьбе за власть.",
                    "emotions_ratings": [
                        ("Напряжение", 9),
                        ("Гнев", 8),
                        ("Грусть", 7),
                    ],
                },
                {
                    "title": "Побег из Шоушенка",
                    "year": 1994,
                    "duration": 142,
                    "country": "США",
                    "director": "Фрэнк Дарабонт",
                    "genre": "drama",
                    "description": "Бухгалтер Энди Дюфрейн оказывается в тюрьме пожизненно и планирует побег.",
                    "emotions_ratings": [
                        ("Вдохновение", 10),
                        ("Напряжение", 8),
                        ("Грусть", 6),
                        ("Радость", 7),
                    ],
                },
            ]

            created_films = 0
            for film_data in films_data:
                emotions_ratings = film_data.pop("emotions_ratings")

                try:
                    # Ищем существующий фильм
                    film = Film.objects.get(
                        title=film_data["title"], year=film_data["year"]
                    )
                    # Обновляем поля
                    for key, value in film_data.items():
                        setattr(film, key, value)
                    film.save()
                    self.stdout.write(f"Обновлен фильм: {film_data['title']}")
                except Film.DoesNotExist:
                    # Создаем новый фильм ЯВНО
                    film = Film(
                        title=film_data["title"],
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

                    # Создаем оценки эмоций для фильма
                    for emotion_name, intensity in emotions_ratings:
                        try:
                            emotion = Emotion.objects.get(name=emotion_name)
                            rating = FilmEmotionRating(
                                film=film,
                                emotion=emotion,
                                intensity=intensity,
                                rated_by=profile,  # Используем User, а не UserProfile
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
