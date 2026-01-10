from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.db.models import Prefetch

from .models import Film, FilmEmotionRating
from emotions.models import Emotion
from .forms import FilmSearchForm


class FilmListView(ListView):
    model = Film
    template_name = "films/list.html"
    context_object_name = "films"
    paginate_by = 12

    def get_queryset(self):
        queryset = Film.objects.filter(is_published=True).select_related("created_by__user")
        
        # Поиск по названию
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # Фильтр по жанру
        genre = self.request.GET.get("genre")
        if genre:
            queryset = queryset.filter(genre=genre)
        
        # Фильтр по году
        year = self.request.GET.get("year")
        if year:
            queryset = queryset.filter(year=year)
        
        # Поиск по эмоциям
        emotion_ids = self.request.GET.getlist("emotions")
        if emotion_ids:
            queryset = queryset.filter(
                emotion_ratings__emotion_id__in=emotion_ids
            ).distinct()
        
        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["emotions"] = Emotion.objects.filter(is_active=True)
        context["search_form"] = FilmSearchForm(self.request.GET)
        context["genres"] = Film.GENRE_CHOICES
        return context


class FilmDetailView(DetailView):
    model = Film
    template_name = "films/detail.html"
    context_object_name = "film"

    def get_queryset(self):
        return Film.objects.filter(is_published=True).prefetch_related(
            "emotion_ratings__emotion"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        film = self.object
        
        # Получаем эмоциональный профиль
        emotion_ratings = FilmEmotionRating.objects.filter(
            film=film
        ).select_related("emotion")
        
        context["emotion_ratings"] = emotion_ratings
        context["emotion_profile"] = {
            rating.emotion.name: rating.intensity for rating in emotion_ratings
        }
        
        # Похожие фильмы (по жанру)
        context["similar_films"] = Film.objects.filter(
            genre=film.genre, is_published=True
        ).exclude(id=film.id)[:6]
        
        # Увеличиваем счетчик просмотров
        film.views_count += 1
        film.save(update_fields=["views_count"])
        
        return context
