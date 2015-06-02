from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from graph.serializers import CourseSerializer, ShortCourseSerializer, CategorySerializer, ShortCategorySerializer
from graph.models import Course, Category


class CourseViewSet(viewsets.ViewSet):
    def list(self, request):
        serializer = self.short_serializer_class(self.queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, slug=None):
        course = get_object_or_404(self.queryset, slug=slug)
        serializer = self.serializer_class(course, context={'request': request})
        return Response(serializer.data)

    queryset = Course.objects.all()
    short_serializer_class = ShortCourseSerializer
    serializer_class = CourseSerializer

    lookup_field = 'slug'


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request):
        serializer = self.short_serializer_class(self.queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        category = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(category, context={'request': request})
        return Response(serializer.data)

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    short_serializer_class = ShortCategorySerializer
