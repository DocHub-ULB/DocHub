from typing import Optional

import mimetypes
import uuid
from collections.abc import Iterable

from django.core.files import File

import magic

from catalog.models import Course
from tags.models import Tag
from users.models import User


def clean_filename(name: str) -> str:
    if name.isupper():
        name = name.capitalize()

    return name.replace("_", " ")


def cast_tag(tag: str | Tag) -> Tag:
    if isinstance(tag, Tag):
        return tag
    else:
        return Tag.objects.get_or_create(name=tag.lower())[0]


def add_file_to_course(
    file: File,
    name: str,
    extension: str,
    course: Course,
    tags: list[str | Tag],
    user: User,
    import_source: str | None = None,
) -> "Optional[Document]":
    if not extension.startswith("."):
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            mime = m.id_buffer(file.read(4096))
            guessed_extension = mimetypes.guess_extension(mime, strict=True)
            if guessed_extension:
                extension = guessed_extension
            file.seek(0)
    if import_source is not None:
        document, created = Document.objects.get_or_create(
            user=user,
            name=name,
            course=course,
            import_source=import_source,
            file_type=extension.lower(),
            defaults={"state": Document.DocumentState.PREPARING},
        )
        if not created:
            return None
    else:
        document = Document.objects.create(
            user=user,
            name=name,
            course=course,
            state=Document.DocumentState.PREPARING,
            file_type=extension.lower(),
        )

    cleaned_tags: Iterable[Tag]
    if len(tags) > 0:
        cleaned_tags = [cast_tag(tag) for tag in tags]
    else:
        cleaned_tags = tags_from_name(name)

    document.tags.add(*cleaned_tags)

    document.original.save(str(uuid.uuid4()) + extension, file)
    document.state = Document.DocumentState.READY_TO_QUEUE

    document.save()

    return document


def tags_from_name(name: str) -> set[Tag]:
    translate = {"é": "e", "è": "e", "ê": "e", "-": " ", "_": " ", "û": "u", "ô": "o"}
    name = name.lower()
    for k, v in translate.items():
        name = name.replace(k, v)

    tags = set()

    mapping = {
        ("aout", "sept", "juin", "mai", "exam", "questions", "oral"): "examen",
        ("corr", "reponse", "rponse"): "corrigé",
        (
            "tp",
            "pratique",
            "exo",
            "exercice",
            "seance",
            "enonce",
        ): "tp",
        (
            "resum",
            "r?sum",
            "rsum",
            "synthese",
            "synthse",
        ): "résumé",
        (
            "slide",
            "transparent",
        ): "slides",
        ("formul",): "formulaire",
        (
            "rapport",
            "labo",
            "cahier",
        ): "laboratoire",
        ("note",): "notes",
        ("sylabus", "syllabus"): "syllabus",
        ("officiel", "oficiel"): "officiel",
    }

    for keys, val in mapping.items():
        for key in keys:
            if key in name:
                tags.add(val)

    tag_objs = {Tag.objects.get_or_create(name=tag)[0] for tag in tags}
    return tag_objs


from documents.models import Document  # NOQA
