# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from documents.serializers import DocumentSerializer, PageSerializer
from documents.models import Document, Page


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class PageViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
