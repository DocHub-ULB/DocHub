from documents.models import Document, Page
from rest_framework import serializers


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    page_set = serializers.HyperlinkedIdentityField(view_name='document-page-set')

    class Meta:
        model = Document
        fields = (
            'id', 'name', 'url', 'page_set', 'description',
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
