import json
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from catalog.models import Course
from documents.bulk import FileStatus, plan_bulk_upload
from documents.models import Document
from tags.models import Tag

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def local_storage(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.STORAGES = {
        **settings.STORAGES,
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    }


@pytest.fixture
def info():
    return Course.objects.create(name="Algorithmique", slug="info-f101")


@pytest.fixture
def math():
    return Course.objects.create(name="Analyse", slug="math-f112")


def statuses(plan):
    return {
        file.path: (folder.name, file.status)
        for folder in plan.folders
        for file in folder.files
    }


def test_plan_groups_files_by_course_folder(info, math):
    plan = plan_bulk_upload(
        [
            ("export/INFO-F101/TP1.pdf", 10),
            ("export/info-f101/tp/TP2.pdf", 20),
            ("export/math-f112/Examen.pdf", 30),
        ],
    )
    courses = {folder.name: folder.course for folder in plan.folders}
    assert courses == {"INFO-F101": info, "info-f101": info, "math-f112": math}
    assert len(plan.ready_files) == 3
    assert plan.ready_size == 60


def test_plan_reads_the_course_code_at_the_start_of_folder_names(info, math):
    plan = plan_bulk_upload(
        [
            ("export/Info-F101_Algo/TP1.pdf", 10),
            ("export/infof-101/TP2.pdf", 10),
            ("export/INFO F101 (Algo)/TP3.pdf", 10),
            ("export/MATH-F112 Analyse/TP1.pdf", 10),
            ("export/Info-F10l_Algo/TP1.pdf", 10),
        ],
    )
    courses = {folder.name: folder.course for folder in plan.folders}
    assert courses == {
        "Info-F101_Algo": info,
        "infof-101": info,
        "INFO F101 (Algo)": info,
        "MATH-F112 Analyse": math,
        "Info-F10l_Algo": None,
    }
    assert plan.unknown_folders[0].suggestion == "info-f101"


def test_plan_shows_title_and_tags_like_the_upload(info):
    plan = plan_bulk_upload(
        [
            ("export/info-f101/Résumé_chapitre_1.pdf", 10),
            ("export/info-f101/INFO-F101_2024_Juin.pdf", 10),
            ("export/info-f101/Juin #sli.pdf", 10),
        ],
    )
    files = [(file.title, file.tags) for file in plan.folders[0].files]
    assert files == [
        ("2024 Juin", ["examen"]),
        ("Juin", ["slides"]),
        ("Résumé chapitre 1", ["résumé"]),
    ]
    assert Tag.objects.count() == 0


def test_plan_accepts_a_single_course_folder(info):
    plan = plan_bulk_upload(
        [
            ("INFO-F101 Algo/TP1.pdf", 10),
            ("INFO-F101 Algo/tp/TP2.pdf", 10),
        ]
    )
    assert [folder.course for folder in plan.folders] == [info]
    assert len(plan.ready_files) == 2
    assert plan.loose_files == []


def test_plan_reports_unknown_course_with_suggestion(info):
    plan = plan_bulk_upload(
        [
            ("export/info-f10l/TP1.pdf", 10),
            ("export/notes/TP2.pdf", 10),
        ]
    )
    unknown = {folder.name: folder.suggestion for folder in plan.unknown_folders}
    assert unknown == {"info-f10l": "info-f101", "notes": ""}


def test_plan_does_not_suggest_for_valid_unknown_codes(info):
    plan = plan_bulk_upload([("export/info-f102/TP1.pdf", 10)])
    assert plan.unknown_folders[0].suggestion == ""
    assert plan.ready_files == []


def test_plan_reports_files_outside_course_folders(info):
    plan = plan_bulk_upload(
        [
            ("export/Tableau.xlsx", 10),
            ("export/info-f101/TP1.pdf", 10),
        ]
    )
    assert [file.name for file in plan.loose_files] == ["Tableau.xlsx"]
    assert plan.unknown_folders == []
    assert len(plan.ready_files) == 1


def test_plan_skips_system_compressed_and_empty_files(info):
    plan = plan_bulk_upload(
        [
            ("export/info-f101/.DS_Store", 10),
            ("export/__MACOSX/info-f101/._TP1.pdf", 10),
            ("export/info-f101/archive.ZIP", 10),
            ("export/info-f101/empty.pdf", 0),
            ("export/info-f101/TP1.pdf", 10),
        ],
    )
    assert statuses(plan) == {
        "export/info-f101/archive.ZIP": ("info-f101", FileStatus.COMPRESSED),
        "export/info-f101/empty.pdf": ("info-f101", FileStatus.EMPTY),
        "export/info-f101/TP1.pdf": ("info-f101", FileStatus.READY),
    }
    assert [file.name for file in plan.compressed_files] == ["archive.ZIP"]
    assert [file.name for file in plan.empty_files] == ["empty.pdf"]


def test_plan_hides_course_folders_with_nothing_to_send(info, math):
    plan = plan_bulk_upload(
        [
            ("export/info-f101/archive.zip", 10),
            ("export/math-f112/TP1.pdf", 10),
        ]
    )
    assert [folder.course for folder in plan.ready_folders] == [math]
    assert plan.ready_course_count == 1


def check(client, files):
    return client.post(
        reverse("document_bulk_upload_check"), {"entries": json.dumps(files)}
    )


def current_step(page):
    return page.select_one('.bulk-steps [aria-current="step"]').get_text(
        " ", strip=True
    )


def test_check_view_renders_the_plan(client, user, info):
    client.force_login(user)
    response = check(
        client,
        [
            {"path": "export/info-f101/TP1.pdf", "size": 10},
            {"path": "export/info-f10l/TP2.pdf", "size": 10},
        ],
    )
    assert response.status_code == 200
    page = BeautifulSoup(response.content, "html.parser")
    assert page.select_one("turbo-frame")["id"] == "bulk-wizard"
    assert current_step(page) == "3 Vérifie"
    assert len(page.select_one(".bulk-steps").select(".is-done")) == 2
    assert page.select_one(".bulk-summary-folder").get_text(strip=True) == "export"
    assert len(page.select(".bulk-file")) == 1
    assert page.select_one(".bulk-send") is not None
    assert page.select_one(".bulk-file-original").text == "TP1.pdf"
    assert page.select_one(".bulk-file-title").text == "Tp1"
    assert "INFO-F101" in page.select_one(".bulk-notes").get_text()
    assert "1 fichier prêt à être envoyé pour 1 cours" in " ".join(
        page.select_one(".bulk-summary-count").get_text().split()
    )


def test_check_view_puts_compressed_files_aside(client, user, info):
    client.force_login(user)
    response = check(
        client,
        [
            {"path": "export/info-f101/TP1.pdf", "size": 10},
            {"path": "export/info-f101/Anciens examens.zip", "size": 10},
        ],
    )
    page = BeautifulSoup(response.content, "html.parser")
    notes = " ".join(page.select_one(".bulk-notes").get_text().split())
    assert (
        "Ce fichier est compressé, décompresse-le d'abord : Anciens examens.zip"
        in notes
    )
    files = [file.text for file in page.select(".bulk-file-original")]
    assert files == ["TP1.pdf"]
    assert page.select_one(".bulk-folder-meta").text == "1 fichier"


def test_check_view_says_when_nothing_can_be_sent(client, user, info):
    client.force_login(user)
    response = check(client, [{"path": "export/notes/TP1.pdf", "size": 10}])
    page = BeautifulSoup(response.content, "html.parser")
    assert "rien à envoyer" in page.select_one(".bulk-summary-count").text
    assert page.select_one(".bulk-send") is None
    assert page.select_one("template") is None


@pytest.mark.parametrize(
    ("files", "message"),
    [
        ([], "vide"),
        ([{"path": "export/info-f101/TP1.pdf"}], "pas valide"),
        ("not a list", "pas valide"),
        # Some phones send the files without their folders.
        ([{"path": "TP1.pdf", "size": 10}], "pas envoyé de dossier"),
        ([{"path": "export/info-f101/TP1.pdf", "size": -1}], "pas valide"),
    ],
)
def test_check_view_rejects_bad_lists(client, user, files, message):
    client.force_login(user)
    response = check(client, files)
    assert response.status_code == 422
    assert message in response.content.decode()
    # Back to step 2, so that the user can pick another folder.
    page = BeautifulSoup(response.content, "html.parser")
    assert current_step(page) == "2 Choisis ton dossier"
    assert page.select_one("input[webkitdirectory]") is not None


def test_check_view_prepares_the_send_step(client, user, info):
    client.force_login(user)
    response = check(
        client,
        [
            {"path": "export/info-f101/TP1.pdf", "size": 10},
            {"path": "export/info-f101/archive.zip", "size": 10},
        ],
    )
    assert response.status_code == 200
    page = BeautifulSoup(response.content, "html.parser")
    # Parse the inert markup as a fragment, as the browser does when showing it.
    page = BeautifulSoup(page.select_one("template").decode_contents(), "html.parser")
    assert current_step(page) == "4 Envoie"
    assert len(page.select(".bulk-steps .is-done")) == 3
    assert page.select_one("[data-status=sending]") is not None
    assert page.select_one("progress")["max"] == "1"
    assert page.select_one(".bulk-send") is None
    # Only the files that we can send.
    assert json.loads(page.select_one("[data-queue]")["data-queue"]) == [
        {
            "path": "export/info-f101/TP1.pdf",
            "url": reverse("document_bulk_upload_file", args=["info-f101"]),
        }
    ]
    # Too late to check the folder: only the summary shows.
    assert page.select_one(".bulk-lists") is None


def send(client, slug, name="TP1.pdf", content=b"A document" * 100):
    with patch("documents.models.process_document.delay") as queue:
        response = client.post(
            reverse("document_bulk_upload_file", args=[slug]),
            {"file": SimpleUploadedFile(name, content)},
        )
    return response, queue


def test_file_view_adds_the_document(client, user, info):
    client.force_login(user)
    response, queue = send(client, "info-f101", name="INFO-F101_Examen_juin.pdf")
    assert response.status_code == 201
    document = Document.objects.get(course=info)
    assert document.name == "Examen juin"
    assert [tag.name for tag in document.tags.all()] == ["examen"]
    assert document.file_type == ".pdf"
    assert document.user == user
    queue.assert_called_once_with(document.pk)


def test_file_view_reads_the_tag_codes(client, user, info):
    client.force_login(user)
    response, _ = send(client, "info-f101", name="#sli#corrigé Examen juin.pdf")
    assert response.status_code == 201
    document = Document.objects.get(course=info)
    assert document.name == "Examen juin"
    assert {tag.name for tag in document.tags.all()} == {"slides", "corrigé"}


def test_file_view_rejects_duplicates(client, user, info):
    client.force_login(user)
    send(client, "info-f101")
    response, queue = send(client, "info-f101", name="copy.pdf")
    assert response.status_code == 409
    assert Document.objects.count() == 1
    queue.assert_not_called()


def test_file_view_rejects_compressed_files(client, user, info):
    client.force_login(user)
    response, _ = send(client, "info-f101", name="archive.zip")
    assert response.status_code == 400
    assert Document.objects.count() == 0


def test_file_view_unknown_course(client, user):
    client.force_login(user)
    response, _ = send(client, "info-f999")
    assert response.status_code == 404


def test_bulk_upload_page_explains_first(client, user):
    client.force_login(user)
    response = client.get(reverse("document_bulk_upload"))
    assert response.status_code == 200
    page = BeautifulSoup(response.content, "html.parser")
    assert current_step(page) == "1 Prépare tes fichiers"
    assert page.select(".bulk-steps .is-done") == []
    assert page.select_one("details.bulk-tips:not([open])") is not None
    assert page.select_one("input[webkitdirectory]") is None
    ready = page.select_one(".bulk-actions a")
    assert "Mes fichiers sont prêts" in ready.get_text()
    assert ready["href"] == reverse("document_bulk_upload_pick")


def test_bulk_upload_page_pick_step(client, user):
    client.force_login(user)
    response = client.get(reverse("document_bulk_upload_pick"))
    assert response.status_code == 200
    page = BeautifulSoup(response.content, "html.parser")
    assert current_step(page) == "2 Choisis ton dossier"
    assert len(page.select(".bulk-steps .is-done")) == 1
    assert page.select_one("input[webkitdirectory]") is not None


def test_file_view_without_file(client, user, info):
    client.force_login(user)
    response = client.post(reverse("document_bulk_upload_file", args=["info-f101"]))
    assert response.status_code == 400


def test_file_view_keeps_different_content_with_the_same_name(client, user, info):
    client.force_login(user)
    first, _ = send(client, info.slug, content=b"first content")
    second, _ = send(client, info.slug, content=b"different content")
    assert first.status_code == second.status_code == 201
    assert Document.objects.filter(course=info, name="Tp1").count() == 2
