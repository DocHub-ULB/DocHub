import pytest
import responses
from responses import matchers

from users.authBackend import CasRequestError, UlbCasBackend
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def fake_base_url(settings):
    settings.BASE_URL = "http://example.com/"


@responses.activate
def test_auth(fake_base_url):
    ticket = "this-is-a-cas-ticket"
    with open("users/tests/xml-fixtures/minimal.xml") as fd:
        xml = fd.read()

    responses.add(
        responses.GET,
        "https://auth.ulb.be/proxyValidate",
        body=xml,
        status=200,
        match=[
            matchers.query_string_matcher(
                f"ticket={ticket}&service=http%3A%2F%2Fexample.com%2Fauth-ulb"
            )
        ],
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
        "https://auth.ulb.be/proxyValidate",
        body="<xml>server error</xml>",
        status=500,
        match=[
            matchers.query_string_matcher(
                f"ticket={ticket}&service=http%3A%2F%2Fexample.com%2Fauth-ulb"
            )
        ],
    )

    with pytest.raises(CasRequestError) as e:
        UlbCasBackend().authenticate(None, ticket=ticket)

    assert e.value.args[0].status_code == 500
