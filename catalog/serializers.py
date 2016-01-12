# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from rest_framework import serializers

from catalog.models import Course, Category
from documents.serializers import DocumentSerializer


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    document_set = DocumentSerializer(many=True)

    class Meta:
        model = Course
        fields = (
            'id', 'name', 'slug', 'url',
            'categories', 'document_set', 'thread_set'
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
