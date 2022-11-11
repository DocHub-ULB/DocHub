import json
import os

from django.utils.text import slugify

from catalog.models import Category, Course
from www.logger_settings import logger

with open("catalog/management/parser/data/tree.json") as tree_file:
    tree = json.load(tree_file)

a = 0
ulb, _created = Category.objects.get_or_create(name="ULB", slug="root")
for fac_name, fac_info in tree["ULB"].items():
    logger.debug(fac_name)
    fac_obj, _created = Category.objects.get_or_create(
        name=fac_name, slug=slugify(fac_name), description=fac_info["color"]
    )
    fac_obj.parents.add(ulb)

    for program_slug, program_info in fac_info["programs"].items():
        logger.debug(" ", program_info["name"])
        program_obj, _created = Category.objects.get_or_create(
            name=program_info["name"], slug=program_slug
        )
        program_obj.parents.add(fac_obj)

        for bloc_name, bloc_info in program_info["blocs"].items():
            logger.debug("   ", bloc_name)
            bloc_obj, _created = Category.objects.get_or_create(
                name=f"Bloc {bloc_name}",
                slug=f"{program_slug}-bloc-{bloc_name}",
            )
            bloc_obj.parents.add(program_obj)

            for course_mnemo, course_info in bloc_info["courses"].items():
                a += 1
                logger.debug(str(a).zfill(4), course_info["title"])
                course_obj, _created = Course.objects.get_or_create(slug=course_mnemo)
                if _created:
                    course_obj.name = course_info["title"]
                    course_obj.description = f"lecturer(s): {course_info['lecturers']}, quadri: {course_info['quadri']}, mandatory: {course_info['mandatory']}"
                else:
                    course_obj.description += f"\n\nlecturer(s): {course_info['lecturers']}, quadri: {course_info['quadri']}, mandatory: {course_info['mandatory']}"
                course_obj.categories.add(bloc_obj)
                course_obj.save()
