"""API clients use DocHub with a token, under the same limits as everyone."""

from pathlib import Path
from unittest.mock import patch

import pymupdf
import pytest
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from catalog.models import Course
from documents.models import Document, DocumentText
from stats.models import DailyStat, Metric
from users.models import AccessToken, DailyUsage, User

pytestmark = pytest.mark.django_db

SAMPLE_PDF = Path(__file__).resolve().parents[2] / "documents/tests/files/3pages.pdf"


@pytest.fixture(autouse=True)
def local_storage(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.STORAGES = {
        **settings.STORAGES,
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    }


@pytest.fixture
def user():
    return User.objects.create_user(
        netid="test_user", email="test@ulb.be", first_name="Test", last_name="User"
    )


@pytest.fixture
def course():
    return Course.objects.create(name="Test Course", slug="info-f101")


@pytest.fixture
def document(user, course):
    document = Document.objects.create(
        name="Notes de cours",
        user=user,
        course=course,
        state=Document.DocumentState.DONE,
    )
    with SAMPLE_PDF.open("rb") as fd:
        document.pdf.save("3pages.pdf", File(fd))
    return document


@pytest.fixture
def auth(user):
    _token, key = AccessToken.create_for(user, "Claude")
    return {"HTTP_AUTHORIZATION": f"Bearer {key}"}


def test_token_reads_a_course_as_json(client, auth, course, document):
    response = client.get(
        reverse("catalog:course_show", args=[course.slug]), {"format": "json"}, **auth
    )

    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == course.slug
    assert [doc["id"] for doc in data["documents"]] == [document.pk]
    token = AccessToken.objects.get()
    assert token.request_count == 1
    assert token.last_used is not None


def test_badly_copied_token_is_refused_with_a_hint(client, auth, course):
    cut_key = auth["HTTP_AUTHORIZATION"][:-1]
    response = client.get(
        reverse("catalog:course_show", args=[course.slug]),
        HTTP_AUTHORIZATION=cut_key,
    )
    assert response.status_code == 401
    assert "mal formé" in response.json()["error"]


def test_deleted_token_is_refused(client, auth, course):
    AccessToken.objects.all().delete()
    response = client.get(reverse("catalog:course_show", args=[course.slug]), **auth)
    assert response.status_code == 401
    assert "supprimé" in response.json()["error"]


def test_token_cannot_like(client, auth, document):
    response = client.post(reverse("document_like", args=[document.pk]), **auth)
    assert response.status_code == 403


def test_token_reads_the_text_of_a_document(client, auth, user, document):
    response = client.get(reverse("document_text", args=[document.pk]), **auth)

    assert response.status_code == 200
    assert response["Content-Type"] == "text/plain; charset=utf-8"
    text = response.content.decode()
    assert "--- Page 3 ---" in text
    assert "no text" not in text
    assert DailyUsage.today_for(user).downloads == 1


def test_token_uploads_a_document(client, auth, user, course):
    with patch("documents.models.process_document.delay"):
        response = client.post(
            reverse("document_put", args=[course.slug]) + "?format=json",
            {"file": SimpleUploadedFile("notes.pdf", b"some pdf"), "name": "Notes"},
            **auth,
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Notes"
    assert DailyUsage.today_for(user).uploads == 1


def test_token_upload_errors_are_json(client, auth, course):
    response = client.post(
        reverse("document_put", args=[course.slug]) + "?format=json", **auth
    )

    assert response.status_code == 422
    assert "file" in response.json()["errors"]


def test_daily_download_cap_is_shared_with_the_browser(
    client, settings, user, document
):
    settings.DAILY_CAPS = {**settings.DAILY_CAPS, "downloads": 1}
    client.force_login(user)

    assert client.get(reverse("document_pdf", args=[document.pk])).status_code == 200
    response = client.get(reverse("document_text", args=[document.pk]))
    assert response.status_code == 429


def test_rate_limit_also_applies_to_anonymous_visitors(client, settings, course):
    settings.RATE_LIMIT_PER_MINUTE = 2
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }
    url = reverse("catalog:course_show", args=[course.slug])

    assert client.get(url).status_code == 200
    assert client.get(url).status_code == 200
    response = client.get(url)
    assert response.status_code == 429
    assert response["Retry-After"] == "60"


def test_create_then_delete_a_token(client, user):
    client.force_login(user)

    response = client.post(reverse("api_tokens"), {"name": "Claude"}, follow=True)
    key = response.context["new_key"]
    assert key.startswith(AccessToken.PREFIX)
    assert key.removeprefix(AccessToken.PREFIX).isalnum()
    assert AccessToken.is_well_formed(key)
    assert not AccessToken.is_well_formed(key[:-1] + ("a" if key[-1] != "a" else "b"))
    assert AccessToken.objects.get().key_hash == AccessToken.hash_key(key)
    # The key is only shown once
    assert client.get(reverse("api_tokens")).context["new_key"] is None

    token = AccessToken.objects.get()
    client.post(reverse("api_token_delete", args=[token.pk]))
    assert not AccessToken.objects.exists()


def test_llms_txt(client):
    response = client.get("/llms.txt")
    assert response.status_code == 200
    assert "Authorization: Bearer" in response.content.decode()


def test_search_and_document_as_json(client, auth, course, document):
    response = client.get(reverse("course_search"), {"q": "Test", "format": "json"})
    assert response.json()["courses"][0]["slug"] == course.slug

    response = client.get(
        reverse("document_show", args=[document.pk]), {"format": "json"}, **auth
    )
    assert response.json()["text_url"] == f"/documents/{document.pk}/text"


def test_pages_without_text_are_marked(client, auth, user, course):
    document = Document.objects.create(
        name="Scan", user=user, course=course, state=Document.DocumentState.DONE
    )
    blank = pymupdf.open()
    blank.new_page()
    document.pdf.save("blank.pdf", ContentFile(blank.tobytes()))

    response = client.get(reverse("document_text", args=[document.pk]), **auth)

    assert "Page 1: no text, probably a scan" in response.content.decode()


def test_anonymous_visitors_get_no_course_or_document_json(client, course, document):
    for url in (
        reverse("catalog:course_show", args=[course.slug]),
        reverse("document_show", args=[document.pk]),
    ):
        assert client.get(url, {"format": "json"}).status_code == 401


def test_api_requests_are_counted_apart_in_stats(client, auth, user, document):
    client.get(reverse("document_text", args=[document.pk]), **auth)
    client.force_login(user)
    client.get(reverse("document_text", args=[document.pk]))

    rows = DailyStat.objects.filter(name=Metric.DOCUMENT_TEXT)
    assert sorted((row.api, row.value) for row in rows) == [(False, 1), (True, 1)]


def test_document_status_and_what_can_be_read(client, auth, user, course, document):
    def as_json(doc):
        url = reverse("document_show", args=[doc.pk])
        return client.get(url, {"format": "json"}, **auth).json()

    data = as_json(document)
    assert data["status"] == "ready"
    assert data["text_url"] == f"/documents/{document.pk}/text"

    zip_file = Document.objects.create(
        name="Archive", user=user, course=course, state=Document.DocumentState.DONE
    )
    data = as_json(zip_file)
    assert data["status"] == "ready"
    assert data["pdf_url"] is None
    assert data["text_url"] is None

    document.state = Document.DocumentState.PROCESSING
    document.save()
    data = as_json(document)
    assert data["status"] == "processing"
    assert data["text_url"] is None

    document.state = Document.DocumentState.ERROR
    document.save()
    assert as_json(document)["status"] == "error"


def test_text_is_kept_apart_and_reset_when_processed_again(client, auth, document):
    client.get(reverse("document_text", args=[document.pk]), **auth)
    assert DocumentText.objects.filter(document=document).exists()

    with patch("documents.models.process_document.delay"):
        document.add_to_queue()
    assert not DocumentText.objects.filter(document=document).exists()


def test_other_slug_spellings_redirect_with_their_query(client, auth, course):
    response = client.get("/catalog/course/INFO-F-101", {"format": "json"}, **auth)
    assert response.status_code == 302
    assert response["Location"] == "/catalog/course/info-f101?format=json"


def test_upload_to_another_slug_spelling_is_refused(client, auth, course):
    with patch("documents.models.process_document.delay"):
        response = client.post(
            "/documents/upload/INFO-F-101?format=json",
            {"file": SimpleUploadedFile("notes.pdf", b"some pdf")},
            **auth,
        )
    assert response.status_code == 400
    assert "/documents/upload/info-f101" in response.json()["error"]
    assert not Document.objects.filter(name="notes").exists()
