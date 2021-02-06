from django.contrib.sitemaps import Sitemap

from documents.models import Document


class DocumentSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Document.objects.filter(hidden=False)

    def lastmod(self, obj):
        return obj.edited
