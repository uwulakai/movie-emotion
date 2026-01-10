from django.db import models
from django.contrib.auth.models import User

from emotions.models import Emotion


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар"
    )
    bio = models.TextField(blank=True, verbose_name="О себе")
    preferred_emotions = models.ManyToManyField(
        Emotion,
        blank=True,
        related_name="preferred_by_users",
        verbose_name="Предпочитаемые эмоции",
    )
    notification_frequency = models.CharField(
        max_length=20,
        choices=[("daily", "Ежедневно"), ("weekly", "Еженедельно")],
        default="daily",
        verbose_name="Частота уведомлений",
    )
    email_notifications = models.BooleanField(
        default=True, verbose_name="Email уведомления"
    )
    telegram_id = models.CharField(
        max_length=100, blank=True, verbose_name="Telegram ID"
    )
    favorite_films = models.ManyToManyField(
        "films.Film",
        blank=True,
        related_name="favorited_by",
        verbose_name="Любимые фильмы",
    )
    search_history = models.JSONField(
        default=list, blank=True, verbose_name="История поиска"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль: {self.user.username}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
