from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Count

from catalog.models import Course


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        print("Cleaning archives")
        empty_archived_courses = (
            Course.objects.filter(is_archive=True)
            .annotate(num_doc=Count("document"))
            .filter(num_doc=0)
        )
        print("Deleting %s empty courses" % len(empty_archived_courses))
        empty_archived_courses.delete()
