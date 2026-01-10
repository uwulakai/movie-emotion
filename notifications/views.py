from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Subscription, Notification
from .forms import SubscriptionForm
from emotions.models import Emotion
from users.models import UserProfile


@login_required
def subscription_list(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    subscriptions = profile.subscriptions.all().select_related("emotion")
    
    context = {
        "subscriptions": subscriptions,
        "profile": profile,
    }
    return render(request, "notifications/subscription_list.html", context)


@login_required
def subscription_create(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = profile
            subscription.save()
            messages.success(
                request,
                f'Подписка на "{subscription.emotion.name}" успешно создана!',
            )
            return redirect("notifications:subscription_list")
    else:
        form = SubscriptionForm()
    
    context = {
        "form": form,
        "emotions": Emotion.objects.filter(is_active=True),
    }
    return render(request, "notifications/subscription_create.html", context)


@login_required
def subscription_delete(request, subscription_id):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    subscription = get_object_or_404(
        Subscription, id=subscription_id, user=profile
    )
    
    if request.method == "POST":
        emotion_name = subscription.emotion.name
        subscription.delete()
        messages.success(request, f'Подписка на "{emotion_name}" удалена')
        return redirect("notifications:subscription_list")
    
    return render(
        request,
        "notifications/subscription_delete.html",
        {"subscription": subscription},
    )


@login_required
def subscription_toggle(request, subscription_id):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    subscription = get_object_or_404(
        Subscription, id=subscription_id, user=profile
    )
    subscription.is_active = not subscription.is_active
    subscription.save()
    
    status = "активирована" if subscription.is_active else "деактивирована"
    messages.info(request, f'Подписка {status}')
    return redirect("notifications:subscription_list")


@login_required
def notification_list(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    notifications = (
        profile.notifications.all()
        .select_related("film", "emotion", "subscription")
        .order_by("-created_at")
    )
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "notifications": page_obj,
        "profile": profile,
    }
    return render(request, "notifications/notification_list.html", context)


@login_required
def notification_mark_read(request, notification_id):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    notification = get_object_or_404(
        Notification, id=notification_id, user=profile
    )
    notification.mark_as_read()
    messages.info(request, "Уведомление отмечено как прочитанное")
    
    return redirect("notifications:notification_list")


@login_required
def notification_mark_all_read(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "notification_frequency": "daily",
            "email_notifications": True,
        },
    )
    
    profile.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "Все уведомления отмечены как прочитанные")
    
    return redirect("notifications:notification_list")
