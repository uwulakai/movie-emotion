from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):
        """
        Импортируем сигналы при запуске приложения.
        Этот метод вызывается, когда Django полностью загружен.
        """
        import notifications.signals
