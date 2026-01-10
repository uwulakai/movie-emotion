from django.urls import path
from .views import FilmListView, FilmDetailView

app_name = "films"

urlpatterns = [
    path("", FilmListView.as_view(), name="list"),
    path("<int:pk>/", FilmDetailView.as_view(), name="detail"),
]
