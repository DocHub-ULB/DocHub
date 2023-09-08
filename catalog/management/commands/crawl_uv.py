import csv

from django.core.management.base import BaseCommand

import requests
from bs4 import BeautifulSoup


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
        print(f"Found {len(options)} options")
        for option in options:
            print(f"..{option.text}")
            value = option["value"]
            response = requests.get(
                f"https://uv.ulb.ac.be/course/index.php?categoryid={value}&browse=courses&perpage=1000&page=0"
            )
            soup = BeautifulSoup(response.content, "html.parser")

            course_divs = soup.find_all("div", {"class": "coursebox"})
            print(f"Found {len(courses)} in {option.text}")

            for course in course_divs:
                try:
                    slug, rest = course.text.split(" - ", 1)
                    title, year = rest.rsplit(" - ", 1)
                    courses.append((slug, title, year))
                except:  # noqa
                    fails.append(course.text)

        print(f"Found {len(courses)} and failed to parse {len(fails)}")
        with open("csv/uv_courses.csv", "w") as fd:
            writer = csv.writer(fd)
            for course in courses:
                writer.writerow(course)
