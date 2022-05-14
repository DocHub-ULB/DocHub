from rest_framework import serializers

from catalog.models import Category, Course
from documents.serializers import DocumentSerializer


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    document_set = DocumentSerializer(many=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "slug",
            "url",
            "categories",
            "document_set",
            "followers_count",
            "description",
        )

        extra_kwargs = {"url": {"lookup_field": "slug"}}


class ShortCourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "url",
            "slug",
            "name",
        )

        extra_kwargs = {"url": {"lookup_field": "slug"}}


class ShortCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "url",
            "name",
        )


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    children = ShortCategorySerializer(many=True)
    courses = ShortCourseSerializer(many=True, source="course_set")

    class Meta:
        model = Category
        fields = ("id", "url", "name", "parent", "children", "courses")

        extra_kwargs = {
            "course_set": {"lookup_field": "slug"},
        }
