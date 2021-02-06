from django.contrib.sitemaps import Sitemap
from catalog.models import Course


class CourseSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Course.objects.prefetch_related('document_set')

    def lastmod(self, obj: Course):
        lastdoc = obj.document_set.order_by("-created").first()
        if lastdoc:
            return lastdoc.created
