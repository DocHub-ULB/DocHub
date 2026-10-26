"""The bulk upload page in a real browser: pick a folder, check it, send it.

The screenshots land in ``screenshots/bulk_upload/``.

    uv sync --group playwright && uv run playwright install chromium
    uv run pytest -m playwright documents/tests/bulk_upload_playwright_test.py
"""

import json
import shutil
from unittest.mock import patch

import pytest
from django.conf import settings as django_settings
from django.urls import reverse

from catalog.models import Course
from documents.models import Document

# Skip cleanly if the optional playwright package is not installed (e.g. CI).
pytest.importorskip("playwright.sync_api")

pytestmark = [pytest.mark.playwright, pytest.mark.network, pytest.mark.django_db]

FILES = django_settings.BASE_DIR / "documents" / "tests" / "files"
SCREENSHOT_DIR = django_settings.BASE_DIR / "screenshots" / "bulk_upload"
VIEWPORT = {"width": 1280, "height": 1000}


@pytest.fixture
def folder(tmp_path):
    """A folder like the ones people have: course code, then a nickname."""
    root = tmp_path / "Anciens_examens"
    (root / "Info-F101_Algo").mkdir(parents=True)
    (root / "info-f10l").mkdir()
    shutil.copy(
        FILES / "3pages.pdf", root / "Info-F101_Algo" / "INFO-F101_2024_Juin.pdf"
    )
    shutil.copy(
        FILES / "1page.pdf", root / "Info-F101_Algo" / "INFO-F101_2025_Aout.pdf"
    )
    shutil.copy(FILES / "1page.pdf", root / "info-f10l" / "TP1.pdf")
    (root / "Tableau.xlsx").write_bytes(b"not really a spreadsheet")
    return root


def test_bulk_upload(live_server, logged_in_page, user, folder):
    course = Course.objects.create(name="Algorithmique 1", slug="info-f101")
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    with (
        patch("documents.models.process_document.delay"),
        logged_in_page(user, viewport=VIEWPORT) as page,
    ):
        page.goto(live_server.url + reverse("document_bulk_upload"))
        page.get_by_text("Trucs et astuces").click()
        assert page.locator(".bulk-tips-tags").is_visible()
        page.screenshot(path=SCREENSHOT_DIR / "0-prepare.png", full_page=True)
        page.get_by_role("link", name="Mes fichiers sont prêts").click()
        picker = page.locator("input[webkitdirectory]")

        picker.set_input_files(folder)
        page.wait_for_selector(".bulk-summary")
        rows = page.locator(".bulk-file")
        assert rows.count() == 2
        problems = page.locator(".bulk-notes").inner_text()
        assert "INFO-F101" in problems
        assert "Tableau.xlsx" in problems
        assert "Anciens_examens" in page.locator(".bulk-summary-folder").inner_text()
        current = page.locator('.bulk-steps [aria-current="step"]')
        assert "Vérifie" in current.inner_text()
        page.screenshot(path=SCREENSHOT_DIR / "1-plan.png", full_page=True)

        page.get_by_role("button", name="Envoyer les 2 fichiers").click()
        page.wait_for_selector("[data-status=done]")
        assert Document.objects.filter(course=course, user=user).count() == 2
        assert page.locator(".bulk-done-check").is_visible()
        assert page.locator("progress").is_hidden()
        count = page.locator(".bulk-summary-count").inner_text()
        assert "2 fichiers envoyés pour 1 cours" in count
        assert page.locator("progress").get_attribute("value") == "2"
        page.screenshot(path=SCREENSHOT_DIR / "2-sent.png", full_page=True)

        # Picking the same folder again, as after a closed page: the server
        # finds the files that are already on DocHub during the send.
        page.goto(live_server.url + reverse("document_bulk_upload_pick"))
        picker.set_input_files(folder)
        page.wait_for_selector(".bulk-send")
        page.get_by_role("button", name="Envoyer les 2 fichiers").click()
        page.wait_for_selector("[data-status=done]")
        assert page.locator("progress").get_attribute("value") == "2"
        page.screenshot(path=SCREENSHOT_DIR / "3-sent-again.png", full_page=True)

    assert Document.objects.filter(course=course, user=user).count() == 2


