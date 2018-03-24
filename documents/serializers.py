# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from documents.models import Document, Page, Vote
from tags.serializers import TagSerializer
from users.serializers import SmallUserSerializer


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer(many=True)
    user = SmallUserSerializer()

    user_vote = serializers.SerializerMethodField()
    has_perm = serializers.SerializerMethodField()

    def get_user_vote(self, document):
        user = self.context['request'].user
        # We do the filtering in python as this method is called from REST with all the necessary
        #   data already prefetched. Using self.vote_set.filter() would lead to another roundtrip
        #   to the database for each document. Thats bad.
        users_vote = None
        for vote in document.vote_set.all():
            if vote.user == user:
                users_vote = vote
                break

        if users_vote is None:
            return 0
        elif users_vote.vote_type == Vote.UPVOTE:
            return 1
        elif users_vote.vote_type == Vote.DOWNVOTE:
            return -1
        else:
            raise NotImplemented("Vote not of known type.")

    def get_has_perm(self, document):
        user = self.context['request'].user
        return user.write_perm(obj=document)

    class Meta:
        model = Document
        fields = (
            'course', 'date', 'description', 'downloads', 'file_type',
            'has_perm', 'hidden', 'id', 'is_processing', 'is_ready',
            'is_unconvertible', 'md5', 'name', 'pages', 'size', 'state',
            'tags', 'url', 'user', 'user_vote', 'views', 'votes',
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
