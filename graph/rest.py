from rest_framework import viewsets

from graph.serializers import CourseSerializer
from graph.models import Course, Category


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    lookup_field = 'slug'
