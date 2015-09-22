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
from django.core.files import File
from optparse import make_option
import uuid

from users.models import User
from catalog.models import Course
from documents.models import Document
from tags.models import Tag

import os
import glob


class Command(BaseCommand):

    help = 'Import document in a course'
    option_list = BaseCommand.option_list + (
        make_option('--path', action='store', dest='path', default='', help='Documents path'),
        make_option('--user', action='store', dest='username', default='', help='user owning the documents'),
        make_option('--course', action='store', dest='course_slug', default='', help='course slug'),

    )

    tags = {
        'off': 'officiel',
        'ref': 'référence',
        'sli': 'slides',
        'res': 'résumé',
        'exa': 'examen',
        'tp': 'tp',
        'syl': 'syllabus',
        'cor': 'corrigé',
        'corr': 'corrigé',
        'for': 'formulaire',
        'sol': 'corrigé',
        'lab': 'laboratoire',
    }

    def handle(self, *args, **options):
        netid = options["username"]
        self.stdout.write('Looking for user "{}"'.format(netid))

        users = User.objects.filter(netid=netid)
        if len(users) == 0:
            self.stdout.write('Could not find user.')
            return None
        user = users[0]

        slug = options["course_slug"]
        self.stdout.write('Looking for course "{}"'.format(slug))

        courses = Course.objects.filter(slug=slug)
        if len(courses) == 0:
            self.stdout.write('Could not find course.')
            return None
        course = courses[0]

        path = options['path']
        self.stdout.write('Gathering documents in "{}"'.format(path))
        if not os.path.exists(path):
            self.stdout.write("Path does not exist")
            return None

        documents = glob.glob(os.path.join(path, "*.*"))

        for doc in documents:
            self.stdout.write('.', ending='')
            self.stdout.flush()
            name = os.path.split(doc)[1]
            spli = name.split(":", 1)
            if len(spli) == 1:
                name = spli[0]
                tags = []
            else:
                tags, name = spli
                tags = tags.split(',')
                try:
                    tags = map(lambda x: self.tags[x.lower()], tags)
                except KeyError:
                    tags = []

            name = name.replace("_", " ")
            name, extension = os.path.splitext(name)

            dbdoc = Document.objects.create(
                user=user,
                name=name,
                state="PREPARING",
                file_type=extension,
                course=course,
            )

            for tag in tags:
                dbdoc.tags.add(Tag.objects.get_or_create(name=tag)[0])

            dbdoc.original.save(str(uuid.uuid4()) + extension, File(open(doc)))

            dbdoc.state = 'READY_TO_QUEUE'
            dbdoc.save()

            dbdoc.add_to_queue()
