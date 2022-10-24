from www import settings


def test_no_debug():
    assert settings.DEBUG is False
