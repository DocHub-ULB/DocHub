# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from documents.models import Document, Page, Vote
from tags.serializers import TagSerializer
from users.serializers import SmallUserSerializer


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer(many=True)
    user = SmallUserSerializer()

    has_perm = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()

    def get_user_vote(self, document):
        user = self.context['request'].user
        try:
            vote = Vote.objects.get(document=document, user=user)
        except Vote.DoesNotExist:
            return 0

        if vote.vote_type == vote.UPVOTE:
            return 1
        elif vote.vote_type == vote.DOWNVOTE:
            return -1
        else:
            raise NotImplemented("Vote not of known type.")

    def get_has_perm(self, document):
        user = self.context['request'].user
        return user.write_perm(obj=document)

    class Meta:
        model = Document
        fields = (
            'id', 'name', 'url', 'course', 'description',
            'user', 'pages', 'date', 'views', 'user_vote', 'votes',
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


class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = (
            'document', 'numero', 'bitmap_120',
            'bitmap_600', 'bitmap_900', 'height_120',
            'height_600', 'height_900',
        )

        extra_kwargs = {
            'user': {'lookup_field': 'netid'},
        }
