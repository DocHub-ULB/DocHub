# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from getpass import getpass, getuser
from optparse import make_option
from graph.models import Category, Course, CourseInfo
from telepathy.models import Thread, Message


class Command(BaseCommand):
    help = 'Initialize p402 for developpment'
    option_list = BaseCommand.option_list + (
        make_option('--username', action='store', dest='username', default=None, help='default username'),
        make_option('--password', action='store', dest='password', default=None, help='default password'),
        make_option('--first-name', action='store', dest='first_name', default=None, help='default first name'),
        make_option('--last-name', action='store', dest='last_name', default=None, help='default last name'),
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating user\n')
        user = User()
        username = raw_input("Username (default: %s): " % getuser()) if options["username"] is None else options["username"]
        if not username:
            username = getuser()
        user.username = username
        password = getpass("Password (default: 'test'): ") if options["password"] is None else options["password"]
        if not password:
            password = 'test'
        first_name = raw_input("Firstname (default: John): ") if options["first_name"] is None else options["first_name"]
        if not first_name:
            first_name = "John"
        last_name = raw_input("Lastname (default: Smith): ") if options["last_name"] is None else options["last_name"]
        if not last_name:
            last_name = "Smith"
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.save()
        profile = user.get_profile()
        profile.name = first_name + " " + last_name
        profile.email = 'test@mouh.com'
        profile.save()

        self.stdout.write('Adding base data ...\n')
        c1 = Course.objects.create(slug='info-f-666', name='Hell Informatique',
                                   description='Hell Computer Science course')
        c2 = Course.objects.create(slug='info-f-777', name='Over Math',
                                   description='New math course based on fuzzy axiomes')
        c3 = Course.objects.create(slug='info-f-888', name='AlgoSimplex',
                                   description='Les simplex dans tout leurs etats')
        c4 = Course.objects.create(slug='info-f-999', name='Support Vector Machines',
                                   description='Neural Networks are outdated, use SVM!')

        CourseInfo.objects.create(user=profile,
                                  course=c1,
                                  infos = """[
            {    name: "general", values: [
                                        {name: 'Professeur', value:'B. Lecharlier'},
                                        {name: 'Langue', value:'Francais'},
                                        {name: 'Syllabus', value:'Informatique Ba1'},
                                        {name: 'ECTS', value:'5'},
                                    ],
            },
        ]""")

        CourseInfo.objects.create(user = profile,
                                  course=c1,
                                  infos = """[
            {    name: "general", values: [
                                        {name: 'Professeur', value:'B. Lecharlier'},
                                        {name: 'Langue', value:'Francais'},
                                        {name: 'Syllabus', value:'Informatique Ba1'},
                                        {name: 'ECTS', value:'5'},
                                    ],
            },
            {    name: "exam", values: [
                                      {name: 'Difficultes', values:'Language noyaux'},
                                     ],
            },
        ]""")

        facs = Category.objects.create(name='Faculty', description='Root node w/ category')
        sciences = Category.objects.create(name='Sciences', description='Fac de sciences')
        polytech = Category.objects.create(name='Polytech', description='Polytech')
        info = Category.objects.create(name='Computing', description='Section INFO')
        math = Category.objects.create(name='Math', description='Section Math')
        phys = Category.objects.create(name='Physique', description='Section Physique')
        ba1 = Category.objects.create(name='BA-INFO 1', description='Section INFO 1')
        ba2 = Category.objects.create(name='BA-INFO 2', description='Section INFO 2')
        ba3 = Category.objects.create(name='BA-INFO 3', description='Section INFO 3')

        facs.sub_categories.add(sciences)
        facs.sub_categories.add(polytech)
        sciences.sub_categories.add(info)
        sciences.sub_categories.add(math)
        sciences.sub_categories.add(phys)
        info.sub_categories.add(ba1)
        info.sub_categories.add(ba2)
        info.sub_categories.add(ba3)

        info.contains.add(c1)
        info.contains.add(c2)
        ba1.contains.add(c3)
        ba1.contains.add(c4)

        thread = Thread.objects.create(user=profile, referer_content='Course', referer_id=c1.id, subject="A JSON stringifier goes in the opposite direction, converting JavaScript data structures into JSON text. JSON does not support cyclic data structures, so be careful to not give cyclical structures to the JSON stringifier. http://www.json.org/js.html", tags='["info pratique"]')
        Message.objects.create(user=profile, thread=thread, text='Type "copyright", "credits" or "license" for more information.')
