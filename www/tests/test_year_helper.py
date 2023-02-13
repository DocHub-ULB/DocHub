from datetime import UTC, datetime
from unittest import mock

from www import helpers


def mock_datetime(y, m, d, H, M, S):
    res = mock.MagicMock()
    res.today = mock.Mock(return_value=datetime(y, m, d, tzinfo=UTC))
    res.now = mock.Mock(return_value=datetime(y, m, d, H, M, S, tzinfo=UTC))
    return res


Q1 = (2012, 12, 21, 11, 11, 11)
Q2 = (2013, 2, 12, 10, 10, 10)
Q2_2014 = (2015, 3, 19, 15, 35, 22)


def test_Q1():
    helpers.datetime = mock_datetime(*Q1)
    assert helpers.current_year() == 2012


def test_Q2():
    helpers.datetime = mock_datetime(*Q2)
    assert helpers.current_year() == 2012


def test_Q2_2014():
    helpers.datetime = mock_datetime(*Q2_2014)
    assert helpers.current_year() == 2014


def test_Q1List():
    helpers.datetime = mock_datetime(*Q1)
    expected = [("2012-2013",) * 2, ("Archives",) * 2]
    assert expected == helpers.year_choices(backlog=1)


def test_Q2List():
    helpers.datetime = mock_datetime(*Q2)
    expected = [("2012-2013",) * 2, ("Archives",) * 2]
    assert expected == helpers.year_choices(backlog=1)
