from mptt.utils import get_cached_trees
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import DetailSerializerMixin

from catalog.models import Category, Course
from catalog.serializers import (
    CategorySerializer,
    CourseSerializer,
    ShortCategorySerializer,
    ShortCourseSerializer,
)


class CourseViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.prefetch_related(
        "document_set", "document_set__user", "document_set__tags"
    )
    serializer_class = ShortCourseSerializer
    serializer_detail_class = CourseSerializer

    lookup_field = "slug"


class CategoryViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Category.objects.prefetch_related("children")
        .prefetch_related("course_set")
        .all()
    )
    serializer_detail_class = CategorySerializer
    serializer_class = ShortCategorySerializer


class Tree(viewsets.ViewSet):
    """
    A view of the course and category tree, viewed from the top node.
    """

    def list(self, request, format=None):
        def course(node: Course):
            return {
                "name": node.name,
                "id": node.id,
                "slug": node.slug,
            }

        def category(node: Category):
            return {
                "name": node.name,
                "id": node.id,
                "children": list(map(category, node.get_children())),
                "courses": list(map(course, node.course_set.all())),
            }

        categories = list(
            map(
                category,
                get_cached_trees(Category.objects.prefetch_related("course_set").all()),
            )
        )
        return Response(categories)
