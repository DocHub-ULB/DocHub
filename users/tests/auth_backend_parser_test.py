import pytest

from users.authBackend import CasParseError, CasRejectError, UlbCasBackend

# Parse valid cases


def test_parser():
    with open("users/tests/xml-fixtures/minimal.xml") as fd:
        xml = fd.read()
    ret = UlbCasBackend()._parse_response(xml)

    assert ret == {
        "netid": "nmar0003",
        "email": "this.is.an.email@ulb.ac.be",
        "first_name": "Nikita",
        "last_name": "Marchant",
    }


def test_wihout_email():
    with open("users/tests/xml-fixtures/no-email.xml") as fd:
        xml = fd.read()
    ret = UlbCasBackend()._parse_response(xml)

    assert ret == {
        "netid": "nmar0003",
        "email": "nmar0003@ulb.ac.be",
        "first_name": "nmar0003",
        "last_name": "nmar0003",
    }


# Parse invalid responses


def test_invalid_xml():
    with open("users/tests/xml-fixtures/invalid-xml.xml") as fd:
        xml = fd.read()

    with pytest.raises(CasParseError) as e:
        UlbCasBackend()._parse_response(xml)
    assert e.value.args[0] == "INVALID_XML"


@pytest.mark.parametrize(
    "path",
    [
        "users/tests/xml-fixtures/unknown-structure.xml",
        "users/tests/xml-fixtures/missing-user.xml",
    ],
)
def test_unknown_structure(path):
    with open(path) as fd:
        xml = fd.read()

    with pytest.raises(CasParseError) as e:
        UlbCasBackend()._parse_response(xml)
    assert e.value.args[0] == "UNKNOWN_STRUCTURE"


@pytest.mark.parametrize(
    ("path", "expected_error", "expected_text"),
    [
        (
            "users/tests/xml-fixtures/invalid-service.xml",
            "INVALID_SERVICE",
            "does not match supplied service",
        ),
        (
            "users/tests/xml-fixtures/invalid-ticket.xml",
            "INVALID_TICKET",
            "not recognized",
        ),
    ],
)
def test_invalid_service(path, expected_error, expected_text):
    with open(path) as fd:
        xml = fd.read()

    with pytest.raises(CasRejectError) as e:
        UlbCasBackend()._parse_response(xml)
    assert e.value.args[0] == expected_error
    assert expected_text in e.value.args[1]
