# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from documents.models import Document
from tags.models import Tag


def clean_filename(name):
    if name.isupper():
        name = name.capitalize()

    return name.replace("_", " ")


def add_file_to_course(file, name, extension, course, tags, user):
    document = Document.objects.create(
        user=user,
        name=name,
        course=course,
        state="PREPARING",
        file_type=extension.lower()
    )

    if len(tags) > 0:
        tags = [Tag.objects.get_or_create(name=tag.lower())[0] for tag in tags]
        document.tags.add(*tags)
    else:
        document.tag_from_name()

    document.original.save(str(uuid.uuid4()) + extension, file)
    document.state = 'READY_TO_QUEUE'

    document.save()

    return document
