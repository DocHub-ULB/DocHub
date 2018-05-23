import re

from django.db.models import Q
from django.db.models import Count

from catalog.models import Course


def search_course(string):

    slug_matches = []
    slug_matches += re.findall(r'([A-Za-z]+)-([A-Za-z])(\d+)', string)
    slug_matches += re.findall(r'([A-Za-z]+)-([A-Za-z])-(\d+)', string)

    if slug_matches:
        fac, middle, digits = slug_matches[0]
        slug = "%s-%s-%s" % (fac, middle, digits)
        slug = slug.lower()
        exact_slug = Course.objects.filter(slug__iexact=slug).annotate(Count('document'))
        if len(exact_slug) > 0:
            return exact_slug

    q = Q(slug__search=string) | Q(name__search=string) | Q(name__icontains=string)
    return Course.objects.filter(q).annotate(Count('document')).order_by("-document__count")
