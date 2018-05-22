"""
Import documents downloaded with improved-goggles into Dochub.

See also https://github.com/C4ptainCrunch/improved-goggles
"""

import sqlite3
import re
import os
from os import path
from glob import glob
from django.db import transaction
from django.core.files import File
from django.core.management.base import BaseCommand
from django.conf import settings

import documents.logic as logic
from users.models import User
from catalog.models import Course


class Command(BaseCommand):
    help = 'Import documents downloaded with improved-goggles into Dochub'

    def create_courses(self, courses):
        res = {}
        for c in courses:
            slug = c['slug'].lower()
            if not re.match(r'([A-Za-z]+)-([A-Za-z])-(\d+)', slug):
                self.stdout.write(self.style.ERROR(
                    'Course %s has not the right format' % slug
                ))

            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={'name': c['name']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created %s' % course))
            elif self.verbose:
                self.stdout.write('Reusing %s' % course)
            res[c['id']] = course
        return res

    def create_documents(self, courses, documents):
        for doc in documents:
            if not doc['download_id']:
                if self.verbose:
                    self.stdout.write(self.style.WARNING(
                        'SKIP: not downloaded yet: %s' % doc
                    ))
                continue

            course = courses[doc['course_id']]
            pattern = path.join(self.dump_dir, str(doc['download_id'])) + '.*'
            matching_files = glob(pattern)
            if len(matching_files) != 1:
                if self.verbose:
                    self.stdout.write(self.style.WARNING(
                        'SKIP: no single file with id=%d' % doc['download_id']
                    ))
                continue

            srckey = self.source + '?document_id=%d' % doc['document_id']
            filename = matching_files[0]
            _, extension = os.path.splitext(filename)

            if extension in settings.REJECTED_FILE_FORMATS:
                if self.verbose:
                    self.stdout.write(self.style.WARNING(
                        'REJECT: %s has a wrong format (%s)' % (doc['download_id'], extension)
                    ))
                continue

            name = logic.clean_filename(doc['name'])

            document = logic.add_file_to_course(
                file=File(open(filename, 'rb')),
                name=name,
                extension=extension,
                course=course,
                tags=[],
                user=self.user,
                import_source=srckey,
            )
            if document:
                document.add_to_queue()
                self.stdout.write(self.style.SUCCESS(
                    'Enqueued "%s" (pk %s) for processing' % (document, document.id)
                ))

    def add_arguments(self, parser):
        parser.add_argument('respublicae_db', type=str,
                            help="Path to respublicae sqlite3 dump")
        parser.add_argument('-u', '--user', action='store', required=True,
                            dest='netid', type=str, default=None,
                            help=('The inserted documents shall belong to '
                                  'this Dochub user (NetID)'))
        parser.add_argument('-d', '--dump_directory', action='store',
                            required=True, dest='dump_dir', default=None,
                            help=('Directory containing the dump of '
                                  'downloaded files'))
        parser.add_argument('-s', '--source', action='store',
                            dest='source', default='respublicae',
                            help='Identifier for the import_source')

    def handle(self, *args, **options):
        def query(table, columns, limit=None):
            with sqlite3.connect(options['respublicae_db']) as conn:
                cur = conn.cursor()

                # Never do this at home kids !!! https://xkcd.com/327/
                q = "SELECT %s FROM %s" % (', '.join(columns), table)
                if limit is not None:
                    q += ' LIMIT %d' % limit
                cur.execute(q)
                return [dict(zip(columns, row)) for row in cur.fetchall()]

        if not path.exists(options['dump_dir']):
            raise ValueError(
                "Dump directory %s does not exists" % options['dump_dir']
            )
        self.verbose = options['verbosity'] > 1
        self.dump_dir = options['dump_dir']
        self.user = User.objects.get(netid=options['netid'])
        self.source = options['source']

        with transaction.atomic():
            courses = self.create_courses(query('course', [
                'id',
                'name',
                'slug'
            ]))
            self.create_documents(courses, query('document', [
                'document_id',
                'course_id',
                'download_id',
                'was_downloaded',
                'name'
            ]))
