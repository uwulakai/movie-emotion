from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, FormView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random

from django.contrib.auth import views as auth_views

from django.contrib.auth.models import User

from .models import UserProfile, EmailConfirmation
from .forms import UserRegistrationForm, UserProfileForm, ConfirmCodeForm
from films.models import Film


class CustomLoginView(auth_views.LoginView):
    template_name = "users/login.html"

    def form_invalid(self, form):
        messages.error(self.request, "Неверный логин или пароль")
        return super().form_invalid(form)


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("films:list")

    def form_valid(self, form):
        # Сначала проверим, не заняты ли username/email
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        if User.objects.filter(username=username).exists():
            form.add_error("username", "Имя пользователя уже занято")
            return self.form_invalid(form)

        if User.objects.filter(email=email).exists():
            form.add_error("email", "Пользователь с таким email уже существует")
            return self.form_invalid(form)

        # Сохраняем данные регистрации во временное хранилище (сессия)
        reg_data = {
            "username": username,
            "password": form.cleaned_data.get("password1"),
            "first_name": form.cleaned_data.get("first_name", ""),
            "last_name": form.cleaned_data.get("last_name", ""),
            "email": email,
        }
        session_key = f"registration_data:{email}"
        self.request.session[session_key] = reg_data

        # Генерируем код подтверждения и сохраняем (по email)
        code = str(random.randint(100000, 999999))
        EmailConfirmation.objects.create(email=email, code=code)

        # Отправляем письмо с кодом подтверждения
        try:
            send_mail(
                subject="Код подтверждения регистрации",
                message=(
                    f"Здравствуйте, {username}!\n\n"
                    f"Ваш код подтверждения: {code}\n"
                    f"Если вы не регистрировались, просто проигнорируйте это письмо.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Ошибка отправки письма с кодом подтверждения: {e}")

        messages.info(
            self.request,
            "На указанный email отправлен код подтверждения. Введите его для активации аккаунта.",
        )

        # Перенаправляем пользователя на страницу подтверждения с email в параметре
        url = reverse("users:confirm") + f"?email={email}"
        return redirect(url)


class ConfirmRegistrationView(FormView):
    template_name = "users/confirm.html"
    form_class = ConfirmCodeForm
    success_url = reverse_lazy("films:list")

    def get_initial(self):
        initial = super().get_initial()
        email = self.request.GET.get("email") or self.request.POST.get("email")
        if email:
            initial["email"] = email
        return initial

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        code = form.cleaned_data.get("code")

        try:
            confirmation = EmailConfirmation.objects.filter(
                email=email, is_used=False
            ).latest("created_at")
        except EmailConfirmation.DoesNotExist:
            form.add_error(None, "Код подтверждения не найден")
            return self.form_invalid(form)

        # Проверяем код и срок действия (24 часа)
        if confirmation.code != code:
            form.add_error("code", "Неверный код подтверждения")
            return self.form_invalid(form)

        if confirmation.created_at + timedelta(hours=24) < timezone.now():
            form.add_error(None, "Код подтверждения просрочен")
            return self.form_invalid(form)

        # Получаем данные регистрации из сессии
        session_key = f"registration_data:{email}"
        reg_data = self.request.session.get(session_key)
        if not reg_data:
            form.add_error(
                None,
                "Данные регистрации не найдены. Пожалуйста, зарегистрируйтесь заново.",
            )
            return self.form_invalid(form)

        username = reg_data.get("username")
        password = reg_data.get("password")
        first_name = reg_data.get("first_name", "")
        last_name = reg_data.get("last_name", "")

        # Проверяем, не появился ли за это время пользователь с таким именем
        if User.objects.filter(username=username).exists():
            form.add_error(
                None,
                "Имя пользователя стало занято. Пожалуйста, зарегистрируйтесь снова с другим именем.",
            )
            return self.form_invalid(form)

        # Создаём пользователя и профиль
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "notification_frequency": "daily",
                "email_notifications": True,
            },
        )

        confirmation.is_used = True
        confirmation.save(update_fields=["is_used"])

        # Удаляем временные данные регистрации
        try:
            del self.request.session[session_key]
        except KeyError:
            pass

        # Входим за пользователя
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(self.request, user)
        messages.success(
            self.request, "Аккаунт успешно подтверждён и вы вошли в систему."
        )
        return super().form_valid(form)


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "first_name": request.user.first_name or "",
            "last_name": request.user.last_name or "",
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )

    favorite_films = profile.favorite_films.all()
    subscriptions = profile.subscriptions.filter(is_active=True)
    notifications = profile.notifications.filter(is_read=False).order_by("-created_at")[
        :10
    ]

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
            "first_name": request.user.first_name or "",
            "last_name": request.user.last_name or "",
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

    return render(
        request, "users/profile_edit.html", {"form": form, "profile": profile}
    )


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
