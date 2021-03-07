from typing import Dict

import json
from os import path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

import requests
import yaml
from bs4 import BeautifulSoup
from sentry_sdk import capture_exception

from catalog.models import Category, Course
from catalog.slug import Slug


class Command(BaseCommand):
    help = 'Loads a new courses tree into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hit-ulb',
            action='store_true',
            dest='hitulb',
            default=False,
            help='Hit ULB servers to get courses names from slugs'
        )
        parser.add_argument(
            dest='tree_file',
            help='Path to the .yaml tree file',
            metavar="TREE_FILE"
        )

    LOCAL_CACHE: Dict[str, str] = {}

    def handle(self, *args, **options):
        self.stdout.write('Loading tree ... ')

        if not options['hitulb']:
            f = path.join(settings.BASE_DIR, 'catalog/management/localcache.json')
            with open(f) as fd:
                self.LOCAL_CACHE = json.loads(fd.read())

        with open(options['tree_file']) as fd:
            tree = yaml.safe_load(fd)

        with transaction.atomic():
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
                    try:
                        slug = Slug.from_dochub(tree)
                        r = requests.get(f"https://www.ulb.be/fr/programme/{slug.catalog}")
                        soup = BeautifulSoup(r.text, "html5lib")
                        name = soup.find("h1").text.strip()
                    except Exception as e:
                        print("Slug %s failed" % tree)
                        capture_exception(e)
                        name = "Unknown course in cache"
                course = Course.objects.create(name=name, slug=tree)
            course.categories.add(father)

        if isinstance(tree, list):
            for subtree in tree:
                self.create_tree(father, subtree)
