from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    # Если django-filter не установлен, используем только встроенные фильтры
    DjangoFilterBackend = None

from .models import Film, FilmEmotionRating
from .serializers import FilmSerializer, FilmListSerializer, EmotionSerializer
from emotions.models import Emotion


class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с фильмами через API
    """
    queryset = Film.objects.filter(is_published=True).prefetch_related(
        "emotion_ratings__emotion"
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
        filterset_fields = ["genre", "year", "country"]
    search_fields = ["title", "description", "director"]
    ordering_fields = ["year", "rating", "views_count", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return FilmListSerializer
        return FilmSerializer

    @action(detail=False, methods=["get"])
    def by_emotion(self, request):
        """
        Получить фильмы по эмоциям
        Параметры: emotion_ids (список ID эмоций), min_intensity (минимальная интенсивность)
        """
        emotion_ids = request.query_params.getlist("emotion_ids", [])
        min_intensity = request.query_params.get("min_intensity", 1)

        try:
            min_intensity = int(min_intensity)
        except ValueError:
            min_intensity = 1

        queryset = self.get_queryset()

        if emotion_ids:
            queryset = queryset.filter(
                emotion_ratings__emotion_id__in=emotion_ids,
                emotion_ratings__intensity__gte=min_intensity,
            ).distinct()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def emotion_profile(self, request, pk=None):
        """
        Получить эмоциональный профиль фильма
        """
        film = self.get_object()
        ratings = FilmEmotionRating.objects.filter(film=film).select_related("emotion")
        
        profile = {
            rating.emotion.name: {
                "intensity": rating.intensity,
                "color": rating.emotion.color,
                "icon": rating.emotion.icon,
            }
            for rating in ratings
        }
        
        return Response(profile)


class EmotionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с эмоциями через API
    """
    queryset = Emotion.objects.filter(is_active=True)
    serializer_class = EmotionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]
