import re

# from django.db.models import Q
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

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

    vector = SearchVector('slug', config='french') + SearchVector('name', config='french')
    query = SearchQuery(string, config='french')

    return Course.objects.annotate(
        rank=SearchRank(vector, query),
        similarity=TrigramSimilarity('name', string),
        document__count=Count('document'),
    ).filter(similarity__gt=0.2).order_by('-rank', '-similarity', '-document__count')
