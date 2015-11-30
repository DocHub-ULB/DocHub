from django.views.generic.list import ListView
from www.cbv import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse

from models import Notification


class NotificationsView(LoginRequiredMixin, ListView):
    model = Notification

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).filter(read=False)


@login_required
def markAsRead(request, pk, redirect_to_object=False):
    notif = get_object_or_404(Notification, pk=pk)
    if notif.user != request.user:
        return HttpResponseForbidden("Not your notification")
    notif.read = True
    notif.save()

    if redirect_to_object:
        return_url = notif.action.action_object.get_absolute_url()
        if return_url is None:
            return_url = notif.action.action_object_url()
    else:
        return_url = request.META.get('HTTP_REFERER')
        if return_url is None:
            return_url = reverse('notifications')

    return HttpResponseRedirect(return_url)


@login_required
def markAllAsRead(request):
    user = request.user
    Notification.objects.filter(user=user).filter(read=False).update(read=True)
    return HttpResponseRedirect(reverse('notifications'))