def test_browser_checks_once_then_uploads_after_confirmation(
    live_server, logged_in_page, user, folder
):
    Course.objects.create(name="Algorithmique 1", slug="info-f101")
    entries_sent = []
    requests = []
    check_url = live_server.url + reverse("document_bulk_upload_check")
    file_url = live_server.url + reverse(
        "document_bulk_upload_file", args=["info-f101"]
    )

    def capture(route):
        requests.append(route.request.url)
        if route.request.url == check_url:
            entries_sent.append(json.loads(route.request.post_data_json["entries"]))
        route.continue_()

    with patch("documents.models.process_document.delay"), logged_in_page(user) as page:
        page.goto(live_server.url + reverse("document_bulk_upload_pick"))
        page.route("**/documents/upload/bulk/**", capture)
        page.locator("input[webkitdirectory]").set_input_files(folder)
        page.wait_for_selector(".bulk-summary")
        assert requests == [check_url]
        assert Document.objects.count() == 0

        page.get_by_role("button", name="Envoyer les 2 fichiers").click()
        page.wait_for_selector("[data-status=done]")
        assert requests == [check_url, file_url, file_url]
        assert Document.objects.count() == 2
        assert "Envoie" in page.locator('[aria-current="step"]').inner_text()
        assert page.locator(".bulk-lists").count() == 0
    entry = {
        "path": "Anciens_examens/Tableau.xlsx",
        "size": len(b"not really a spreadsheet"),
    }
    assert entry in entries_sent[0]
    assert len(entries_sent[0]) == 4


def test_lost_connection_stops_and_retry(live_server, logged_in_page, user, folder):
    Course.objects.create(name="Algorithmique 1", slug="info-f101")
    requests = []

    def fail_once(route):
        requests.append(route.request)
        if len(requests) == 2:
            route.abort()
        else:
            route.continue_()

    with patch("documents.models.process_document.delay"), logged_in_page(user) as page:
        page.goto(live_server.url + reverse("document_bulk_upload_pick"))
        page.route("**/upload/bulk/file/info-f101", fail_once)
        page.locator("input[webkitdirectory]").set_input_files(folder)
        page.wait_for_selector(".bulk-summary")
        page.get_by_role("button", name="Envoyer les 2 fichiers").click()
        page.wait_for_selector("[data-status=stopped]")
        assert Document.objects.count() == 1
        assert page.locator("progress").get_attribute("value") == "1"
        page.get_by_role("button", name="Réessayer").click()
        page.wait_for_selector("[data-status=done]")
        # The retry starts again at the file that failed.
        assert len(requests) == 3
        assert Document.objects.count() == 2
        assert page.get_by_role("button", name="Réessayer").is_hidden()


def test_new_selection_cancels_old_plan(
    live_server, logged_in_page, user, folder, tmp_path
):
    Course.objects.create(name="Algorithmique 1", slug="info-f101")
    other = tmp_path / "second"
    (other / "info-f101").mkdir(parents=True)
    (other / "info-f101" / "new.pdf").write_bytes(b"new content")
    requests = []

    with logged_in_page(user) as page:
        page.goto(live_server.url + reverse("document_bulk_upload_pick"))

        def hold_plan(route):
            requests.append(route)
            page.evaluate("count => window.heldPlans = count", len(requests))

        page.route(live_server.url + reverse("document_bulk_upload_check"), hold_plan)
        picker = page.locator("input[webkitdirectory]")
        picker.set_input_files(folder)
        page.wait_for_function("window.heldPlans === 1")
        picker.set_input_files(other)
        page.wait_for_function("window.heldPlans === 2")
        requests[1].fulfill(response=requests[1].fetch())
        folder_name = page.locator(".bulk-summary-folder")
        folder_name.filter(has_text="second").wait_for()
        assert page.locator(".bulk-file").count() == 1
        # Even if the old server request finishes later, it cannot replace the plan.
        requests[0].fulfill(response=requests[0].fetch())
        page.wait_for_timeout(100)
        assert folder_name.inner_text().strip() == "second"


