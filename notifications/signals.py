from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from films.models import Film, FilmEmotionRating
from .models import Subscription, Notification


def _notify_subscribers_for_film(film):
    """Отправляет уведомления всем подписчикам для опубликованного фильма."""

    # Проверяем, что фильм опубликован
    if not film.is_published:
        return

    # Получаем все эмоциональные оценки фильма
    emotion_ratings = FilmEmotionRating.objects.filter(film=film).select_related(
        "emotion"
    )

    # Если у фильма нет оценок - не отправляем уведомления
    if not emotion_ratings.exists():
        return

    # Для каждой эмоциональной оценки
    for rating in emotion_ratings:
        emotion = rating.emotion
        intensity = rating.intensity

        # Ищем активные подписки для этой эмоции с подходящей интенсивностью
        subscriptions = Subscription.objects.filter(
            emotion=emotion, min_intensity__lte=intensity, is_active=True
        ).select_related("user__user")

        for subscription in subscriptions:
            user_profile = subscription.user
            user = user_profile.user

            # Проверяем, не было ли уже уведомления для этой комбинации
            existing_notification = Notification.objects.filter(
                user=user_profile,
                film=film,
                emotion=emotion,
                notification_type="subscription",
            ).exists()

            if existing_notification:
                continue

            # Создаём уведомление
            notification = Notification.objects.create(
                user=user_profile,
                subscription=subscription,
                film=film,
                emotion=emotion,
                notification_type="subscription",
                title=f'Новый фильм: "{film.title}"',
                message=(
                    f'По вашей подписке на эмоцию "{emotion.name}" '
                    f'появился новый фильм "{film.title}" ({film.year}) '
                    f"с интенсивностью {intensity}/10."
                ),
            )

            # Отправляем email если включено
            if user_profile.email_notifications and user.email:
                try:
                    site_domain = (
                        settings.ALLOWED_HOSTS[0]
                        if settings.ALLOWED_HOSTS
                        else "localhost"
                    )
                    if "://" not in site_domain:
                        site_domain = f"http://{site_domain}"

                    send_mail(
                        subject=f'MovieEmotion: Новый фильм по подписке - "{film.title}"',
                        message=(
                            f"Здравствуйте, {user.username}!\n\n"
                            f'По вашей подписке на эмоцию "{emotion.name}" '
                            f"появился новый фильм:\n\n"
                            f'"{film.title}" ({film.year})\n'
                            f"Режиссер: {film.director}\n"
                            f"Жанр: {film.get_genre_display()}\n"
                            f'Интенсивность эмоции "{emotion.name}": {intensity}/10\n\n'
                            f"Описание: {film.description[:200]}...\n\n"
                            f"Посмотреть фильм: {site_domain}/films/{film.id}/\n\n"
                            f"---\n"
                            f"MovieEmotion - подбор фильмов по эмоциям\n"
                            f"Отписаться от уведомлений можно в личном кабинете"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                    )
                    notification.sent_via_email = True
                    notification.save(update_fields=["sent_via_email"])
                except Exception as e:
                    print(
                        f"Ошибка отправки email для пользователя {user.username}: {e}"
                    )

            # Обновляем дату последнего уведомления
            subscription.last_notified = notification.created_at
            subscription.save(update_fields=["last_notified"])


@receiver(pre_save, sender=Film)
def _store_old_publish_state(sender, instance, **kwargs):
    """Сохраняем предыдущее состояние is_published для сравнения."""
    if instance.pk:
        try:
            prev = Film.objects.get(pk=instance.pk)
            instance._old_is_published = prev.is_published
        except Film.DoesNotExist:
            instance._old_is_published = None
    else:
        instance._old_is_published = None


@receiver(post_save, sender=Film)
def handle_film_publish_changes(sender, instance, created, **kwargs):
    """Обрабатываем публикацию фильма."""

    # Определяем, был ли фильм только что опубликован
    just_published = False

    # Ситуация 1: Фильм создан и сразу опубликован
    if created and instance.is_published:
        just_published = True

    # Ситуация 2: Фильм обновлен и изменился статус с неопубликованного на опубликованный
    elif not created and hasattr(instance, "_old_is_published"):
        if instance._old_is_published is False and instance.is_published:
            just_published = True

    # Если фильм не был опубликован - ничего не делаем
    if not just_published:
        return

    # Используем transaction.on_commit чтобы гарантировать, что фильм сохранен
    from django.db import transaction

    transaction.on_commit(lambda: _notify_subscribers_for_film(instance))
