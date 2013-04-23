# -*- coding: utf-8 -*-
# Copyright 2013, Titou. All rights reserved.
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
from datetime import datetime
import json

class Command(BaseCommand):
    drops = [u"Niveau dans le cycle*", u"Lieu d’enseignement*", u"Cycle*",
             u"Faculté gestionnaire*", u"Institution organisatrice*",
             u"Langue d'évaluation*", u"Horaire*", u"Discipline*",
             u"Contenu du cours*", u"Priorités de l'enseignant",
             u"Autres pré-requis", u"Objectifs du cours et compétences visées*",
             u"Syllabus*"]
    NOW = datetime.now()
    USER = None

    to_ulb = lambda self,n: n[0:4].upper() + "_" + n[5].upper() + n[7:]

    help = 'Initialize p402 for developpment'
    option_list = BaseCommand.option_list + (
        make_option('--username', action='store', dest='username', default=None, help='default username'),
        make_option('--password', action='store', dest='password', default=None, help='default password'),
        make_option('--first-name', action='store', dest='first_name', default=None, help='default first name'),
        make_option('--last-name', action='store', dest='last_name', default=None, help='default last name'),
    )

    def createCourse(self, parentNode, slug):
        try:
            course = Course.objects.get(slug=slug)
        except:
            ULBInfos = self.courseList[self.to_ulb(slug)]
            name = slug.upper()
            infos = []
            for cat, content in ULBInfos.iteritems():
                if content == "" or cat in self.drops:
                    continue
                if cat == u"Construction de la note, pondération des différentes activités*":
                    cat = "Note"
                if cat == u"Langue d'enseignement*":
                    cat = "Langue"
                if cat == u"Intitulé du cours*":
                    cat = "Nom"
                    name = content
                if cat[-1] == "*":
                    cat = cat[:-1]
                infos.append({"name": cat, "value": content})
            course = Course.objects.create(
                name=name, slug=slug,
                description=json.dumps(ULBInfos)
            )
            courseMeta = CourseInfo.objects.create(
                course=course, infos=json.dumps(infos),
                date=self.NOW, user=self.USER
            )
        parentNode.add_child(course)
        self.stdout.write('.')
        self.stdout.flush()



    def walk(self, jsonTree, parentNode):
        for key in jsonTree:
            val = jsonTree[key]
            if key.lower() == 'course':
                for slug in val:
                    self.createCourse(parentNode, slug)
            else:
                category = Category.objects.create(name=key, description="Magic !")
                parentNode.add_child(category)
                self.stdout.write('#')
                self.stdout.flush()
                self.walk(val, category)


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
        profile.email = 'gaston@dupuis.be'
        profile.save()
        
        #Second user for tests
        user2 = User()
        user2.username="blabevue"
        user2.first_name="Bertrand"
        user2.last_name="Labévue"
        user2.set_password(password)
        user2.save()
        profile2 = user2.get_profile()
        profile2.name = user2.first_name + " " + user2.last_name
        profile2.email = 'bertrand@labevue.be'
        profile2.save()
        self.stdout.write("Second user {} with password {} created\n".format(
            user2.username, password
        ))

        tree = json.load(open('parsing/tree.json'))
        self.courseList = json.load(open('parsing/cours.json'))
        self.USER = profile
        Root = Category.objects.create(name='P402', description='Bring back real student cooperation !')
        self.walk(tree, Root)
        self.stdout.write("\n")


