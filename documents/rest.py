# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from documents.serializers import DocumentSerializer
from documents.models import Document, Vote


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class VoteView(APIView):
    def post(self, request, pk, format=None):
        user = request.user
        data = request.data

        vote, created = Vote.objects.get_or_create(document_id=pk, user=user)
        vote.vote_type = data["vote_type"]
        vote.save()

        return Response({"status": "ok"})
