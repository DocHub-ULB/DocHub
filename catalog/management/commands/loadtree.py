# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from django.core.management.base import BaseCommand
import json
from os import path
from optparse import make_option

from www.settings import BASE_DIR
from catalog.models import Category, Course
from libulb.catalog.course import Course as ULBCourse


class Command(BaseCommand):
    help = 'Loads a new courses tree into the database'

    option_list = BaseCommand.option_list + (
        make_option(
            '--hit-ulb',
            action='store_true',
            dest='hitulb',
            default=False,
            help='Hit ULB servers to get courses names from slugs'
        ),
        make_option(
            '--tree',
            dest='tree_file',
            default=path.join(BASE_DIR, "catalog/management/devtree.json"),
            help='Use a tree file. Defaults to catalog/management/devtree.json'
        ),
    )

    LOCAL_CACHE = {}
    YEAR = "201516"

    def handle(self, *args, **options):
        if not options['hitulb']:
            f = path.join(BASE_DIR, 'catalog/management/localcache.json')
            self.LOCAL_CACHE = json.loads(open(f).read())

        tree = json.loads(open(options['tree_file']).read())

        Category.objects.all().delete()
        self.add_category(None, tree)

    def add_category(self, father, category):
        cat = Category.objects.create(
            name=category["name"],
            slug=category.get("slug", ""),
            parent=father
        )

        for children in category.get("children", []):
            self.add_category(cat, children)

        for slug in category.get("courses", []):
            try:
                course = Course.objects.get(slug=slug)
            except Course.DoesNotExist:
                if self.LOCAL_CACHE:
                    name = self.LOCAL_CACHE.get(slug, "Unknown course in cache")
                else:
                    ulbCourse = ULBCourse.get_from_slug(slug, self.YEAR)
                    name = ulbCourse.name
                course = Course.objects.create(
                    name=name,
                    slug=slug,
                    description=""
                )

            course.categories.add(cat)
