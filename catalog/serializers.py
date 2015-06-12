from catalog.models import Course, Category
from rest_framework import serializers
from documents.serializers import ShortDocumentSerializer
import json


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    meta = serializers.SerializerMethodField()

    def get_meta(self, course):
        return json.loads(course.description)

    class Meta:
        model = Course
        fields = ('id', 'name', 'slug', 'url', 'meta', 'categories', 'document_set')

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


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'url', 'slug', 'name', 'parent', 'children', 'course_set')

        extra_kwargs = {
            'course_set': {'lookup_field': 'slug'},
        }


class ShortCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'url', 'slug', 'name', )


