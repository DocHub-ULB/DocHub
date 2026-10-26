import hashlib
import mimetypes
import os
import re
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


# A course code at the start of a text, written in any of the ways people use:
# "INFO-F105", "info-f-105", "INFOF105", "infof-105", "info f105"...
# The code must end there: "INFO-F10l" (a typo) is not a code.
COURSE_CODE = re.compile(
    r"\s*([a-z]{1,4})[-_ ]?([a-z])[-_ ]?(\d{2,5})(?![a-z0-9])[-_ ]*", re.IGNORECASE
)


def split_course_code(text: str) -> tuple[str, str]:
    """Split "INFO-F105_2018_Juin" into ("info-f105", "2018_Juin").

    Without a course code at the start, gives ("", text).
    """
    match = COURSE_CODE.match(text)
    if match is None:
        return "", text
    domain, faculty, number = match.groups()
    return f"{domain}-{faculty}{number}".lower(), text[match.end() :]


# The tags a user can write in a file name, with a "#" before them:
# "#exa #cor Examen juin.pdf" or "Examen juin #examen#corrigé.pdf".
# A tag is its short code or its full name.
# Keep in line with the help of documents/templates/documents/bulk_upload.html.
TAG_CODES = {
    "off": "officiel",
    "ref": "référence",
    "sli": "slides",
    "res": "résumé",
    "exa": "examen",
    "tp": "tp",
    "syl": "syllabus",
    "cor": "corrigé",
    "corr": "corrigé",
    "sol": "corrigé",
    "for": "formulaire",
    "lab": "laboratoire",
    "law": "loi",
}
TAG_NAMES = TAG_CODES | {name: name for name in TAG_CODES.values()}

# A "#" and the letters or digits after it. The separators around it go with
# it, so that "Examen_#cor_juin" becomes "Examen juin".
HASHTAG = re.compile(r"[-_ ]*#([^\W_]+)[-_ ]*")


def split_tags(name: str) -> tuple[list[str], str]:
    """Split "#exa#cor Examen" into (["examen", "corrigé"], "Examen").

    We keep in the name a "#" that is not a tag: "TP #3" has no tags.
    """
    tags = []

    def remove_tag(match: re.Match[str]) -> str:
        tag = TAG_NAMES.get(match.group(1).lower())
        if tag is None:
            return match.group(0)
        tags.append(tag)
        return " "

    name = HASHTAG.sub(remove_tag, name).strip()
    return list(dict.fromkeys(tags)), name


def document_tags(file_name: str) -> list[str]:
    """The tags written in a file name, see TAG_CODES.

    Without tags, gives no tags: add_file_to_course then guesses them from the title.
    """
    return split_tags(file_name)[0]


def document_title(file_name: str, course: Course) -> str:
    """The title of a document, from its file name.

    We remove the tags written in the name, see TAG_CODES.
    We also remove the code of the course: the document is already in that
    course, so "INFO-F105_2018_Juin.pdf" becomes "2018 Juin".
    """
    name = os.path.splitext(file_name)[0]
    # A name with only tags keeps them: "#exa.pdf" becomes "#exa".
    title = clean_filename(split_tags(name)[1] or name)
    code, rest = split_course_code(title)
    if rest and code == course.slug:
        title = rest
    return title[:255]


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
    return {Tag.objects.get_or_create(name=tag)[0] for tag in tag_names_from_name(name)}


def tag_names_from_name(name: str) -> set[str]:
    """Guess the tags of a document from its name, without touching the database."""
    translate = {"é": "e", "è": "e", "ê": "e", "-": " ", "_": " ", "û": "u", "ô": "o"}
    name = name.lower()
    for k, v in translate.items():
        name = name.replace(k, v)

    tags = set()

    mapping = {
        (
            "janv",
            "aout",
            "sept",
            "juin",
            "mai",
            "exam",
            "partiel",
            "questions",
            "oral",
        ): "examen",
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

    return tags


from documents.models import Document  # NOQA