def test_server_error_stops_batch(live_server, logged_in_page, user, folder):
    Course.objects.create(name="Algorithmique 1", slug="info-f101")
    requests = []

    def server_error(route):
        requests.append(route.request)
        route.fulfill(status=500, body="Server error")

    with logged_in_page(user) as page:
        page.goto(live_server.url + reverse("document_bulk_upload_pick"))
        page.locator("input[webkitdirectory]").set_input_files(folder)
        page.wait_for_selector(".bulk-summary")
        page.route("**/upload/bulk/file/info-f101", server_error)
        page.get_by_role("button", name="Envoyer les 2 fichiers").click()
        page.wait_for_selector("[data-status=stopped]")
        assert len(requests) == 1
        assert Document.objects.count() == 0
        assert "L'envoi s'est arrêté" in page.locator(".bulk-summary").inner_text()


def test_duplicate_found_during_upload(live_server, logged_in_page, user, tmp_path):
    course = Course.objects.create(name="Algorithmique 1", slug="info-f101")
    root = tmp_path / "export"
    (root / "info-f101").mkdir(parents=True)
    (root / "info-f101" / "first.pdf").write_bytes(b"same content")
    (root / "info-f101" / "renamed.pdf").write_bytes(b"same content")
    with patch("documents.models.process_document.delay"), logged_in_page(user) as page:
        page.goto(live_server.url + reverse("document_bulk_upload_pick"))
        page.locator("input[webkitdirectory]").set_input_files(root)
        page.wait_for_selector(".bulk-summary")
        page.get_by_role("button", name="Envoyer les 2 fichiers").click()
        page.wait_for_selector("[data-status=done]")
        assert Document.objects.filter(course=course).count() == 1


@pytest.mark.parametrize("leave", [False, True])
@pytest.mark.parametrize("entry", ["prepare", "turbo_visit"])
def test_browser_back_warns_during_upload(
    live_server, logged_in_page, user, folder, leave, entry
):
    Course.objects.create(name="Algorithmique 1", slug="info-f101")
    requests = []

    def hold_upload(route):
        requests.append(route)
        if len(requests) == 1:
            page.evaluate("window.uploadHeld = true")
        else:
            route.continue_()

    with patch("documents.models.process_document.delay"), logged_in_page(user) as page:
        page.goto(live_server.url + reverse("document_bulk_upload"))
        if entry == "prepare":
            page.get_by_role("link", name="Mes fichiers sont prêts").click()
        else:
            # Any Turbo link to the picker must also create a native history entry.
            page.evaluate(
                "url => Turbo.visit(url)", reverse("document_bulk_upload_pick")
            )
        page.locator("input[webkitdirectory]").set_input_files(folder)
        page.wait_for_selector(".bulk-send")
        page.route("**/upload/bulk/file/info-f101", hold_upload)
        page.get_by_role("button", name="Envoyer les 2 fichiers").click()
        page.wait_for_selector("[data-status=sending]")
        page.wait_for_function("window.uploadHeld")

        with page.expect_event("dialog") as prompt:
            page.evaluate("() => { setTimeout(() => history.back(), 0); }")
        assert prompt.value.type == "beforeunload"
        if leave:
            prompt.value.accept()
            page.wait_for_url(live_server.url + reverse("document_bulk_upload"))
            page.wait_for_selector(".bulk-start")
            assert len(requests) == 1
            assert Document.objects.count() == 0
        else:
            prompt.value.dismiss()
            assert page.url == live_server.url + reverse("document_bulk_upload_pick")
            assert page.locator("[data-status=sending]").count() == 1
            assert len(requests) == 1
            requests[0].continue_()
            page.wait_for_selector("[data-status=done]")
            assert Document.objects.count() == 2
            # Once complete, Back no longer needs confirmation.
            page.go_back()
            page.wait_for_selector(".bulk-start")
