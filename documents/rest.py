# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from documents.serializers import DocumentSerializer
from documents.models import Document


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
