from graph.models import Course, Category
from documents.models import Document
from rest_framework import serializers
from documents.serializers import ShortDocumentSerializer
import json


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    meta = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    def get_meta(self, course):
        return json.loads(course.description)

    def get_documents(self, course):
        children = course.children().non_polymorphic()
        docs = filter(lambda x: x.get_real_instance_class() == Document, children)
        docs = map(lambda x: x.id, docs)
        docs = Document.objects.filter(id__in=docs)
        return ShortDocumentSerializer(docs, many=True, context={'request': self.context['request']}).data

    class Meta:
        model = Course
        fields = (
            'id',
            'name',
            'slug',
            'url',
            'documents',
            'meta',

        )

        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class ShortCourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id',
            'url',
            'slug',
            'name',
        )

        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    subcategories = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    def get_subcategories(self, cat):
        children = cat.children().non_polymorphic()
        cats = filter(lambda x: x.get_real_instance_class() == Category, children)
        cats = map(lambda x: x.id, cats)
        cats = Category.objects.filter(id__in=cats)
        return ShortCategorySerializer(
            cats,
            many=True,
            context={'request': self.context['request']}
        ).data

    def get_courses(self, cat):
        children = cat.children().non_polymorphic()
        courses = filter(lambda x: x.get_real_instance_class() == Course, children)
        courses = map(lambda x: x.id, courses)
        courses = Course.objects.filter(id__in=courses)
        return ShortCourseSerializer(
            courses,
            many=True,
            context={'request': self.context['request']}
        ).data

    class Meta:
        model = Category
        fields = (
            'id',
            'url',
            'slug',
            'name',
            'subcategories',
            'courses',
        )


class ShortCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'url',
            'slug',
            'name',
        )
