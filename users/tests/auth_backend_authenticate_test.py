import pytest
import responses
from responses import matchers

from users.authBackend import CasRequestError, UlbCasBackend
from users.models import CasFailure, User

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


CAS_XML_TEMPLATE = """\
<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationSuccess>
        <cas:user>{netid}</cas:user>
        <cas:attributes>
            <cas:mail>{email}</cas:mail>
            <cas:sn>{last_name}</cas:sn>
            <cas:givenName>{first_name}</cas:givenName>
        </cas:attributes>
    </cas:authenticationSuccess>
</cas:serviceResponse>"""

TICKET = "test-ticket"
SERVICE_MATCHER = matchers.query_string_matcher(
    f"ticket={TICKET}&service=http%3A%2F%2Fexample.com%2Fauth-ulb"
)


def _mock_cas_response(netid, email, first_name="Test", last_name="User"):
    xml = CAS_XML_TEMPLATE.format(
        netid=netid, email=email, first_name=first_name, last_name=last_name
    )
    responses.add(
        responses.GET,
        "https://auth.ulb.be/proxyValidate",
        body=xml,
        status=200,
        match=[SERVICE_MATCHER],
    )


@responses.activate
def test_netid_match_updates_email(fake_base_url):
    """When netid matches an existing user, reuse it and update email."""
    User.objects.create_user(
        netid="glagaff", email="gaston.lagaffe@ulb.ac.be", first_name="Gaston"
    )

    _mock_cas_response("glagaff", "gaston.lagaffe@ulb.be")
    user = UlbCasBackend().authenticate(None, ticket=TICKET)

    assert user.netid == "glagaff"
    assert user.email == "gaston.lagaffe@ulb.be"
    assert User.objects.count() == 1


@responses.activate
def test_email_fallback_updates_netid(fake_base_url):
    """When netid doesn't match but email does, reuse the user and update netid."""
    User.objects.create_user(
        netid="fantasio", email="fantasio@ulb.be", first_name="Fantasio"
    )

    _mock_cas_response("fant0001", "fantasio@ulb.be")
    user = UlbCasBackend().authenticate(None, ticket=TICKET)

    assert user.netid == "fant0001"
    assert user.email == "fantasio@ulb.be"
    assert User.objects.count() == 1


@responses.activate
def test_no_match_creates_user(fake_base_url):
    """When neither netid nor email match, create a new user."""
    _mock_cas_response("mleblanc", "modeste.leblanc@ulb.be", "Modeste", "Leblanc")
    user = UlbCasBackend().authenticate(None, ticket=TICKET)

    assert user.netid == "mleblanc"
    assert user.email == "modeste.leblanc@ulb.be"
    assert user.first_name == "Modeste"
    assert user.last_name == "Leblanc"
    assert User.objects.count() == 1


@responses.activate
def test_fields_synced_on_login(fake_base_url):
    """All CAS fields are updated on every login."""
    User.objects.create_user(
        netid="pdemousk",
        email="prunelle.de.mouskinson@ulb.ac.be",
        first_name="Leon",
        last_name="Prunelle",
    )

    _mock_cas_response(
        "pdemousk", "prunelle.de.mouskinson@ulb.be", "Leon", "De Mouskinson"
    )
    user = UlbCasBackend().authenticate(None, ticket=TICKET)

    assert user.email == "prunelle.de.mouskinson@ulb.be"
    assert user.first_name == "Leon"
    assert user.last_name == "De Mouskinson"


@responses.activate
def test_no_duplicate_when_netid_and_email_match_different_users(fake_base_url):
    """When netid matches user A and email matches user B, prefer user A (netid)."""
    User.objects.create_user(
        netid="glagaff", email="gaston.lagaffe@ulb.ac.be", first_name="Gaston"
    )
    User.objects.create_user(
        netid="lechat", email="gaston.lagaffe@ulb.be", first_name="Le Chat"
    )

    _mock_cas_response("glagaff", "gaston.lagaffe@ulb.be")
    user = UlbCasBackend().authenticate(None, ticket=TICKET)

    assert user.netid == "glagaff"
    # Email not updated because Le Chat already has it
    assert user.email == "gaston.lagaffe@ulb.ac.be"
    assert User.objects.count() == 2

    # An EMAIL_CONFLICT failure should be logged
    failure = CasFailure.objects.get()
    assert failure.code == "EMAIL_CONFLICT"
    assert "glagaff" in failure.details
    assert "lechat" in failure.details
