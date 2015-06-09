from documents.models import Document, Page
from rest_framework import serializers
# from rest_framework_extensions.fields import ResourceUriField


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    # page_set = ResourceUriField(view_name='page-set-list', read_only=True, lookup_field='document')
    # page_set = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='page-set', lookup_field='document')

    class Meta:
        model = Document
        fields = (
            'id', 'name', 'url', 'description',
            'user', 'pages', 'date', 'views',
            'downloads', 'state', 'md5',
        )

        extra_kwargs = {
            'user': {'lookup_field': 'netid'},
        }


class ShortDocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'url')


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
