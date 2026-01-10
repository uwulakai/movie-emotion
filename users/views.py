from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from .models import UserProfile
from .forms import UserRegistrationForm, UserProfileForm
from films.models import Film


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("films:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            # Создаем профиль пользователя
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "notification_frequency": "daily",
                    "email_notifications": True,
                },
            )
            messages.success(self.request, "Регистрация прошла успешно!")
        return response


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    favorite_films = profile.favorite_films.all()
    subscriptions = profile.subscriptions.filter(is_active=True)
    notifications = profile.notifications.filter(is_read=False).order_by("-created_at")[:10]
    
    context = {
        "profile": profile,
        "favorite_films": favorite_films,
        "subscriptions": subscriptions,
        "notifications": notifications,
    }
    return render(request, "users/profile.html", context)


@login_required
def profile_edit_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, "users/profile_edit.html", {"form": form, "profile": profile})


@login_required
def toggle_favorite(request, film_id):
    film = get_object_or_404(Film, id=film_id, is_published=True)
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    if film in profile.favorite_films.all():
        profile.favorite_films.remove(film)
        messages.info(request, f'"{film.title}" удален из избранного')
    else:
        profile.favorite_films.add(film)
        messages.success(request, f'"{film.title}" добавлен в избранное')
    
    return redirect("films:detail", pk=film_id)
