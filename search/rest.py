from rest_framework import viewsets
from rest_framework.response import Response

from search.serializers import CourseSearchSerializer
import search.logic


class CourseSearchViewSet(viewsets.ViewSet):
    def get_queryset(self):
        query = self.request.query_params.get('query', "")
        return search.logic.search_course(query)[:30]

    def list(self, request):
        serializer = CourseSearchSerializer(self.get_queryset(), context={'request': request}, many=True)
        return Response(serializer.data)
