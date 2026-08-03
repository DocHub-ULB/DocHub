"""Real-life smoke test for the in-browser PDF preview (pdf.js).

The document viewer (``static/main.js`` -> ``Viewer#connect``) renders PDFs in
the browser with pdf.js, loaded from a CDN. It regressed once: importing
jsdelivr's ``/+esm`` auto-bundle made pdf.js take a Node.js code path in the
browser and throw ``TypeError: _t.getBuiltinModule is not a function`` when it
resolved the (relative) PDF URL, so the preview never rendered and users got the
"Oups !" fallback.

``test_document_preview_renders`` spins up the actual Django app, creates a real
Document with a real PDF, logs in, opens the document page in a real browser and
asserts the pages actually render. It is the durable guard: it fails if PDF
rendering breaks again for *any* reason.

This is heavy (real Chromium + CDN network) and opt-in. It is deselected by
default (``addopts = -m 'not playwright'``) and needs the optional deps::

    uv sync --group playwright && uv run playwright install chromium
    uv run pytest -m playwright
"""

import os
from pathlib import Path
from unittest import mock

from django.core.files import File
from django.core.files.base import ContentFile

import pytest

# Skip cleanly if the optional playwright package is not installed (e.g. CI).
sync_api = pytest.importorskip("playwright.sync_api")

pytestmark = [pytest.mark.playwright, pytest.mark.network]

SAMPLE_PDF = Path(__file__).resolve().parent / "files" / "3pages.pdf"
# A PDF header with no valid objects: pdf.js cannot build a document from it and
# getDocument() rejects. (The repo's broken.pdf only misses the "%" of its magic
# number, which pdf.js silently recovers from -- so it is not a useful control.)
BROKEN_PDF_BYTES = b"%PDF-1.7\nthis file is intentionally not a valid PDF\n%%EOF\n"


@pytest.fixture(scope="module")
def browser():
    # Playwright's sync API runs an asyncio loop in this thread, which trips
    # Django's async-safety guard on ORM calls. Our ORM/live_server calls are
    # genuinely synchronous, so allow them for the (opt-in) lifetime of the loop.
    with (
        mock.patch.dict(os.environ, {"DJANGO_ALLOW_ASYNC_UNSAFE": "1"}),
        sync_api.sync_playwright() as playwright,
    ):
        try:
            instance = playwright.chromium.launch()
        except sync_api.Error as exc:  # browser binary not installed
            pytest.skip(
                f"chromium not installed (run `playwright install chromium`): {exc}"
            )
        with instance:
            yield instance


def test_document_preview_renders(
    live_server, browser, client, settings, tmp_path, document
):
    """The document page renders its PDF pages in a real browser (end-to-end)."""
    # Keep uploaded files out of the repo's media/ dir.
    settings.MEDIA_ROOT = str(tmp_path)
    # Tests run with DEBUG=False + manifest static storage, which needs a
    # collectstatic run. Use the plain backend so {% static %} resolves to
    # /static/<name>, which live_server serves straight from the finders.
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    with SAMPLE_PDF.open("rb") as fd:
        document.pdf.save("3pages.pdf", File(fd), save=True)

    # Authenticate the browser by reusing a Django session cookie (the viewer and
    # the /pdf endpoint are both login-required).
    client.force_login(document.user)
    session_cookie = client.cookies[settings.SESSION_COOKIE_NAME]

    with browser.new_context() as context:
        context.add_cookies(
            [
                {
                    "name": settings.SESSION_COOKIE_NAME,
                    "value": session_cookie.value,
                    "url": live_server.url,
                }
            ]
        )
        page = context.new_page()
        page.goto(f"{live_server.url}/documents/{document.pk}")

        viewer = page.locator("[data-controller='viewer']")
        # The document has 3 pages. pdf.js creates one wrapper per page and
        # renders each into a <canvas> lazily as it scrolls into view. Scroll to
        # each page and wait until its canvas has a real size *and* actually
        # contains non-white ink -- a blank canvas would mean rendering silently
        # failed. (Poll rather than read once: the viewer marks a page "ready"
        # slightly before pdf.js finishes painting it.)
        for page_number in (1, 2, 3):
            wrapper = (
                f"[data-controller='viewer'] [data-viewer-page-param='{page_number}']"
            )
            page.locator(wrapper).scroll_into_view_if_needed()
            page.wait_for_function(
                """(selector) => {
                    const canvas = document.querySelector(selector);
                    if (!canvas || !canvas.width || !canvas.height) return false;
                    const ctx = canvas.getContext("2d");
                    const d = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                    for (let i = 0; i < d.length; i += 4) {
                        const r = d[i], g = d[i + 1], b = d[i + 2], a = d[i + 3];
                        if (a > 0 && (r < 245 || g < 245 || b < 245)) return true;
                    }
                    return false;
                }""",
                arg=f"{wrapper} canvas",
                timeout=30_000,
            )

        # Exactly three pages, and no error state.
        assert viewer.locator(".page-wrapper").count() == 3
        assert viewer.get_attribute("data-viewer-error-value") is None
        assert not viewer.locator(".error").is_visible()


def test_broken_pdf_shows_error(
    live_server, browser, client, settings, tmp_path, document
):
    """A broken PDF shows the "Oups !" error state instead of rendering.

    Negative control for test_document_preview_renders: it proves the "rendered"
    assertions mean something, and if the viewer markup changes both break.
    """
    settings.MEDIA_ROOT = str(tmp_path)
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    document.pdf.save("broken.pdf", ContentFile(BROKEN_PDF_BYTES), save=True)

    client.force_login(document.user)
    session_cookie = client.cookies[settings.SESSION_COOKIE_NAME]

    with browser.new_context() as context:
        context.add_cookies(
            [
                {
                    "name": settings.SESSION_COOKIE_NAME,
                    "value": session_cookie.value,
                    "url": live_server.url,
                }
            ]
        )
        page = context.new_page()
        page.goto(f"{live_server.url}/documents/{document.pk}")

        viewer = page.locator("[data-controller='viewer']")
        # getDocument() rejects, so the controller flips into its error state.
        page.wait_for_selector(
            "[data-controller='viewer'][data-viewer-error-value]", timeout=30_000
        )
        assert viewer.locator(".error").is_visible()
        # Nothing should have rendered.
        assert viewer.locator(".page-wrapper[data-viewer-ready]").count() == 0
