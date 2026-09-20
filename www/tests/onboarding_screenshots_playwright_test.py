"""Visual report of the home page onboarding checklist.

The screenshots land in ``screenshots/onboarding/``.

    uv sync --group playwright && uv run playwright install chromium
    uv run pytest -m playwright www/tests/onboarding_screenshots_playwright_test.py
    open screenshots/onboarding/
"""

from datetime import timedelta
from pathlib import Path

import pytest
from django.conf import settings as django_settings

from catalog.models import Course
from documents.models import Document
from users.models import User

# Skip cleanly if the optional playwright package is not installed (e.g. CI).
pytest.importorskip("playwright.sync_api")

pytestmark = [pytest.mark.playwright, pytest.mark.network]

SAMPLE_PDF = django_settings.BASE_DIR / "documents" / "tests" / "files" / "3pages.pdf"
SCREENSHOT_DIR = django_settings.BASE_DIR / "screenshots" / "onboarding"

# A desktop window
VIEWPORT = {"width": 1280, "height": 1000}


class Screenshots:
    """Numbered, full-page screenshots of the home page."""

    def __init__(self, page, live_server, directory: Path):
        self.page = page
        self.live_server = live_server
        self.directory = directory
        self.count = 0

    def shot(self, name: str) -> None:
        """Load the home page from scratch and save a full-page screenshot."""
        self.page.goto(self.live_server.url)
        self.page.wait_for_selector(".home-hero")
        # Let the web fonts settle, otherwise the first screenshots are taken
        # with the fallback fonts and look different from the later ones.
        self.page.evaluate("document.fonts.ready.then(() => true)")

        self.count += 1
        self.page.screenshot(
            path=self.directory / f"{self.count}-{name}.png", full_page=True
        )


@pytest.fixture
def screenshot_dir() -> Path:
    """An empty ``screenshots/onboarding/``, so a run never mixes two stories."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in SCREENSHOT_DIR.iterdir():
        stale.unlink()
    return SCREENSHOT_DIR


def test_onboarding_screenshots(live_server, logged_in_page, screenshot_dir, capsys):
    """Walk a newcomer through the four onboarding steps, screenshotting each."""
    newcomer = User.objects.create_user(
        netid="newcomer", first_name="Alice", last_name="Dupont", email="alice@ulb.be"
    )
    author = User.objects.create_user(
        netid="author", first_name="Bertrand", last_name="Labevue", email="bl@ulb.be"
    )
    course = Course.objects.create(name="Algorithmique 1", slug="info-f101")
    for title in ("Résumé du cours", "Examen janvier 2025", "Notes de TP"):
        Document.objects.create(
            name=title, user=author, course=course, state=Document.DocumentState.DONE
        )

    with logged_in_page(newcomer, viewport=VIEWPORT) as page:
        shots = Screenshots(page, live_server, screenshot_dir)

        shots.shot("first-login")

        # Step 1: visiting a course page records a CourseUserView.
        page.goto(f"{live_server.url}{course.get_absolute_url()}")
        shots.shot("course-seen")

        # Step 2: follow that course.
        page.goto(f"{live_server.url}{course.get_absolute_url()}")
        page.get_by_role("button", name="Suivre ce cours").click()
        shots.shot("course-followed")

        # Step 3: like one of its documents.
        page.goto(f"{live_server.url}{course.get_absolute_url()}")
        page.locator(".doc-link").first.click()
        page.get_by_role("button", name="Ce doc m'a aidé").click()
        shots.shot("document-liked")

        # Step 4: share a document. The upload form hides its fields until the
        # Stimulus controller has seen the file, and Stimulus comes from a CDN,
        # so submit the form itself rather than hunting for a button that may
        # never appear. Everything server-side still runs for real.
        page.goto(f"{live_server.url}/documents/upload/{course.slug}")
        page.locator("#id_file").set_input_files(SAMPLE_PDF)
        page.locator("#document-upload").evaluate("form => form.submit()")
        page.wait_for_url(f"{live_server.url}{course.get_absolute_url()}")
        shots.shot("document-shared")

        # And finally the regular home page, a few weeks later: no more welcome
        # greeting, no more checklist.
        User.objects.filter(pk=newcomer.pk).update(
            created=newcomer.created - timedelta(days=30)
        )
        shots.shot("regular")

        # The only thing worth asserting: the four steps really did flip, so
        # the checklist is gone from the last screenshots.
        assert "onboarding-grid" not in page.content()

    with capsys.disabled():
        print(f"\n{shots.count} screenshots written to {screenshot_dir}")
