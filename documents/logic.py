import hashlib
import mimetypes
import uuid
from collections.abc import Iterable

import magic
from django.core.files import File

from catalog.models import Course
from documents.exceptions import ExisingChecksum
from tags.models import Tag
from users.models import User


def calculate_checksum(file: File) -> str:
    hasher = hashlib.md5()
    file.seek(0)
    try:
        for chunk in file.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()
    finally:
        file.seek(0)


def check_document_is_unique(
    file: File, document_id_to_ignore: int | None = None
) -> str:
    checksum = calculate_checksum(file)
    duplicates = Document.objects.filter(md5=checksum, hidden=False)
    if document_id_to_ignore is not None:
        duplicates = duplicates.exclude(pk=document_id_to_ignore)
    duplicate = duplicates.first()
    if duplicate is not None:
        raise ExisingChecksum(
            "Ce document est déjà sur DocHub.",
            document=duplicate,
        )
    return checksum


def delete_hidden_duplicates(document: "Document") -> None:
    if document.md5:
        Document.objects.filter(md5=document.md5, hidden=True).exclude(
            pk=document.pk
        ).delete()


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
    description: str = "",
) -> "Document":
    if not extension.startswith("."):
        mime = magic.from_buffer(file.read(4096), mime=True)
        guessed_extension = mimetypes.guess_extension(mime, strict=True)
        if guessed_extension:
            extension = guessed_extension
        file.seek(0)
    checksum = check_document_is_unique(file)
    document = Document.objects.create(
        user=user,
        name=name,
        course=course,
        import_source=import_source,
        state=Document.DocumentState.PREPARING,
        md5=checksum,
        description=description,
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
    delete_hidden_duplicates(document)

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
