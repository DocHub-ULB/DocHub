# import pytest

from users.authBackend import NetidBackend, IntranetError
import glob

parse = NetidBackend()._parse_response


def test_parser_real_life():
    for fpath in glob.glob("users/tests/xml-private-data/*.xml"):
        xml = open(fpath).read()
        try:
            ret = parse(xml)
            assert ret is not None
        except IntranetError:
            pass
