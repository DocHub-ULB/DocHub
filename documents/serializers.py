# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from documents.models import Document
from tags.serializers import TagSerializer
from users.serializers import SmallUserSerializer


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer(many=True)
    user = SmallUserSerializer()

    has_perm = serializers.SerializerMethodField()

    def get_has_perm(self, document):
        user = self.context['request'].user
        return user.write_perm(obj=document)

    class Meta:
        model = Document
        fields = (
            'id', 'name', 'url', 'course', 'description',
            'user', 'pages', 'date', 'views',
            'downloads', 'state', 'md5', 'tags', 'has_perm',
            'is_unconvertible', 'is_ready', 'is_processing',
            'hidden',
        )

        extra_kwargs = {
            'user': {'lookup_field': 'netid'},
            'course': {'lookup_field': 'slug'},
        }


class ShortDocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'url', 'course')
