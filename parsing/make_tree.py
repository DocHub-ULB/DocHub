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

import os
import bs4 as bs
import json

from graph.models import Course, Category
from polydag.models import Keyword
from users.models import User

DROPS = [u"Niveau dans le cycle*", u"Lieu d’enseignement*", u"Cycle*",
             u"Faculté gestionnaire*", u"Institution organisatrice*",
             u"Langue d'évaluation*", u"Horaire*", u"Discipline*",
             u"Contenu du cours*", u"Priorités de l'enseignant",
             u"Autres pré-requis", u"Objectifs du cours et compétences visées*",
             u"Syllabus*"]


def gettype(soup, type):
    tags = filter(lambda x: isinstance(x, bs.Tag), soup)
    return list(filter(lambda x: x.name == type, tags))


def extract(content, souptag, current):
    b = gettype(souptag, 'b')
    if len(b) == 1:
        content[b[0].text] = []
        current = content[b[0].text]
    a = filter(lambda x: 'href' in x.attrs.keys(), gettype(souptag, 'a'))
    current += list(a)
    if hasattr(souptag, 'contents'):
        for tag in souptag.contents:
            current = extract(content, tag, current)
    return current


def prettify_sciencesBA(tree):
    for key, section in tree.iteritems():
        for ykey, year in section.iteritems():
            year['course'] = year.pop('Cours obligatoires')
            options = year.pop('Cours optionnels', []) + year.pop(u'Cours \xe0 choisir', [])
            if options != []:
                year['Options'] = options
            year.pop('Autres cours', None)

            #Chimie
            travail = (
                year.pop('Approche Pratique', []) +
                year.pop(u'Approche th\xe9orique', []) +
                year.pop('Travail de fin de cycle', []) +
                year.pop(u'Travaux pratiques \xe0 choisir', [])
            )
            if travail != []:
                year['Travail'] = travail

            # Math
            if key == "Mathématique":
                year['Options'] = {}
                year['Options']["Informatique"] = year.pop(u'Math\xe9matique et informatique', [])
                year['Options']["Physique"] = year.pop(u'Math\xe9matique et physique', [])
                year['Options']["Economie"] = year.pop(u'Math\xe9matique et \xe9conomie', [])


def filter_years(years, use):
    used = []
    for year in years:
        for key in use.keys():
            if year[0].startswith(key):
                used.append(year)
                break
    return sorted(used)


def get_years():
    years = os.listdir('parsing/catalogs/')
    years = filter(lambda x: "-" in x, years)

    cleaned_years = []
    for year in years:
        splitted = year.split("_")
        good_name = "-".join(splitted[2:])
        cleaned_years.append((good_name, year))

    return cleaned_years


def science_treeBA(years):
    science_use = {
        "BA-BIOL": "Biologie",
        "BA-CHIM": "Chimie",
        "BA-IRBI": "Bioingénieur",
        "BA-GOEG": "Géographie",
        "BA-GEOL": "Géologie",
        "BA-INFO": "Informatique",
        "BA-MATH": "Mathématique",
        "BA-PHYS": "Physique"
    }

    science_years = filter_years(years, science_use)

    science = {}

    for name, path in science_years:
        soup = bs.BeautifulSoup(open("parsing/catalogs/" + path, "r").read(), "html5lib")
        table = gettype(soup("form")[0], 'table')
        if len(table) < 2:
            print "fail {}".format(name)
            continue
        else:
            print "ok {}".format(name)
        table = table[1]
        year_content = {}

        orphelins = []
        extract(year_content, table, orphelins)

        for key, val in year_content.iteritems():
            newval = []
            for course in val:
                newval.append(course.text[:9])
            year_content[key] = newval

        section = science_use[name[:7]]
        year = "BA" + name[-1]
        if not science.get(section, False):
            science[section] = {}
        science[section][year] = year_content

    prettify_sciencesBA(science)

    return science

def course_list(tree):
    l = []
    for key in tree:
        node = tree[key]
        if isinstance(node, list):
            l += node
        else:
            l += course_list(node)

    return l

def create_courses(clist):
    course_info = json.loads(open("parsing/cours.json").read())
    for course in clist:
        ulb_slug = course.upper().replace("-", "_")

        ulb = course_info[ulb_slug]

        slug = course.lower()
        slug = slug[:6] + "-" + slug[6:]
        c = Course.objects.create(
            name=ulb[u'Intitul\xe9 du cours*'],
            slug=slug
        )

        infos = []
        for cat, content in ulb.iteritems():
            if content == "" or cat in DROPS:
                continue
            if cat == u"Construction de la note, pondération des différentes activités*":
                cat = "Note"
            if cat == u"Langue d'enseignement*":
                cat = "Langue"
            if cat == u"Intitulé du cours*":
                cat = "Nom"
            if cat[-1] == "*":
                cat = cat[:-1]
            infos.append({"name": cat, "value": content})


def walk(jsonTree, parentNode):
    for key in jsonTree:
        val = jsonTree[key]
        if isinstance(val, list):
            if not key == "course":
                category = Category.objects.create(name=key, description="Magic !")
                parentNode.add_child(category)
            else:
                category = parentNode
            for slug in val:
                slug = slug.lower()
                slug = slug[:6] + "-" + slug[6:]
                category.add_child(Course.objects.get(slug=slug))
        else:
            category = Category.objects.create(name=key, description="Magic !")
            parentNode.add_child(category)
            walk(val, category)

def add_keywords():
    Keyword.objects.create(name="Labo")
    Keyword.objects.create(name="TP")
    Keyword.objects.create(name="Examen")
    Keyword.objects.create(name="Résumé")
    Keyword.objects.create(name="Formulaire")
    Keyword.objects.create(name="Référence")
    Keyword.objects.create(name="Projet")
    Keyword.objects.create(name="Consignes")

    Keyword.objects.create(name="Slides")
    Keyword.objects.create(name="Syllabus")

    Keyword.objects.create(name="Officiel")
    Keyword.objects.create(name="Corrigé")
    Keyword.objects.create(name="Points")


def add_users():
    users = json.loads(open("migrator/users.json").read())
    for user_tuple in users:
        netid, email, first_name, last_name = user_tuple
        if email == "":
            email = "{}@ulb.ac.be".format(netid)
        user = User.objects.create_user(netid=netid, email=email, password="qsdfqsfs")
        user.first_name = first_name
        user.last_name = last_name
        user.set_unusable_password()
        user.save()


def main():
    years = get_years()
    m = science_treeBA(years)
    clist = set(course_list(m))
    create_courses(clist)
    root = Category.objects.create(name='P402', description='Bring back real student cooperation !')
    walk(m, root)
    add_users()
