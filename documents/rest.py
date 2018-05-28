# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.db.models import F

from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework import permissions
from www.rest import VaryModelViewSet

from documents.serializers import DocumentSerializer, UploadDocumentSerializer, EditDocumentSerializer
from documents.models import Document, Vote


class DocumentAccessPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if view.action == 'vote': # FIXME : hardcoded check is bad
            return True
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.write_perm(obj=obj)


class DocumentViewSet(VaryModelViewSet):
    permission_classes = (DocumentAccessPermission,)

    queryset = Document.objects.filter(hidden=False)\
        .select_related("course", 'user')\
        .prefetch_related('tags', 'vote_set')\
        .order_by("-edited")
    serializer_class = DocumentSerializer
    create_serializer_class = UploadDocumentSerializer
    update_serializer_class = EditDocumentSerializer

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

        document.downloads = F('views') + 1
        document.save(update_fields=['views'])
        return response

    @detail_route(methods=['post'])
    def vote(self, request, pk):
        document = self.get_object()

        vote, created = Vote.objects.get_or_create(document=document, user=request.user)
        vote.vote_type = request.data["vote_type"]
        vote.save()

        return Response({"status": "ok"})

    def destroy(self, request, pk=None):
        document = self.get_object()
        document.hidden = True
        document.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
