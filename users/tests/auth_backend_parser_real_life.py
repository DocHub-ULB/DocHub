# import pytest

import glob

import pytest

from users.authBackend import IntranetError, NetidBackend

parse = NetidBackend()._parse_response


@pytest.mark.parametrize("fpath", glob.glob("users/tests/xml-private-data/*.xml") + glob.glob("users/tests/xml-anonymized-data/*.xml"))
def test_parser_real_life(fpath):
    with open(fpath) as fd:
        xml = fd.read()
        ret = parse(xml)
        assert ret is not None
