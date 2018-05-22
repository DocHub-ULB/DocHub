# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

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


def add_file_to_course(file, name, extension, course, tags, user, import_source=None):
    if not extension.startswith("."):
        raise ValueError("extension must start with a '.'")
    if import_source is not None:
        document, created = Document.objects.get_or_create(
            user=user,
            name=name,
            course=course,
            import_source=import_source,
            file_type=extension.lower(),
            defaults={'state': 'PREPARING'}
        )
        if not created:
            return document
    else:
        document = Document.objects.create(
            user=user,
            name=name,
            course=course,
            state="PREPARING",
            file_type=extension.lower()
        )

    if len(tags) > 0:
        tags = [cast_tag(tag) for tag in tags]
    else:
        tags = tags_from_name(name)

    document.tags.add(*tags)

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
    name = name.lower()
    for k, v in translate.items():
        name = name.replace(k, v)

    tags = set()

    mapping = {
        ("aout", "sept", "juin", "mai", "exam", "questions", "oral"): "examen",
        ("corr", "reponse", "rponse"): "corrigé",
        ("tp", "pratique", "exo", "exercice", "seance", "enonce",): "tp",
        ("resum", "r?sum", "rsum", "synthese", "synthse", ): "résumé",
        ("slide", "transparent",): "slides",
        ("formul",): "formulaire",
        ("rapport", "labo", "cahier",): "laboratoire",
        ("note",): "notes",
        ("sylabus", "syllabus"): "syllabus",
        ("officiel", "oficiel"): "officiel",
    }

    for keys, val in mapping.items():
        for key in keys:
            if key in name:
                tags.add(val)

    tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tags]
    return tags

from documents.models import Document # NOQA
