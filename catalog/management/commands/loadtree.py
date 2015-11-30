# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from django.core.management.base import BaseCommand
import json
from os import path
from optparse import make_option
import yaml

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
            help='Path to the .yaml tree file'
        ),
    )

    LOCAL_CACHE = {}
    YEAR = "201516"

    def handle(self, *args, **options):
        self.stdout.write('Loading tree ... ')

        if not options['hitulb']:
            f = path.join(BASE_DIR, 'catalog/management/localcache.json')
            self.LOCAL_CACHE = json.loads(open(f).read())

        tree = yaml.load(open(options['tree_file']))

        Category.objects.all().delete()

        root = Category.objects.create(
            name="ULB",
            slug="root",
            parent=None,
        )

        self.create_tree(root, tree)

        self.stdout.write('Done \n')

    def create_tree(self, father, tree):
        if isinstance(tree, dict):
            for key, value in tree.items():
                cat = Category.objects.create(
                    name=key,
                    slug="",
                    parent=father
                )
                self.create_tree(cat, value)

        if isinstance(tree, str):
            try:
                course = Course.objects.get(slug=tree)
            except Course.DoesNotExist:
                if self.LOCAL_CACHE:
                    name = self.LOCAL_CACHE.get(tree, "Unknown course in cache")
                else:
                    ulbCourse = ULBCourse.get_from_slug(tree, self.YEAR)
                    name = ulbCourse.name
                course = Course.objects.create(name=name, slug=tree, description="")
            course.categories.add(father)

        if isinstance(tree, list):
            for subtree in tree:
                self.create_tree(father, subtree)
