from actstream.models import Action
from rest_framework import serializers

from catalog.models import Course
from documents.models import Document
from users.serializers import SmallUserSerializer


class PolymorphicSerializer(serializers.ModelSerializer):
    obj_type = serializers.SerializerMethodField()

    def get_obj_type(self, obj):
        return str(type(obj).__name__).lower()


class VeryShortDocumentSerializer(PolymorphicSerializer):
    class Meta:
        model = Document
        fields = ('name', 'pages', 'obj_type', 'id')


class VeryShortCourseSerializer(PolymorphicSerializer):

    class Meta:
        model = Course
        fields = ('slug', 'name', 'obj_type')


class GenericRelatedField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, Document):
            serializer = VeryShortDocumentSerializer(value)
        elif isinstance(value, Course):
            serializer = VeryShortCourseSerializer(value)
        else:
            raise Exception("Neither a Dcoument nor Course instance! %s" % type(value))
        return serializer.data


class FeedSerializer(serializers.ModelSerializer):
    actor = SmallUserSerializer(read_only=True)
    action_object = GenericRelatedField(read_only=True)
    target = GenericRelatedField(read_only=True)

    class Meta:
        model = Action
        fields = ('actor', 'verb', 'action_object', 'target')
