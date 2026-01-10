from django.db import models

from emotions.enums import EMOTION_COLORS
from slugify import slugify


class Emotion(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название эмоции")
    slug = models.SlugField(
        max_length=100, unique=True, verbose_name="URL-идентификатор", blank=True
    )
    description = models.TextField(verbose_name="Описание эмоционального состояния")
    color = models.CharField(
        max_length=7,
        choices=EMOTION_COLORS,
        default="#FF6B6B",
        verbose_name="Цвет для визуализации",
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Название иконки (FontAwesome)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Эмоция"
        verbose_name_plural = "Эмоции"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        # Всегда генерируем slug, если он пустой
        if not self.slug or self.slug.strip() == "":
            self.slug = slugify(self.name)

        if self.slug:
            original_slug = self.slug
            counter = 1
            while Emotion.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def css_color(self):
        """Возвращает цвет для CSS"""
        return self.color
