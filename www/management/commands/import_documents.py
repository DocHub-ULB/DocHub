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
from optparse import make_option

from users.models import User
from graph.models import Course
from documents.models import Document
from www import settings

import os
import glob
import shutil

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
        'tp':  'tp',
        'syl': 'syllabus',
        'cor': 'corrigé',
        'for': 'formulaire',
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
        
        for doc in documents[0]:
            self.stdout.write('.', ending='')
            self.stdout.flush()
            name = os.path.split(doc)[1]
            spli = name.split(":",1)
            if len(spli) == 1:
                name = spli[0]
                tags = []
            else:
                tags, name = spli
                tags = tags.split(',')
                tags = map(lambda x: self.tags[x.lower()], tags)

            name = name.replace("_", " ")
            name, extension = os.path.splitext(name)
            extension = extension[1:]

            dbdoc = Document.objects.create(user=user, name=name, state="pending")
            course.add_child(dbdoc)
            if not len(tags) == 0:
                dbdoc.add_keywords(*tags)

            if not os.path.exists(settings.TMP_UPLOAD_DIR):
                os.makedirs(settings.TMP_UPLOAD_DIR)

            tmp_file = os.path.join(settings.TMP_UPLOAD_DIR, "{}.{}".format(dbdoc.id, extension))
            source = 'file://' + tmp_file
            dbdoc.source = source

            shutil.copy(doc, tmp_file)

            dbdoc.save()





