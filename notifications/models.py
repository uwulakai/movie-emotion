from django.db import models

from emotions.models import Emotion
from films.models import Film, FilmEmotionRating
from users.models import UserProfile


class Subscription(models.Model):
    """Подписка пользователя на эмоции"""

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    emotion = models.ForeignKey(
        Emotion,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Эмоция",
    )
    min_intensity = models.IntegerField(
        default=5,
        verbose_name="Минимальная интенсивность",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    last_notified = models.DateTimeField(
        null=True, blank=True, verbose_name="Последнее уведомление"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ["user", "emotion"]
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.user.username} → {self.emotion.name} (от {self.min_intensity}/10)"
        )

    def check_film(self, film):
        """Проверяет, подходит ли фильм для подписки"""
        try:
            rating = FilmEmotionRating.objects.get(film=film, emotion=self.emotion)
            return rating.intensity >= self.min_intensity
        except FilmEmotionRating.DoesNotExist:
            return False


class Notification(models.Model):
    """Уведомление для пользователя"""

    NOTIFICATION_TYPES = [
        ("new_film", "Новый фильм"),
        ("subscription", "По подписке"),
        ("system", "Системное"),
        ("recommendation", "Рекомендация"),
    ]

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Пользователь",
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="Подписка",
    )
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="Фильм",
    )
    emotion = models.ForeignKey(
        Emotion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Эмоция"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default="new_film",
        verbose_name="Тип уведомления",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    message = models.TextField(verbose_name="Текст уведомления")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    sent_via_email = models.BooleanField(
        default=False, verbose_name="Отправлено по email"
    )
    sent_via_telegram = models.BooleanField(
        default=False, verbose_name="Отправлено в Telegram"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} для {self.user.username}"

    def mark_as_read(self):
        """Помечает уведомление как прочитанное"""
        self.is_read = True
        self.save(update_fields=["is_read"])

    def send_email(self):
        """Отправляет email уведомление"""
        # Здесь будет логика отправки email
        # Пока просто помечаем как отправленное
        self.sent_via_email = True
        self.save(update_fields=["sent_via_email"])

    def send_telegram(self):
        """Отправляет уведомление в Telegram"""
        # Здесь будет логика отправки в Telegram
        if self.user.profile.telegram_id:
            self.sent_via_telegram = True
            self.save(update_fields=["sent_via_telegram"])
