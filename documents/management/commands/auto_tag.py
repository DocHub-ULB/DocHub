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
from documents.models import Document


def clean_str(string):
    return string.lower().replace(u"é", "e").replace(u"è", "e").replace(u"ê", "e")


def is_exam(doc):
    clean = clean_str(doc.name)
    has_month = "janv" in clean or "aout" in clean or "sept" in clean or "juin" in clean
    return has_month or "exam" in clean


def is_corr(doc):
    clean = clean_str(doc.name)
    return "corr" in clean


def is_tp(doc):
    clean = clean_str(doc.name)
    return "tp" in clean or "seance" in clean


def is_res(doc):
    clean = clean_str(doc.name)
    return "resum" in clean or "r?sum" in clean or "rsum" in clean


def is_slide(doc):
    clean = clean_str(doc.name)
    return "slide" in clean or "transparent" in clean


def is_form(doc):
    clean = clean_str(doc.name)
    return "formulaire" in clean


def is_labo(doc):
    clean = clean_str(doc.name)
    return "rapport" in clean or "labo" in clean


class Command(BaseCommand):

    help = 'Auto-tag documents based on their name'

    def handle(self, *args, **options):
        self.stdout.write('Auto-tagging ... ')
        exams = list(filter(is_exam, Document.objects.all()))
        corr = list(filter(is_corr, Document.objects.all()))
        tp = list(filter(is_tp, Document.objects.all()))
        res = list(filter(is_res, Document.objects.all()))
        slide = list(filter(is_slide, Document.objects.all()))
        form = list(filter(is_form, Document.objects.all()))
        labo = list(filter(is_labo, Document.objects.all()))

        for doc in exams:
            doc.add_keywords('examen')

        for doc in corr:
            doc.add_keywords('corrigé')

        for doc in tp:
            doc.add_keywords('tp')

        for doc in res:
            doc.add_keywords('résumé')

        for doc in slide:
            doc.add_keywords('slides')

        for doc in form:
            doc.add_keywords('formulaire')

        for doc in labo:
            doc.add_keywords('laboratoire')

        self.stdout.write('Done \n')
