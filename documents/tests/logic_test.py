from io import BytesIO

import pytest
from django.core.files import File

from catalog.models import Course
from documents import logic
from documents.exceptions import ExisingChecksum
from documents.models import Document
from tags.models import Tag

pytestmark = pytest.mark.django_db


def test_add_file_to_course(user, course):
    Tag.objects.create(name="tag one")
    tags = ["tag one", "tag two", Tag.objects.create(name="tag three")]

    file = File(BytesIO(b"mybinarydocumentcontent"))
    file.size = len(b"mybinarydocumentcontent")

    doc = logic.add_file_to_course(file, "My document", ".dll", course, tags, user)

    assert doc
    assert doc in course.document_set.all()
    assert doc.name == "My document"
    assert doc.state == Document.DocumentState.READY_TO_QUEUE
    assert Tag.objects.count() == 3
    assert doc.tags.count() == 3
    assert doc.file_type == ".dll"


def test_no_extension(user, course):
    doc = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\n/\x00\x00\t\x81\x08\x06\x00\x00\x00'\x06\xfee\x00\x00\x00\tpHYs\x00\x00n\xba\x00\x00n\xba\x01\xd6\xde\xb1\x17\x00\x00\x00\x19tEXtSoftware\x00www.inkscape.org\x9b\xee<\x1a\x00\x00 \x00IDATx"
    file = File(BytesIO(doc))
    file.size = len(doc)

    doc = logic.add_file_to_course(file, "My document", "", course, [], user)

    assert doc
    assert doc.file_type == ".png"


def test_duplicate_is_rejected_before_storage(user, course):
    contents = b"same document"
    first = logic.add_file_to_course(
        File(BytesIO(contents)), "First", ".pdf", course, [], user
    )
    assert first.md5 == logic.calculate_checksum(File(BytesIO(contents)))
    with pytest.raises(ExisingChecksum):
        logic.add_file_to_course(
            File(BytesIO(contents)), "Second", ".pdf", course, [], user
        )
    assert Document.objects.count() == 1
    assert first.original.read() == contents


def test_repeated_import_is_rejected_by_checksum(user, course):
    logic.add_file_to_course(
        File(BytesIO(b"imported")),
        "Imported",
        ".pdf",
        course,
        [],
        user,
        import_source="source.pdf",
    )
    with pytest.raises(ExisingChecksum):
        logic.add_file_to_course(
            File(BytesIO(b"imported")),
            "Imported",
            ".pdf",
            course,
            [],
            user,
            import_source="source.pdf",
        )
    assert Document.objects.count() == 1


def test_same_import_source_with_different_contents_is_accepted(user, course):
    for contents in (b"original", b"updated"):
        logic.add_file_to_course(
            File(BytesIO(contents)),
            "Imported",
            ".pdf",
            course,
            [],
            user,
            import_source="source.pdf",
        )
    assert Document.objects.filter(import_source="source.pdf").count() == 2


def test_known_pdf_checksum():
    with open("documents/tests/files/3pages.pdf", "rb") as stream:
        file = File(stream)
        assert logic.calculate_checksum(file) == "8be98044ac25f3050b121aceac618823"
        assert file.tell() == 0


@pytest.mark.parametrize(
    ("name", "tags"),
    [
        ("INFO-F101 2024 Janvier", {"examen"}),
        ("INFO-F203 2020 Juin partiel", {"examen"}),
        ("MATH-F315 2008 Juin exercices", {"examen", "tp"}),
        ("Résumé chapitre 1", {"résumé"}),
        ("Cours 3", set()),
    ],
)
def test_tag_names_from_name(name, tags):
    assert logic.tag_names_from_name(name) == tags


@pytest.mark.parametrize(
    ("name", "tags", "rest"),
    [
        ("#exa #cor Examen", ["examen", "corrigé"], "Examen"),
        ("#exa#cor Examen", ["examen", "corrigé"], "Examen"),
        ("Examen #EXAMEN#corrigé", ["examen", "corrigé"], "Examen"),
        ("Examen_#cor_juin", ["corrigé"], "Examen juin"),
        ("#cor #sol Examen", ["corrigé"], "Examen"),
        ("#résumé Chapitre 1", ["résumé"], "Chapitre 1"),
        # A "#" that is not a tag stays in the name.
        ("TP #3 #tp", ["tp"], "TP #3"),
        ("Examen #2019", [], "Examen #2019"),
        ("Examen", [], "Examen"),
    ],
)
def test_split_tags(name, tags, rest):
    assert logic.split_tags(name) == (tags, rest)


@pytest.mark.parametrize(
    ("file_name", "title"),
    [
        ("INFO-F101_2018_Juin.pdf", "2018 Juin"),
        ("info-f-101 Résumé.docx", "Résumé"),
        ("INFOF101_notes.pdf", "notes"),
        # Another course code tells something, we keep it.
        ("MATH-F112_2023_Juin.pdf", "MATH-F112 2023 Juin"),
        ("INFO-F101.pdf", "Info-f101"),
        ("Examen_juin.pdf", "Examen juin"),
        ("#exa #cor INFO-F101_2018_Juin.pdf", "2018 Juin"),
        ("INFO-F101_2018_Juin_#exa.pdf", "2018 Juin"),
        ("#exa.pdf", "#exa"),
    ],
)
def test_document_title(file_name, title):
    course = Course(slug="info-f101")
    assert logic.document_title(file_name, course) == title


@pytest.mark.parametrize(
    ("text", "result"),
    [
        ("INFO-F105_2018_Juin", ("info-f105", "2018_Juin")),
        ("info-f-105", ("info-f105", "")),
        ("infof-105 Algo", ("info-f105", "Algo")),
        ("INFOF105", ("info-f105", "")),
        ("info f105 (LDP1)", ("info-f105", "(LDP1)")),
        # A typo is not a code.
        ("Info-F10l_Algo", ("", "Info-F10l_Algo")),
        ("Examen juin", ("", "Examen juin")),
    ],
)
def test_split_course_code(text, result):
    assert logic.split_course_code(text) == result
