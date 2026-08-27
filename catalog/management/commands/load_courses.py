import json
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import CatalogEdition, Category, Course
from catalog.slug import normalize_slug

logger = logging.getLogger(__name__)


def get_category(edition, slug, name=None, parent=None, type=None):
    cat, created = Category.objects.get_or_create(
        edition=edition, slug=slug, defaults={"name": name, "type": type}
    )
    if created and parent:
        cat.parents.add(parent)
    return cat


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("csv/courses.json") as f:
            programs = json.load(f)

        with transaction.atomic():
            edition, _ = CatalogEdition.objects.get_or_create(
                status=CatalogEdition.Status.ACTIVE,
                defaults={"key": "current"},
            )

            logger.info("Temporarily set all courses as archived")
            for course in Course.objects.all():
                course.is_archive = True
                course.save()

            for program_slug, courses in programs.items():
                logger.info("Inserting %s courses from %s", len(courses), program_slug)
                category = get_category(edition, program_slug)
                for course in courses.values():
                    bloc = course["bloc"]
                    p = get_category(
                        edition,
                        f"{program_slug}-{bloc}",
                        name=f"Bloc {bloc}",
                        parent=category,
                        type=Category.CategoryType.BLOC,
                    )
                    c = Course.objects.get_or_create(
                        slug=normalize_slug(course["id"]),
                        defaults={
                            "slug": normalize_slug(course["id"]),
                            "name": course["title"],
                        },
                    )[0]
                    c.name = course["title"]
                    c.is_archive = False
                    c.save()
                    c.categories.add(p)
