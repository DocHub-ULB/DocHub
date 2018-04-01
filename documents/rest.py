# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unicodedata
from django.http import HttpResponse
from django.db.models import F

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from documents.serializers import DocumentSerializer
from documents.models import Document, Vote


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @detail_route()
    def original(self, request, pk):
        document = self.get_object()
        body = document.original.read()

        response = HttpResponse(body, content_type='application/octet-stream')
        response['Content-Description'] = 'File Transfer'
        response['Content-Transfer-Encoding'] = 'binary'
        response['Content-Disposition'] = 'attachment; filename="{}{}"'.format(document.safe_name, document.file_type).encode("ascii", "ignore")

        document.downloads = F('downloads') + 1
        document.save(update_fields=['downloads'])
        return response

    @detail_route()
    def pdf(self, request, pk):
        document = self.get_object()
        body = document.pdf.read()

        response = HttpResponse(body, content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; filename="%s.pdf"' % document.safe_name).encode("ascii", "ignore")

        document.downloads = F('downloads') + 1
        document.save(update_fields=['downloads'])
        return response


class VoteView(APIView):
    def post(self, request, pk, format=None):
        user = request.user
        data = request.data

        vote, created = Vote.objects.get_or_create(document_id=pk, user=user)
        vote.vote_type = data["vote_type"]
        vote.save()

        return Response({"status": "ok"})
