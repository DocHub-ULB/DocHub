from django.urls import path

from notifications import views

urlpatterns = [
    path("", views.NotificationsView.as_view(), name="notifications"),
    path("read/<int:pk>", views.markAsRead, name="mark_as_read"),
    path("redirect/<int:pk>", views.markAsReadAndRedirect, name="read_and_redirect"),
    path("read_all", views.markAllAsRead, name="read_all"),
]
