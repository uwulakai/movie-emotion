from rest_framework import serializers
from .models import Film, FilmEmotionRating
from emotions.models import Emotion


class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emotion
        fields = ["id", "name", "slug", "description", "color", "icon"]


class FilmEmotionRatingSerializer(serializers.ModelSerializer):
    emotion = EmotionSerializer(read_only=True)

    class Meta:
        model = FilmEmotionRating
        fields = ["emotion", "intensity", "description"]


class FilmSerializer(serializers.ModelSerializer):
    emotion_ratings = FilmEmotionRatingSerializer(many=True, read_only=True)
    duration_hours = serializers.ReadOnlyField()
    emotion_profile = serializers.SerializerMethodField()

    class Meta:
        model = Film
        fields = [
            "id",
            "title",
            "original_title",
            "description",
            "year",
            "duration",
            "duration_hours",
            "poster",
            "trailer_url",
            "country",
            "director",
            "genre",
            "rating",
            "views_count",
            "is_published",
            "created_at",
            "emotion_ratings",
            "emotion_profile",
        ]
        read_only_fields = ["rating", "views_count", "created_at"]

    def get_emotion_profile(self, obj):
        return obj.emotion_profile


class FilmListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка фильмов"""

    class Meta:
        model = Film
        fields = [
            "id",
            "title",
            "year",
            "director",
            "genre",
            "rating",
            "poster",
            "duration",
        ]
