from django.contrib.sitemaps import Sitemap
from django.db.models import Max

from catalog.models import Course


class CourseSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Course.objects.annotate(latest_doc_date=Max("document__created"))

    def lastmod(self, obj: Course):
        return obj.latest_doc_date
