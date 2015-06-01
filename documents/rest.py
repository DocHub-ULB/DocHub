from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from documents.serializers import DocumentSerializer, PageSerializer
from documents.models import Document, Page


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @detail_route()
    def page_set(self, request, pk):
        page_set = Document.objects.get(pk=pk).page_set.all()

        serializer = PageSerializer(
            page_set,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
