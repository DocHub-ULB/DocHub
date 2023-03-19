from django.db import connection

import pytest


def needs_postgres(fn):
    @pytest.mark.django_db()
    @pytest.mark.postgresql()
    @pytest.mark.skipif(
        connection.vendor != "postgresql",
        reason="This test requires a PostgreSQL database",
    )
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


@needs_postgres
def test_running_with_postgres():
    """
    This is a dummy test to check if our logic of @needs_postgres is correct
    and that the setup of GitHub actions is correct too.
    """
    assert True


# FIXME: add more tests (see https://github.com/UrLab/DocHub/issues/257)
