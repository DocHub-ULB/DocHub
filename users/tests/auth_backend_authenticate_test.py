import pytest
from users.authBackend import NetidBackend
from users.models import User
import responses

pytestmark = pytest.mark.django_db


@responses.activate
def test_auth():
    sid = "this-is-a-sid"
    uid = 'this-is-a-uid-and-is-longer'
    xml = open("users/tests/xml-fixtures/nimarcha.xml").read()

    responses.add(
        responses.GET,
        f'https://www.ulb.ac.be/commons/check?_type=normal&_sid={sid}&_uid={uid}',
        body=xml, status=200,
        match_querystring=True
    )

    user = NetidBackend().authenticate(sid=sid, uid=uid)

    assert len(responses.calls) == 1
    assert isinstance(user, User)
    assert user.netid == 'nimarcha'
    assert User.objects.filter(netid='nimarcha').count() == 1
    assert open(f"/tmp/netids/{sid}__{uid}").read() == xml
    assert user.inscription_set.count() == 4
