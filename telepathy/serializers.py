from rest_framework import serializers

from telepathy.models import Thread, Message
from users.serializers import SmallUserSerializer


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    user = SmallUserSerializer()

    class Meta:
        model = Message
        fields = ('id', 'user', 'created', 'edited', 'thread', 'text')


class ThreadSerializer(serializers.HyperlinkedModelSerializer):
    user = SmallUserSerializer()
    message_set = MessageSerializer(many=True)

    class Meta:
        model = Thread
        fields = ('id', 'name', 'user', 'created', 'edited', 'course', 'document', 'url', 'message_set')

        extra_kwargs = {
            'course': {'lookup_field': 'slug'},
        }


class SmallThreadSerializer(serializers.HyperlinkedModelSerializer):
    user = SmallUserSerializer()

    class Meta:
        model = Thread
        fields = ('id', 'name', 'user', 'created', 'edited', 'course', 'document', 'url')

        extra_kwargs = {
            'course': {'lookup_field': 'slug'},
        }
