"""Fixtures shared by the whole test suite."""

import os
from contextlib import contextmanager
from unittest import mock

import pytest


@pytest.fixture(scope="session")
def browser():
    """A headless Chromium, for the opt-in ``playwright`` tests.

    Skips (rather than fails) when the optional dependency or the browser
    binary is missing, so a plain ``uv run pytest -m playwright`` on a fresh
    checkout tells you what to install instead of erroring out.
    """
    sync_api = pytest.importorskip("playwright.sync_api")

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


@pytest.fixture
def browser_settings(settings, tmp_path):
    """The settings a real browser needs to be served the app properly."""
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
    return settings


@pytest.fixture
def logged_in_page(browser, browser_settings, client, live_server):
    """Opens a browser page already logged in as the given user.

    Real logins go through the ULB's CAS, which we cannot drive from here, so
    hand the browser a session cookie instead, which is what CAS ends up doing
    anyway. Keyword arguments go to the browser context (``viewport=...``).
    """
    cookie_name = browser_settings.SESSION_COOKIE_NAME

    @contextmanager
    def open_page(user, **context_kwargs):
        client.force_login(user)
        cookie = client.cookies[cookie_name]
        with browser.new_context(**context_kwargs) as context:
            context.add_cookies(
                [
                    {
                        "name": cookie_name,
                        "value": cookie.value,
                        "url": live_server.url,
                    }
                ]
            )
            yield context.new_page()

    return open_page
