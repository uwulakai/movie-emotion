from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Профиль"
    fields = (
        "first_name",
        "last_name",
        "avatar",
        "bio",
        "preferred_emotions",
        "notification_frequency",
        "email_notifications",
        "telegram_id",
    )
    filter_horizontal = ["preferred_emotions"]


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "full_name",
        "email_notifications",
        "notification_frequency",
        "created_at",
    ]
    list_filter = ["email_notifications", "notification_frequency", "created_at"]
    search_fields = ["user__username", "user__email", "first_name", "last_name"]
    readonly_fields = ["created_at"]
    filter_horizontal = ["preferred_emotions", "favorite_films"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
