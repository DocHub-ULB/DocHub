import json

from rest_framework import serializers

from catalog.models import Course, Category
from documents.serializers import DocumentSerializer
from telepathy.serializers import SmallThreadSerializer


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    document_set = DocumentSerializer(many=True)
    thread_set = SmallThreadSerializer(many=True)

    class Meta:
        model = Course
        fields = (
            'id', 'name', 'slug', 'url',
            'categories', 'document_set', 'thread_set',
            'gehol_url', 'followers_count', 'description',
        )

        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class ShortCourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'url', 'slug', 'name', )

        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class ShortCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'url', 'name', )


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    children = ShortCategorySerializer(many=True)
    courses = ShortCourseSerializer(many=True, source="course_set")

    class Meta:
        model = Category
        fields = ('id', 'url', 'name', 'parent', 'children', 'courses')

        extra_kwargs = {
            'course_set': {'lookup_field': 'slug'},
        }
