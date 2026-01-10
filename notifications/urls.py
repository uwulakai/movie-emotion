from django.urls import path
from .views import (
    subscription_list,
    subscription_create,
    subscription_delete,
    subscription_toggle,
    notification_list,
    notification_mark_read,
    notification_mark_all_read,
)

app_name = "notifications"

urlpatterns = [
    path("subscriptions/", subscription_list, name="subscription_list"),
    path("subscriptions/create/", subscription_create, name="subscription_create"),
    path(
        "subscriptions/<int:subscription_id>/delete/",
        subscription_delete,
        name="subscription_delete",
    ),
    path(
        "subscriptions/<int:subscription_id>/toggle/",
        subscription_toggle,
        name="subscription_toggle",
    ),
    path("", notification_list, name="notification_list"),
    path(
        "<int:notification_id>/read/",
        notification_mark_read,
        name="notification_mark_read",
    ),
    path("mark-all-read/", notification_mark_all_read, name="mark_all_read"),
]
