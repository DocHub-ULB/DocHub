from django.test import TestCase
import helpers
from datetime import datetime
import mock

def mock_datetime(y, m, d, H, M, S):
    res = mock.MagicMock()
    res.datetime = datetime
    res.today = mock.Mock(return_value=datetime(y, m, d))
    res.now = mock.Mock(return_value=datetime(y, m, d, H, M, S))
    return res

class SimpleTest(TestCase):
    Q1 = (2012, 12, 21, 11, 11, 11)
    Q2 = (2013, 2, 12, 10, 10, 10)

    def testQ1(self):
        helpers.datetime = mock_datetime(*self.Q1)
        self.assertEquals(2012, helpers.current_year())

    def testQ2(self):
        helpers.datetime = mock_datetime(*self.Q2)
        self.assertEquals(2012, helpers.current_year())

    def testQ1List(self):
        helpers.datetime = mock_datetime(*self.Q1)
        expected = [("2012-2013",)*2, ("Archives",)*2]
        self.assertEquals(expected, helpers.year_choices(backlog=1))

    def testQ2List(self):
        helpers.datetime = mock_datetime(*self.Q2)
        expected = [("2012-2013",)*2, ("Archives",)*2]
        self.assertEquals(expected, helpers.year_choices(backlog=1))
