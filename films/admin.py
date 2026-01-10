from django.contrib import admin
from django.utils.html import format_html

from .models import Film, FilmEmotionRating


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "year",
        "director",
        "genre",
        "rating",
        "is_published",
        "views_count",
        "created_at",
    ]
    list_filter = ["genre", "year", "is_published", "created_at"]
    search_fields = ["title", "director", "description", "country"]
    readonly_fields = ["created_at", "updated_at", "views_count", "rating"]
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "original_title",
                    "description",
                    "poster",
                    "trailer_url",
                )
            },
        ),
        (
            "Детали",
            {
                "fields": (
                    "year",
                    "duration",
                    "country",
                    "director",
                    "genre",
                )
            },
        ),
        (
            "Статистика",
            {
                "fields": (
                    "rating",
                    "views_count",
                    "is_published",
                )
            },
        ),
        (
            "Системная информация",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("created_by")


@admin.register(FilmEmotionRating)
class FilmEmotionRatingAdmin(admin.ModelAdmin):
    list_display = ["film", "emotion", "intensity", "rated_by", "created_at"]
    list_filter = ["emotion", "intensity", "created_at"]
    search_fields = ["film__title", "emotion__name"]
    readonly_fields = ["created_at"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("film", "emotion", "rated_by__user")
        )
