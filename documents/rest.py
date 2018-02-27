# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.views import APIView
from rest_framework.response import Response

from documents.serializers import DocumentSerializer, PageSerializer
from documents.models import Document, Page, Vote


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class PageViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class UpvoteView(APIView):
    def post(self, request, format=None):
        user = request.user
        data = request.data
        document = Document.objects.get(pk=data["doc_id"])

        try:
            vote = Vote.objects.get(document=document, user=user)
        except Vote.DoesNotExist:
            vote = Vote(document=document, user=user)

        vote.vote_type = vote.UPVOTE
        vote.save()

        return Response("Success")


class DownvoteView(APIView):
    def post(self, request, format=None):
        user = request.user
        data = request.data
        document = Document.objects.get(pk=data["doc_id"])

        try:
            vote = Vote.objects.get(document=document, user=user)
        except Vote.DoesNotExist:
            vote = Vote(document=document, user=user)

        vote.vote_type = vote.DOWNVOTE
        vote.save()

        return Response("Success")
