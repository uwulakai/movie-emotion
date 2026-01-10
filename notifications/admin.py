from django.contrib import admin

from .models import Subscription, Notification


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "emotion",
        "min_intensity",
        "is_active",
        "created_at",
        "last_notified",
    ]
    list_filter = ["is_active", "emotion", "min_intensity", "created_at"]
    search_fields = ["user__user__username", "emotion__name"]
    readonly_fields = ["created_at", "last_notified"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user__user", "emotion")
        )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "title",
        "notification_type",
        "is_read",
        "sent_via_email",
        "created_at",
    ]
    list_filter = [
        "notification_type",
        "is_read",
        "sent_via_email",
        "sent_via_telegram",
        "created_at",
    ]
    search_fields = ["user__user__username", "title", "message", "film__title"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user__user", "film", "emotion", "subscription")
        )
