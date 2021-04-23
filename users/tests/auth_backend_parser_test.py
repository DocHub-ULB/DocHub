# import pytest

import datetime

from users.authBackend import UlbCasBackend

parse = UlbCasBackend()._parse_response


nimarcha = {
    'netid': 'nmar0003',
}


def test_parser():
    xml = open("users/tests/xml-fixtures/minimal.xml").read()
    ret = parse(xml)

    assert ret == nimarcha
