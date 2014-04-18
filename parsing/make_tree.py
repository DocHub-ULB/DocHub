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
    years = os.listdir('./catalogs/')
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
        soup = bs.BeautifulSoup(open("./catalogs/" + path, "r").read())
        table = gettype(soup("form")[0], 'table')[1]
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

###################

years = get_years()
#print science_treeBA(years)
