from django.urls import reverse

import pytest
import responses

from users.models import CasFailure

pytestmark = pytest.mark.django_db


@pytest.fixture
def fake_base_url(settings):
    settings.BASE_URL = "http://example.com/"


def _mock_cas_response(fixture_path):
    with open(fixture_path) as fd:
        xml = fd.read()
    responses.add(
        responses.GET,
        "https://auth.ulb.be/proxyValidate",
        body=xml,
        status=200,
    )


@pytest.mark.parametrize(
    ("fixture", "code"),
    [
        ("users/tests/xml-fixtures/invalid-service.xml", "INVALID_SERVICE"),
        ("users/tests/xml-fixtures/invalid-ticket.xml", "INVALID_TICKET"),
    ],
)
@responses.activate
def test_recoverable_reject_redirects_to_login(client, fake_base_url, fixture, code):
    """CAS rejecting with a recoverable code triggers a quiet retry through /login."""
    _mock_cas_response(fixture)

    response = client.get(reverse("auth-ulb"), {"ticket": "ST-x"})

    assert response.status_code == 302
    assert response.url == reverse("login")
    assert response.cookies["cas_autoretry"].value == "1"

    failure = CasFailure.objects.get()
    assert failure.code == f"AUTORETRY__{code}"
    assert failure.ticket == "ST-x"


@pytest.mark.parametrize(
    ("fixture", "code"),
    [
        ("users/tests/xml-fixtures/invalid-service.xml", "INVALID_SERVICE"),
        ("users/tests/xml-fixtures/invalid-ticket.xml", "INVALID_TICKET"),
    ],
)
@responses.activate
def test_recoverable_reject_does_not_loop_when_cookie_set(
    client, fake_base_url, fixture, code
):
    """Once we've already tried to recover, surface the error instead of looping."""
    _mock_cas_response(fixture)
    client.cookies["cas_autoretry"] = "1"

    response = client.get(reverse("auth-ulb"), {"ticket": "ST-x"})

    assert response.status_code == 200
    assert f"CAS_{code}".encode() in response.content
    assert CasFailure.objects.filter(code=code).exists()
    assert not CasFailure.objects.filter(code__startswith="AUTORETRY__").exists()
