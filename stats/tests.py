import json
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest

from catalog.models import Course
from documents.models import Document
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        netid="alice",
        email="alice@ulb.be",
        first_name="Al",
        last_name="Ice",
    )


@pytest.fixture
def course():
    return Course.objects.create(name="Algorithms", slug="info-f101")


def _extract_chart_data(body: str, stats_key: str) -> list[int]:
    """Pull the data-chart-data-value JSON off the canvas matching the given key."""
    needle = f'data-stats-key="{stats_key}"'
    canvas_start = body.index(needle)
    data_attr = 'data-chart-data-value="'
    data_start = body.index(data_attr, canvas_start) + len(data_attr)
    data_end = body.index('"', data_start)
    return json.loads(body[data_start:data_end])


def test_stats_smoke(client, user):
    client.force_login(user)
    resp = client.get(reverse("stats"))
    assert resp.status_code == 200
    body = resp.content.decode()
    for key in (
        "documents",
        "votes",
        "reports",
        "users",
        "rep_requests",
        "moderation",
        "cas_failures",
    ):
        assert f'data-stats-key="{key}"' in body


def test_stats_data_shape(client, user, course):
    """Seed documents on 3 distinct days within the range and check the chart data."""
    client.force_login(user)
    today = timezone.localdate()

    # Create 3 documents, then backdate them to 3 distinct days.
    days_back = [0, 2, 5]
    for offset in days_back:
        doc = Document.objects.create(user=user, course=course, name=f"Doc {offset}")
        target = timezone.now() - timedelta(days=offset)
        Document.objects.filter(pk=doc.pk).update(created=target)

    resp = client.get(reverse("stats") + "?range=30d")
    assert resp.status_code == 200

    body = resp.content.decode()
    # Pull the labels list out of the json_script tag.
    labels_marker = '<script id="chart-labels" type="application/json">'
    start = body.index(labels_marker) + len(labels_marker)
    end = body.index("</script>", start)
    labels = json.loads(body[start:end])

    # 30d range → 30 labels, last one is today.
    assert len(labels) == 30
    assert labels[-1] == today.isoformat()

    data = _extract_chart_data(body, "documents")

    assert len(data) == 30
    # The last 6 entries are 6 days ago → today, with 1s on offsets 0, 2, 5.
    assert data[-6:] == [1, 0, 0, 1, 0, 1]
    # Everything earlier is zero.
    assert data[:-6] == [0] * 24


def test_stats_invalid_range_falls_back(client, user):
    client.force_login(user)
    resp = client.get(reverse("stats") + "?range=banana")
    assert resp.status_code == 200
    # default is 1y → weekly bucketing → ~53 labels (Mondays covering ~52 weeks)
    body = resp.content.decode()
    labels_marker = '<script id="chart-labels" type="application/json">'
    start = body.index(labels_marker) + len(labels_marker)
    end = body.index("</script>", start)
    labels = json.loads(body[start:end])
    assert 52 <= len(labels) <= 54


def test_stats_weekly_bucketing(client, user, course):
    """In 1y range, documents in the same week land in the same bucket."""
    client.force_login(user)
    today = timezone.localdate()
    # Two docs in the same ISO week (today and 2 days ago).
    for offset in (0, 2):
        doc = Document.objects.create(user=user, course=course, name=f"Doc {offset}")
        target = timezone.now() - timedelta(days=offset)
        Document.objects.filter(pk=doc.pk).update(created=target)

    resp = client.get(reverse("stats") + "?range=1y")
    assert resp.status_code == 200
    body = resp.content.decode()

    data = _extract_chart_data(body, "documents")

    # Total should be 2; if today and 2-days-ago are in the same ISO week,
    # the current week's bucket is 2; otherwise the last two buckets are each 1.
    assert sum(data) == 2
    if today.weekday() >= 2:  # both fall in current week (Mon=0…Sun=6)
        assert data[-1] == 2
    else:
        assert data[-1] == 1
        assert data[-2] == 1


def test_stats_monthly_bucketing(client, user, course):
    """In 'all' range, the bucket count equals the number of distinct (year, month) tuples."""
    client.force_login(user)
    # User fixture's `created` is auto-set, so we already have ≥1 month.
    resp = client.get(reverse("stats") + "?range=all")
    assert resp.status_code == 200
    body = resp.content.decode()

    labels_marker = '<script id="chart-labels" type="application/json">'
    s = body.index(labels_marker) + len(labels_marker)
    e = body.index("</script>", s)
    labels = json.loads(body[s:e])
    # All labels must be a month-start date (day == 01).
    assert all(label.endswith("-01") for label in labels)
    assert len(labels) >= 1
