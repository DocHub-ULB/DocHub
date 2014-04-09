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

from json import loads, dumps

to_ulb = lambda n: n[0:4].upper() + "_" + n[5].upper() + n[7:]
tree = loads(open("tree.json").read())
ulb_courses = loads(open("cours.json").read())
course_pk, cat_pk = 0, 0

drops = [u"Niveau dans le cycle*", u"Lieu d’enseignement*", u"Cycle*",
         u"Faculté gestionnaire*", u"Institution organisatrice*",
         u"Langue d'évaluation*", u"Horaire*", u"Discipline*",
         u"Contenu du cours*", u"Priorités de l'enseignant",
         u"Autres pré-requis", u"Objectifs du cours et compétences visées*",
         u"Syllabus*"]

users = """[
    {"pk": 1,
     "model": "users.User",
     "fields": {"netid": "root",
                "first_name": "Great",
                "last_name": "Architect",
                "is_active": true,
                "is_superuser": false,
                "is_staff": false,
                "last_login": "2013-03-09T19:20:26.104",
                "groups": [],
                "user_permissions": [],
                "password": "pbkdf2_sha256$10000$9SMbs1VSLOtC$XYLVkKG3JXbp+c1Hm81TICR2D/vCQfhmVmmDW/hUAEY=",
                "date_joined": "2012-11-30T20:53:56.087",
                "comment": null,
                "photo": "",
                "welcome": true,
                "user": 1,
                "registration": "0",
                "follow": [],
                "email": "p402@cerkinfo.be"}}]"""


def add_course(slug):
    global course_pk, inital_data

    name = slug.upper()
    course = ulb_courses[to_ulb(slug)]
    infos = []

    for cat, content in course.iteritems():
        if content == "" or cat in drops:
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

    course_pk = course_pk + 1
    initial_data.append({"pk": course_pk,
                         "model": "graph.course",
                         "fields": {"description": dumps(course),
                                    "slug": slug,
                                    "name": name}})
    initial_data.append({"pk": course_pk,
                         "model": "graph.courseinfo",
                         "fields": {"date": "2012-11-30T20:54:51.982",
                                    "course": course_pk,
                                    "infos": dumps(infos)}})
    return course_pk


def walk(mother_key, mother_node):
    global cat_pk, initial_data

    courses, subcat = [], []
    for key, node in mother_node.iteritems():
        if key == "course":
            courses = [add_course(c) for c in node]
        else:
            subcat.append(walk(key, node))

    cat_pk = cat_pk + 1
    initial_data.append({"pk": cat_pk,
                         "model": "graph.category",
                         "fields": {"contains": courses,
                                    "sub_categories": subcat,
                                    "name": mother_key,
                                    "description": "?*"}})
    return cat_pk

cat_pk = cat_pk + 1
initial_data = loads(users)
initial_data.append({"pk": cat_pk,
                     "model": "graph.category",
                     "fields": {"contains": [],
                                "sub_categories": [],
                                "name": "Sections",
                                "description": "Root node w/ category"}})
root_subcat = []
for key, node in tree.iteritems():
    root_subcat.append(walk(key, node))
initial_data[2]["fields"]["sub_categories"] = root_subcat

print dumps(initial_data)
