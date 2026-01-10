import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from emotions.models import Emotion
from users.models import UserProfile


def film_poster_path(instance, filename):
    """Генерация пути для сохранения постера"""
    ext = filename.split(".")[-1]
    filename = f"{instance.id}_poster.{ext}"
    return os.path.join("films/posters/", filename)


class Film(models.Model):
    """Модель фильма"""

    GENRE_CHOICES = [
        ("action", "Боевик"),
        ("comedy", "Комедия"),
        ("drama", "Драма"),
        ("horror", "Ужасы"),
        ("sci_fi", "Научная фантастика"),
        ("romance", "Мелодрама"),
        ("thriller", "Триллер"),
        ("documentary", "Документальный"),
        ("animation", "Анимация"),
        ("fantasy", "Фэнтези"),
    ]

    title = models.CharField(max_length=200, verbose_name="Название фильма")
    original_title = models.CharField(
        max_length=200, blank=True, verbose_name="Оригинальное название"
    )
    description = models.TextField(verbose_name="Описание")
    year = models.IntegerField(
        verbose_name="Год выпуска",
        validators=[
            MinValueValidator(1895),  # Первый фильм
            MaxValueValidator(2030),
        ],
    )
    duration = models.IntegerField(
        verbose_name="Продолжительность (мин)", validators=[MinValueValidator(1)]
    )
    poster = models.ImageField(
        upload_to=film_poster_path, verbose_name="Постер", blank=True, null=True
    )
    trailer_url = models.URLField(blank=True, verbose_name="Ссылка на трейлер")
    country = models.CharField(max_length=100, verbose_name="Страна производства")
    director = models.CharField(max_length=200, verbose_name="Режиссер")
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, verbose_name="Жанр")
    emotions = models.ManyToManyField(
        Emotion,
        through="FilmEmotionRating",
        related_name="films",
        verbose_name="Эмоции",
    )
    rating = models.FloatField(
        default=0.0,
        verbose_name="Рейтинг фильма",
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    views_count = models.IntegerField(default=0, verbose_name="Количество просмотров")
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="films_created",
        verbose_name="Добавил",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["genre"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.year})"

    @property
    def duration_hours(self):
        """Возвращает продолжительность в часах"""
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}ч {minutes}мин"

    @property
    def emotion_profile(self):
        """Возвращает словарь с эмоциональным профилем"""
        ratings = FilmEmotionRating.objects.filter(film=self).select_related("emotion")
        return {rating.emotion.name: rating.intensity for rating in ratings}

    def update_rating(self):
        """Обновляет рейтинг фильма на основе эмоциональных оценок"""
        ratings = FilmEmotionRating.objects.filter(film=self)
        if ratings.exists():
            avg_intensity = sum(r.intensity for r in ratings) / ratings.count()
            self.rating = round(avg_intensity, 1)
            self.save(update_fields=["rating"])


class FilmEmotionRating(models.Model):
    """Оценка эмоционального воздействия фильма"""

    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name="emotion_ratings",
        verbose_name="Фильм",
    )
    emotion = models.ForeignKey(
        Emotion,
        on_delete=models.CASCADE,
        related_name="film_ratings",
        verbose_name="Эмоция",
    )
    intensity = models.IntegerField(
        verbose_name="Интенсивность (1-10)",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    description = models.TextField(blank=True, verbose_name="Описание воздействия")
    rated_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ratings_given",
        verbose_name="Оценил",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оценки")

    class Meta:
        verbose_name = "Оценка эмоции фильма"
        verbose_name_plural = "Оценки эмоций фильмов"
        unique_together = ["film", "emotion"]
        ordering = ["-intensity"]

    def __str__(self):
        return f"{self.film.title} - {self.emotion.name}: {self.intensity}/10"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обновляем рейтинг фильма при изменении оценки
        self.film.update_rating()
