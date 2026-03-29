import csv
import logging

from django.core.management.base import BaseCommand

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        response = requests.get(
            "https://uv.ulb.ac.be/course/index.php?categoryid=1&browse=courses&perpage=1&page=0"
        )
        soup = BeautifulSoup(response.content, "html.parser")
        dropdown = soup.find("select", {"name": "categoryid"})
        options = dropdown.find_all("option")

        courses = []
        fails = []
        logger.info("Found %s options", len(options))  # debug car verbeux
        for option in options:
            logger.debug("..%s", option.text)
            value = option["value"]
            response = requests.get(
                f"https://uv.ulb.ac.be/course/index.php?categoryid={value}&browse=courses&perpage=1000&page=0"
            )
            soup = BeautifulSoup(response.content, "html.parser")

            course_divs = soup.find_all("div", {"class": "coursebox"})
            logger.info("Found %s in %s", len(courses), option.text)

            for course in course_divs:
                try:
                    slug, rest = course.text.split(" - ", 1)
                    title, year = rest.rsplit(" - ", 1)
                    courses.append((slug, title, year))
                except:  # noqa
                    fails.append(course.text)

        logger.info("Found %s and failed to parse %s", len(courses), len(fails))
        with open("csv/uv_courses.csv", "w") as fd:
            writer = csv.writer(fd)
            for course in courses:
                writer.writerow(course)
