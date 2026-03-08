from typing import Any

import logging

from django.core.management.base import BaseCommand
from django.db.models import Count

from catalog.models import Course

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        logger.info("Cleaning archives")
        empty_archived_courses = (
            Course.objects.filter(is_archive=True)
            .annotate(num_doc=Count("document"))
            .filter(num_doc=0)
        )
        logger.info("Deleting %s empty courses", len(empty_archived_courses))
        empty_archived_courses.delete()
