# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from users.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key', 'created')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    avatar = serializers.CharField(source='get_photo')
    token = TokenSerializer(source="auth_token")

    class Meta:
        model = User
        fields = (
            'id',
            'url',
            'netid',
            'name',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_representative',
            'is_academic',
            'avatar',
            'token'
        )

        extra_kwargs = {
            'url': {'lookup_field': 'netid'}
        }


class SmallUserSerializer(serializers.ModelSerializer):
    avatar = serializers.CharField(source='get_photo')

    class Meta:
        model = User
        fields = (
            'name',
            'first_name',
            'last_name',
            'is_representative',
            'avatar',
        )

        extra_kwargs = {
            'url': {'lookup_field': 'netid'}
        }
