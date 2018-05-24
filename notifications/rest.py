from rest_framework import viewsets

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        all_notifs = 'all' in self.request.query_params
        qs = Notification.objects.filter(user=self.request.user)
        if not all_notifs:
            qs = qs.filter(read=False)
        qs = qs.select_related('action')
        qs = qs.prefetch_related('action__target', 'action__actor', 'action__action_object')

        return qs
