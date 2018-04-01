from rest_framework import viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from mptt.utils import get_cached_trees

from catalog.serializers import (
    CourseSerializer,
    ShortCourseSerializer,
    CategorySerializer,
    ShortCategorySerializer,
)
from catalog.models import Course, Category


class CourseViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.prefetch_related(
        "document_set",
        "document_set__user",
        "document_set__tags"
    )
    serializer_class = ShortCourseSerializer
    serializer_detail_class = CourseSerializer

    lookup_field = 'slug'


class CategoryViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_detail_class = CategorySerializer
    serializer_class = ShortCategorySerializer


class Tree(APIView):
    """
    A view of the course and category tree, viewed from the top node.
    """
    def get(self, request):
        def course(node):
            return {
                'name': node.name,
                'id': node.id,
                'slug': node.slug,
            }

        def category(node):
            return {
                'name': node.name,
                'id': node.id,
                'children': list(map(category, node.get_children())),
                'courses': list(map(course, node.course_set.all())),
            }

        categories = list(map(category, get_cached_trees(Category.objects.prefetch_related('course_set').all())))
        return Response(categories)
