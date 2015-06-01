from users.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'netid',
            'name',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_representative',
            'is_academic'
        )
