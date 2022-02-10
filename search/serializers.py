from rest_framework import serializers

from catalog.models import Course


class CourseSearchSerializer(serializers.ModelSerializer):
    document_count = serializers.IntegerField(read_only=True, source="document__count")
    similarity = serializers.FloatField(read_only=True)
    rank = serializers.FloatField(read_only=True)

    class Meta:
        model = Course
        fields = ("name", "slug", "document_count", "rank", "similarity")
