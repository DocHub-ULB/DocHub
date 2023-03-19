from datetime import datetime

import time_machine
from pytz import UTC

from www import helpers

Q1 = datetime(2012, 12, 21, 11, 11, 11, tzinfo=UTC)
Q2 = datetime(2013, 2, 12, 10, 10, 10, tzinfo=UTC)
Q2_2014 = datetime(2015, 3, 19, 15, 35, 22, tzinfo=UTC)


@time_machine.travel(Q1)
def test_Q1():
    assert helpers.current_year() == 2012


@time_machine.travel(Q2)
def test_Q2():
    assert helpers.current_year() == 2012


@time_machine.travel(Q2_2014)
def test_Q2_2014():
    assert helpers.current_year() == 2014


@time_machine.travel(Q1)
def test_Q1List():
    expected = [("2012-2013",) * 2, ("Archives",) * 2]
    assert expected == helpers.year_choices(backlog=1)


@time_machine.travel(Q2)
def test_Q2List():
    expected = [("2012-2013",) * 2, ("Archives",) * 2]
    assert expected == helpers.year_choices(backlog=1)
