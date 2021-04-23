from users.authBackend import UlbCasBackend

nimarcha = {
    'netid': 'nmar0003',
    'email': 'nmar0003@ulb.ac.be'
}


def test_parser():
    xml = open("users/tests/xml-fixtures/minimal.xml").read()
    ret = UlbCasBackend()._parse_response(xml)

    assert ret == nimarcha
