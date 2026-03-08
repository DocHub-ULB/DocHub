import csv
import json
import logging

from django.core.management.base import BaseCommand
from django.db.models import Count

from catalog.models import Course
from catalog.slug import normalize_slug

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("csv/courses.json") as f:
            programs = json.load(f)

        new_slugs = set()
        slug2name = {}
        for _program_slug, courses in programs.items():
            for course in courses.values():
                slug = normalize_slug(course["id"])
                new_slugs.add(slug)
                slug2name[slug] = course["title"]

        courses = Course.objects.all().annotate(num_docs=Count("document"))
        orphans = courses.exclude(slug__in=new_slugs)
        empty_orphans = orphans.filter(num_docs=0)

        orphans_to_fix = orphans.exclude(num_docs=0)
        logger.info(
            "%s empty orphans and %s orphans with documents",
            empty_orphans.count(),
            orphans_to_fix.count(),
        )
        with open("csv/orphans.csv", "w") as fd:
            writer = csv.writer(fd)
            for course in orphans_to_fix:
                writer.writerow((course.slug, course.name, course.num_docs))

        with open("csv/new_slugs.csv", "w") as fd:
            writer = csv.writer(fd)
            for slug in new_slugs:
                writer.writerow((slug, slug2name[slug]))
