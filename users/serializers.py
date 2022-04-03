from rest_framework import serializers
from rest_framework.authtoken.models import Token

from catalog.models import Course
from users.models import User


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ("key", "created")


class FollowedCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("slug", "name")


class UserSerializer(serializers.HyperlinkedModelSerializer):
    token = TokenSerializer(source="auth_token")
    followed_courses = serializers.SerializerMethodField()

    def get_followed_courses(self, obj):
        courses = obj.following_courses
        return FollowedCourseSerializer(courses, many=True).data

    class Meta:
        model = User
        fields = (
            "id",
            "url",
            "netid",
            "name",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_representative",
            "is_academic",
            "token",
            "followed_courses",
        )

        extra_kwargs = {"url": {"lookup_field": "netid"}}


class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "name",
            "first_name",
            "last_name",
            "is_representative",
        )

        extra_kwargs = {"url": {"lookup_field": "netid"}}
