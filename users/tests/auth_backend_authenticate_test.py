from django.test.client import RequestFactory

import pytest
import responses

from users.authBackend import NetidBackend
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture()
def fake_base_url(settings):
    settings.BASE_URL = "http://example.com/"


@responses.activate
def test_auth(fake_base_url):
    ticket = "this-is-a-cas-ticket"
    xml = open("users/tests/xml-fixtures/minimal.xml").read()

    responses.add(
        responses.GET,
        f"https://auth-pp.ulb.be/proxyValidate?ticket={ticket}&service=http%3A%2F%2Fexample.com%2Fauth-ulb",
        body=xml,
        status=200,
        match_querystring=True,
    )

    rf = RequestFactory()
    user = NetidBackend().authenticate(rf.get("/this-is-a-fake-django-request"), ticket=ticket)

    assert len(responses.calls) == 1
    assert isinstance(user, User)
    assert user.netid == "nmar0003"
    assert User.objects.filter(netid="nmar0003").count() == 1
