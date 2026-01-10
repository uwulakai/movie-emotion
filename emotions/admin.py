from django.contrib import admin
from django.utils.html import format_html

from .models import Emotion


@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ["name", "color_display", "icon", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "slug"]
    prepopulated_fields = {"slug": ("name",)}

    def color_display(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
                obj.color,
                obj.color,
            )
        return "-"

    color_display.short_description = "Цвет"
