from django.views.generic.list import ListView
from www.cbv import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from models import Notification


class NotificationsView(LoginRequiredMixin, ListView):
    model = Notification

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).filter(read=False)

@login_required
def markAsRead(request, pk):
    notif = get_object_or_404(Notification, pk=pk)
    if notif.user != request.user:
        pass
    notif.read = True
    notif.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('notifications')))
