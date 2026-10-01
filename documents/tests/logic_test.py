from io import BytesIO

import pytest
from django.core.files import File

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
