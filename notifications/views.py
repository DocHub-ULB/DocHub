from django.views.generic.list import ListView
from www.cbv import LoginRequiredMixin

from models import Notification


class NotificationsView(LoginRequiredMixin, ListView):
    model = Notification

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).filter(read=False)
