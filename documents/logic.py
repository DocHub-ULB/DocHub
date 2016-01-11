# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from documents.models import Document
from tags.models import Tag


def clean_filename(name):
    if name.isupper():
        name = name.capitalize()

    return name.replace("_", " ")


def cast_tag(tag):
    if isinstance(tag, Tag):
        return tag
    else:
        return Tag.objects.get_or_create(name=tag.lower())[0]


def add_file_to_course(file, name, extension, course, tags, user):
    if not extension.startswith("."):
        raise ValueError("extension must start with a '.'")
    document = Document.objects.create(
        user=user,
        name=name,
        course=course,
        state="PREPARING",
        file_type=extension.lower()
    )

    if len(tags) > 0:
        tags = [cast_tag(tag) for tag in tags]
        document.tags.add(*tags)
    else:
        document.tag_from_name()

    document.original.save(str(uuid.uuid4()) + extension, file)
    document.state = 'READY_TO_QUEUE'

    document.save()

    return document


def tags_from_name(name):
    translate = {
        'é': 'e',
        'è': 'e',
        'ê': 'e',
        '-': ' ',
        '_': ' ',
        'û': 'u',
        'ô': 'o'
    }
    name = name.lower().translate(translate)
    tokens = name.split(' ')
    tags = []

    mapping = {
        ("aout", "sept", "juin", "mai", "exam", "questions", "oral"): "examen",
        ("corr", "reponse", "rponse"): "corrigé",
        ("tp", "pratique", "exo", "exercice", "seance", "enonce",): "tp",
        ("resum", "r?sum", "rsum", "synthese", "synthse", ): "résumé",
        ("slide", "transparent",): "slides",
        ("formule",): "formulaire",
        ("rapport", "labo", "cahier",): "laboratoire",
        ("note",): "notes",
        ("sylabus", "syllabus"): "syllabus",
        ("officiel", "oficiel"): "officiel",
    }

    for token in tokens:
        for key, val in mapping.items():
            if key in token:
                tags.append(val)

    tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tags]
    return tags
