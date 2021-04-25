import pytest
import responses

from users.authBackend import CasRequestError, UlbCasBackend
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

    # Log the user for the first time
    user = UlbCasBackend().authenticate(None, ticket=ticket)

    # We should create a user in the DB
    assert len(responses.calls) == 1
    assert isinstance(user, User)
    assert user.netid == "nmar0003"
    assert User.objects.filter(netid="nmar0003").count() == 1

    # Log the user a second time
    user = UlbCasBackend().authenticate(None, ticket=ticket)

    # We should reuse the same user
    assert len(responses.calls) == 2
    assert isinstance(user, User)
    assert user.netid == "nmar0003"
    assert User.objects.filter(netid="nmar0003").count() == 1


@responses.activate
def test_server_error(fake_base_url):
    ticket = "this-is-a-cas-ticket"

    responses.add(
        responses.GET,
        f"https://auth-pp.ulb.be/proxyValidate?ticket={ticket}&service=http%3A%2F%2Fexample.com%2Fauth-ulb",
        body="<xml>server error</xml>",
        status=500,
        match_querystring=True,
    )

    with pytest.raises(CasRequestError) as e:
        UlbCasBackend().authenticate(None, ticket=ticket)

    assert e.value.args[0].status_code == 500
