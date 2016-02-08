# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'color', 'name')
