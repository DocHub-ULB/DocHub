import csv
import json

from django.core.management.base import BaseCommand
from django.db.models import Count

from catalog.models import Course
from catalog.slug import normalize_slug


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("csv/courses.json") as f:
            programs = json.load(f)

        new_slugs = set()
        for _program_slug, courses in programs.items():
            for course in courses.values():
                slug = normalize_slug(course["id"])
                new_slugs.add(slug)

        courses = Course.objects.all().annotate(num_docs=Count("document"))
        orphans = courses.exclude(slug__in=new_slugs)
        empty_orphans = orphans.filter(num_docs=0)

        orphans_to_fix = orphans.exclude(num_docs=0)
        print(
            f"{empty_orphans.count()} empty orphans and {orphans_to_fix.count()} orphans with documents"
        )

        with open("csv/orphans.csv", "w") as fd:
            writer = csv.writer(fd)
            for course in orphans_to_fix:
                writer.writerow((course.slug, course.name, course.num_docs))

        with open("csv/new_slugs.csv", "w") as fd:
            writer = csv.writer(fd)
            for slug in new_slugs:
                writer.writerow((slug,))
