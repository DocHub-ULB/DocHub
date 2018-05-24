from rest_framework import serializers
from notifications.models import Notification
from www.serializers import FeedSerializer


class NotificationSerializer(serializers.ModelSerializer):
    action = FeedSerializer()

    class Meta:
        model = Notification
        fields = ('id', 'read', 'action')
