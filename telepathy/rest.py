from rest_framework import viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin

from telepathy.models import Message, Thread
from telepathy.serializers import (
    MessageSerializer,
    SmallThreadSerializer,
    ThreadSerializer,
)


class ThreadViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Thread.objects.select_related('user', 'course', 'document').all()
    serializer_class = SmallThreadSerializer
    serializer_detail_class = ThreadSerializer


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.select_related('user').all()
    serializer_class = MessageSerializer
