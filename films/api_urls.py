from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import FilmViewSet, EmotionViewSet

router = DefaultRouter()
router.register(r"films", FilmViewSet, basename="film")
router.register(r"emotions", EmotionViewSet, basename="emotion")

urlpatterns = [
    path("", include(router.urls)),
]
