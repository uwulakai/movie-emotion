from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView,
    profile_view,
    profile_edit_view,
    toggle_favorite,
    ConfirmRegistrationView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("confirm/", ConfirmRegistrationView.as_view(), name="confirm"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit_view, name="profile_edit"),
    path("favorite/<int:film_id>/", toggle_favorite, name="toggle_favorite"),
]
