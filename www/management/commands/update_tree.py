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

    to_ulb = lambda self, n: n[0:4].upper() + "_" + n[5].upper() + n[7:]

    help = 'Update the courses and categories tree'

    def createCourse(self, parentNode, slug):
        try:
            course = Course.objects.get(slug=slug)
            self.stdout.write('.', ending='')
        except:
            ULBInfos = self.courseList[self.to_ulb(slug)]
            self.stdout.write('c', ending='')
            name = slug.upper()
            infos = []
            for cat, content in ULBInfos.iteritems():
                if content == "" or cat in self.drops:
                    continue
                if cat == u"Construction de la note, pondération des différentes activités*":
                    cat = "Note"
                if cat == u"Langue d'enseignement*":
                    cat = "Langue"
                if cat == u"Nom":
                    cat = "Nom"
                    name = content
                if cat[-1] == "*":
                    cat = cat[:-1]
                infos.append({"name": cat, "value": content})
            course = Course.objects.create(
                name=name, slug=slug,
                description=json.dumps(ULBInfos)
            )
            CourseInfo.objects.create(
                course=course, infos=json.dumps(infos),
                date=self.NOW
            )
        parentNode.add_child(course)

        self.stdout.flush()

    def walk(self, jsonTree, parentNode):
        for key in jsonTree:
            val = jsonTree[key]
            if key.lower() == 'course':
                for slug in val:
                    self.createCourse(parentNode, slug)
            else:
                categories = list(filter(lambda x: x.name == key, parentNode.children(only=[Category])))
                if len(categories) > 1:
                    raise Exception('len(Category) > 1')
                elif len(categories) == 1:
                    category = categories[0]
                    self.stdout.write('#', ending='')
                elif len(categories) == 0:
                    category = Category.objects.create(name=key, description="Magic !")
                    parentNode.add_child(category)
                    self.stdout.write('C', ending='')
                self.stdout.flush()
                self.walk(val, category)

    def handle(self, *args, **options):
        tree = json.load(open('parsing/tree.json'))
        self.courseList = json.load(open('parsing/cours.json'))
        Root = Category.objects.get(name='P402')
        self.walk(tree, Root)
        self.stdout.write("\n")
