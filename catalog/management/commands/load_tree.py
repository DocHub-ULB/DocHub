from typing import Any

import json

from django.core.management.base import BaseCommand
from django.db import transaction

from slugify import slugify

from catalog.models import Category

STOP = {"d'", "de", "du", "et", "l'", "la", "le", "les"}


def is_level0(name):
    if "Université" in name:
        return True
    if "Haute Ecole" in name:
        return True
    return False


def slugify0(name):
    abbrev = {
        "Mons": "umons",
        "Namur": "unamur",
        "Liège": "ulg",
        "Louvain": "ucl",
        "Charlemagne": "hec",
        "Prigogine": "HELB",
        "Saint-Louis": "usaintlouis",
    }
    for long, short in abbrev.items():
        if long in name:
            return short
    return slugify(name, stopwords=STOP)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        with open("csv/programs.json") as f:
            programs = json.load(f)

        faculties: dict[str, str] = {}  # name: color
        for program in programs:
            for faculty in program["faculty"]:
                faculties[faculty["name"]] = faculty["color"]

        level0 = {k: v for k, v in faculties.items() if is_level0(k)}
        level1 = {k: v for k, v in faculties.items() if not is_level0(k)}

        with transaction.atomic():
            if Category.objects.filter(slug="archives").first():
                print("We already have archives, deleting the non-archives")
                Category.objects.filter(is_archive=False).delete()
            else:
                print("Archiving old categories")
                old_ulb = Category.objects.filter(slug="ULB").get()
                old_ulb.name = "Archives"
                old_ulb.slug = "archives"
                old_ulb.type = Category.CategoryType.UNIVERSITY
                old_ulb.save()

                Category.objects.all().update(is_archive=True)

                print("Fixing old faculties")
                for child in old_ulb.children.all():
                    child.type = Category.CategoryType.FACULTY
                    child.save()

            # Level 0
            print("Creating level 0")
            ULB = Category.objects.create(
                name="Université Libre de Bruxelles",
                slug="ULB",
                type=Category.CategoryType.UNIVERSITY,
            )

            for name, _color in level0.items():
                Category.objects.create(
                    name=name,
                    slug=slugify0(name),
                    type=Category.CategoryType.UNIVERSITY,
                )

            # Level 1
            print("Creating level 1")
            for name, _color in level1.items():
                slug = (
                    name.removeprefix("Faculté de ")
                    .removeprefix("Faculté d'")
                    .removeprefix("Faculté des ")
                    .removeprefix("Institut d'")
                    .removeprefix("Institut des")
                )
                c = Category.objects.create(
                    name=name,
                    slug=slugify(slug, stopwords=STOP),
                    type=Category.CategoryType.FACULTY,
                )
                c.parents.add(ULB)

            # Programs
            print("Adding all programs")
            for program in programs:
                if "bachelier" in program["name"].lower() or program["slug"].startswith(
                    "BA"
                ):
                    program_type = Category.CategoryType.BACHELOR
                elif "spécialisation" in program["name"].lower() or program[
                    "slug"
                ].startswith("MS"):
                    program_type = Category.CategoryType.MASTER_SPECIALIZATION
                elif "master" in program["name"].lower() or program["slug"].startswith(
                    "MA"
                ):
                    program_type = Category.CategoryType.MASTER
                elif "certificat" in program["name"].lower():
                    program_type = Category.CategoryType.CERTIFICATE
                elif "agrégation" in program["name"].lower():
                    program_type = Category.CategoryType.AGGREGATION
                else:
                    program_type = None

                c = Category.objects.create(
                    name=program["name"],
                    slug=program["slug"],
                    type=program_type,
                )

                for faculty in program["faculty"]:
                    parent = Category.objects.get(name=faculty["name"])
                    c.parents.add(parent)

            print("Done")
