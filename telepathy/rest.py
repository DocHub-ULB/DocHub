# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin

from telepathy.serializers import ThreadSerializer, SmallThreadSerializer, MessageSerializer
from telepathy.models import Thread, Message


class ThreadViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = SmallThreadSerializer
    serializer_detail_class = ThreadSerializer


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
