# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from rest_framework import serializers

try:
    from minio.error import NoSuchKey
except ImportError:
    pass

from documents.models import Document, Vote
from tags.serializers import TagSerializer
from users.serializers import SmallUserSerializer
from rest_framework.fields import CurrentUserDefault

from documents import logic
from catalog.models import Course
from tags.models import Tag
from documents import tasks


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer(read_only=True, many=True)

    user = SmallUserSerializer(read_only=True)

    user_vote = serializers.SerializerMethodField(read_only=True)
    has_perm = serializers.SerializerMethodField(read_only=True)
    file_size = serializers.SerializerMethodField(read_only=True)

    original_url = serializers.HyperlinkedIdentityField(
        view_name='document-original',
    )

    pdf_url = serializers.HyperlinkedIdentityField(
        view_name='document-pdf',
    )

    class Meta:
        model = Document

        read_only_fields = (
            'course', 'date', 'downloads', 'file_size',
            'file_type', 'has_perm', 'id', 'is_processing',
            'is_ready', 'is_unconvertible', 'md5', 'pages', 'state',
            'url', 'user', 'user_vote', 'views', 'votes',
            'original_url', 'pdf_url', 'imported',
        )
        writable_fields = (
            'description', 'name', 'tags'
        )

        fields = writable_fields + read_only_fields

        extra_kwargs = {
            'user': {'lookup_field': 'netid'},
            'course': {'lookup_field': 'slug'},
        }

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

    def get_file_size(self, document):
        try:
            return document.original.size
        except (FileNotFoundError, NoSuchKey):
            return None


class ShortDocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'url', 'course')


class EditDocumentSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects, many=True)

    class Meta:
        model = Document

        fields = (
            'description', 'name', 'tags'
        )


class UploadDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    course = serializers.SlugRelatedField(slug_field='slug', queryset=Course.objects)
    tags = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects, many=True)

    class Meta:
        model = Document
        fields = ('name', 'description', 'file', 'course', 'tags')

    def create(self, validated_data):
        file = validated_data['file']
        name, extension = os.path.splitext(file.name)
        name = logic.clean_filename(name)

        if validated_data['name']:
            name = validated_data['name']

        document = logic.add_file_to_course(
            file=file,
            name=name,
            extension=extension,
            course=validated_data['course'],
            tags=validated_data['tags'],
            user=self.context['request'].user
        )

        document.description = validated_data['description']
        document.save()

        document.add_to_queue()
        return document


class DriveDocumentSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='slug', queryset=Course.objects)
    tags = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects, many=True)
    file_id = serializers.CharField()
    token = serializers.CharField()

    class Meta:
        model = Document
        fields = ('name', 'description', 'course', 'tags', 'file_id', 'token')

    def create(self, validated_data):
        tasks.import_drive_file.delay(
            name=validated_data['name'],
            file_id=validated_data['file_id'],
            token=validated_data['token'],
            netid=self.context['request'].user.netid,
            slug=validated_data['course'].slug,
            tags=[x.name for x in validated_data['tags']]
        )


class DropboxDocumentSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='slug', queryset=Course.objects)
    tags = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects, many=True)
    link = serializers.CharField()

    class Meta:
        model = Document
        fields = ('name', 'description', 'course', 'tags', 'link')

    def create(self, validated_data):
        tasks.import_dropbox_file.delay(
            name=validated_data['name'],
            url=validated_data['link'],
            netid=self.context['request'].user.netid,
            slug=validated_data['course'].slug,
            tags=[x.name for x in validated_data['tags']]
        )
