from www import helpers
from datetime import datetime
from unittest import mock


def mock_datetime(y, m, d, H, M, S):
    res = mock.MagicMock()
    res.today = mock.Mock(return_value=datetime(y, m, d))
    res.now = mock.Mock(return_value=datetime(y, m, d, H, M, S))
    return res


Q1 = (2012, 12, 21, 11, 11, 11)
Q2 = (2013, 2, 12, 10, 10, 10)
Q2_2014 = (2015, 3, 19, 15, 35, 22)


def test_Q1():
    helpers.datetime = mock_datetime(*Q1)
    assert 2012 == helpers.current_year()


def test_Q2():
    helpers.datetime = mock_datetime(*Q2)
    assert 2012 == helpers.current_year()


def test_Q2_2014():
    helpers.datetime = mock_datetime(*Q2_2014)
    assert 2014 == helpers.current_year()


def test_Q1List():
    helpers.datetime = mock_datetime(*Q1)
    expected = [("2012-2013",) * 2, ("Archives",) * 2]
    assert expected == helpers.year_choices(backlog=1)


def test_Q2List():
    helpers.datetime = mock_datetime(*Q2)
    expected = [("2012-2013",) * 2, ("Archives",) * 2]
    assert expected == helpers.year_choices(backlog=1)
