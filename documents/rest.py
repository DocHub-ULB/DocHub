# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.views import APIView
from rest_framework.response import Response

from documents.serializers import DocumentSerializer, PageSerializer
from documents.models import Document, Page, Vote


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all() \
                               .prefetch_related("vote_set__user") \
                               .prefetch_related("tags") \
                               .select_related("course") \
                               .select_related("user")
    serializer_class = DocumentSerializer


class PageViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class VoteView(APIView):
    def post(self, request, pk, format=None):
        user = request.user
        data = request.data

        vote, created = Vote.objects.get_or_create(document_id=pk, user=user)
        vote.vote_type = data["vote_type"]
        vote.save()

        return Response({"status": "ok"})
