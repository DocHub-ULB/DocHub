# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.core.management.base import BaseCommand
from django.core.files import File
import csv

from users.models import User
from catalog.models import Course
from documents import logic


class Command(BaseCommand):

    help = 'Import documents from a csv'

    def add_arguments(self, parser):
        parser.add_argument(action='store', dest='path', default='', help='Documents path')
        parser.add_argument('--user', action='store', dest='username', default='tverhaegen', help='user owning the documents')

    def handle(self, *args, **options):
        netid = options["username"]
        self.stdout.write('Looking for user "{}"'.format(netid))

        user = User.objects.filter(netid=netid).first()
        if user is None:
            self.stdout.write('Could not find user.')
            return

        path = options['path']
        self.stdout.write('Reading csv from "{}"'.format(path))
        if not os.path.exists(path):
            self.stdout.write("CSV does not exist")
            return

        with open(path) as fd:
            reader = csv.DictReader(fd)

            for row in reader:
                try:
                    import_document(row, user)
                    self.stdout.write('.', ending='')
                    self.stdout.flush()
                except:
                    print('Fail for %r' % row)


def import_document(row, user):
    """row has keys ['name', 'slug', 'path']"""
    path = row['path']
    filename = os.path.split(path)[1]
    _, extension = os.path.splitext(filename)

    name = row['name']
    name = logic.clean_filename(name)

    course = Course.objects.get(slug=row['slug'])

    with open(path, 'rb') as fd:
        document = logic.add_file_to_course(
            file=File(fd),
            name=name,
            extension=extension,
            course=course,
            tags=[],
            user=user
        )

    document.tag_from_name()
    document.add_to_queue()
