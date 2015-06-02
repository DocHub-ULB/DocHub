from rest_framework import viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin

from graph.serializers import CourseSerializer, ShortCourseSerializer, CategorySerializer, ShortCategorySerializer
from graph.models import Course, Category


class CourseViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = ShortCourseSerializer
    serializer_detail_class = CourseSerializer

    lookup_field = 'slug'


class CategoryViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_detail_class = CategorySerializer
    serializer_class = ShortCategorySerializer
