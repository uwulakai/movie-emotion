from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from films.models import Film, FilmEmotionRating
from .models import Subscription, Notification


@receiver(post_save, sender=Film)
def notify_subscribers_on_new_film(sender, instance, created, **kwargs):
    """Отправляет уведомления подписчикам при создании нового фильма"""
    if not created or not instance.is_published:
        return

    # Получаем эмоциональные оценки фильма
    emotion_ratings = FilmEmotionRating.objects.filter(film=instance).select_related(
        "emotion"
    )

    if not emotion_ratings.exists():
        return

    # Находим все активные подписки, которые соответствуют эмоциям фильма
    for rating in emotion_ratings:
        subscriptions = Subscription.objects.filter(
            emotion=rating.emotion,
            min_intensity__lte=rating.intensity,
            is_active=True,
        ).select_related("user__user")

        for subscription in subscriptions:
            user = subscription.user.user
            profile = subscription.user

            # Проверяем настройки уведомлений пользователя
            if not profile.email_notifications:
                # Создаем уведомление, но не отправляем email
                Notification.objects.create(
                    user=profile,
                    subscription=subscription,
                    film=instance,
                    emotion=rating.emotion,
                    notification_type="subscription",
                    title=f'Новый фильм: "{instance.title}"',
                    message=(
                        f'По вашей подписке на эмоцию "{rating.emotion.name}" '
                        f'появился новый фильм "{instance.title}" '
                        f"({instance.year}) с интенсивностью {rating.intensity}/10."
                    ),
                )
                continue

            # Создаем уведомление в базе данных
            notification = Notification.objects.create(
                user=profile,
                subscription=subscription,
                film=instance,
                emotion=rating.emotion,
                notification_type="subscription",
                title=f'Новый фильм: "{instance.title}"',
                message=(
                    f'По вашей подписке на эмоцию "{rating.emotion.name}" '
                    f'появился новый фильм "{instance.title}" '
                    f"({instance.year}) с интенсивностью {rating.intensity}/10."
                ),
            )

            # Отправляем email уведомление
            try:
                send_mail(
                    subject=f'Новый фильм по подписке: "{instance.title}"',
                    message=(
                        f"Здравствуйте, {user.username}!\n\n"
                        f'По вашей подписке на эмоцию "{rating.emotion.name}" '
                        f"появился новый фильм:\n\n"
                        f'"{instance.title}" ({instance.year})\n'
                        f"Режиссер: {instance.director}\n"
                        f'Интенсивность эмоции "{rating.emotion.name}": {rating.intensity}/10\n\n'
                        f"Описание: {instance.description[:200]}...\n\n"
                        f"Посмотреть фильм: {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}/films/{instance.id}/\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                notification.sent_via_email = True
                notification.save(update_fields=["sent_via_email"])
            except Exception as e:
                # Логируем ошибку, но не прерываем выполнение
                print(f"Ошибка отправки email для пользователя {user.username}: {e}")

            # Обновляем дату последнего уведомления
            subscription.last_notified = notification.created_at
            subscription.save(update_fields=["last_notified"])
