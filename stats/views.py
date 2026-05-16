from typing import NamedTuple

import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.shortcuts import render
from django.utils import timezone

from documents.models import Document, DocumentReport, Vote
from moderation.models import ModerationLog, RepresentativeRequest
from users.models import CasFailure, User


class RangeOption(NamedTuple):
    key: str
    label: str
    days: int | None  # None means "since the first user"
    granularity: str  # "daily" | "weekly" | "monthly"


RANGE_OPTIONS = [
    RangeOption("30d", "30 derniers jours", 30, "daily"),
    RangeOption("90d", "90 derniers jours", 90, "daily"),
    RangeOption("1y", "1 an", 365, "weekly"),
    RangeOption("2y", "2 ans", 730, "weekly"),
    RangeOption("all", "Tout", None, "monthly"),
]
DEFAULT_RANGE = "1y"


def _range_option(value: str) -> RangeOption | None:
    for option in RANGE_OPTIONS:
        if option.key == value:
            return option
    return None


def _start_date(option: RangeOption, today: date) -> date:
    if option.days is not None:
        return today - timedelta(days=option.days - 1)
    first_user = User.objects.order_by("created").first()
    if first_user is None:
        return today
    return timezone.localtime(first_user.created).date()


def _next_month(d: date) -> date:
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)


def _buckets(start: date, end: date, granularity: str) -> list[date]:
    """Generate the list of bucket start dates from start to end (inclusive)."""
    buckets = []
    if granularity == "monthly":
        cur = date(start.year, start.month, 1)
        while cur <= end:
            buckets.append(cur)
            cur = _next_month(cur)
        return buckets
    if granularity == "weekly":
        cur = start - timedelta(days=start.weekday())  # Monday on/before start
        step = timedelta(days=7)
    else:
        cur = start
        step = timedelta(days=1)
    while cur <= end:
        buckets.append(cur)
        cur += step
    return buckets


def _trunc(date_field: str, granularity: str):
    if granularity == "monthly":
        return TruncMonth(date_field)
    if granularity == "weekly":
        return TruncWeek(date_field)
    return TruncDate(date_field)


def _series(
    queryset, date_field: str, start: date, end: date, granularity: str
) -> list[int]:
    """Return counts per bucket from start to end (inclusive), zero-filled."""
    trunc = _trunc(date_field, granularity)
    rows = (
        queryset.filter(
            **{f"{date_field}__date__gte": start, f"{date_field}__date__lte": end}
        )
        .annotate(bucket=trunc)
        .values("bucket")
        .annotate(count=Count("id"))
    )
    by_bucket: dict[date, int] = {}
    for row in rows:
        bucket = row["bucket"]
        # TruncWeek may return a datetime; normalize to date.
        if hasattr(bucket, "date"):
            bucket = bucket.date()
        by_bucket[bucket] = by_bucket.get(bucket, 0) + row["count"]
    return [by_bucket.get(b, 0) for b in _buckets(start, end, granularity)]


def _labels(start: date, end: date, granularity: str) -> list[str]:
    return [b.isoformat() for b in _buckets(start, end, granularity)]


@login_required
def stats(request):
    option = _range_option(request.GET.get("range", "")) or _range_option(DEFAULT_RANGE)

    today = timezone.localdate()
    start = _start_date(option, today)
    end = today
    granularity = option.granularity

    labels = _labels(start, end, granularity)

    charts = [
        {
            "section": "Contenu",
            "title": "Documents uploadés",
            "key": "documents",
            "data": _series(
                Document.objects.filter(import_source__isnull=True),
                "created",
                start,
                end,
                granularity,
            ),
        },
        {
            "section": "Contenu",
            "title": "Votes",
            "key": "votes",
            "data": _series(Vote.objects.all(), "when", start, end, granularity),
        },
        {
            "section": "Contenu",
            "title": "Documents signalés",
            "key": "reports",
            "data": _series(
                DocumentReport.objects.all(), "created", start, end, granularity
            ),
        },
        {
            "section": "Communauté",
            "title": "Nouveaux utilisateurs",
            "key": "users",
            "data": _series(User.objects.all(), "created", start, end, granularity),
        },
        {
            "section": "Communauté",
            "title": "Demandes de modérateur·trices",
            "key": "rep_requests",
            "data": _series(
                RepresentativeRequest.objects.all(),
                "created",
                start,
                end,
                granularity,
            ),
        },
        {
            "section": "Autres",
            "title": "Actions de modération",
            "key": "moderation",
            "data": _series(
                ModerationLog.objects.all(), "timestamp", start, end, granularity
            ),
        },
        {
            "section": "Autres",
            "title": "Erreurs de login ULB",
            "key": "cas_failures",
            "data": _series(
                CasFailure.objects.all(), "created", start, end, granularity
            ),
        },
    ]

    for chart in charts:
        chart["data_json"] = json.dumps(chart["data"])

    sections: dict[str, list[dict]] = {}
    for chart in charts:
        sections.setdefault(chart["section"], []).append(chart)

    return render(
        request,
        "stats/stats.html",
        {
            "range_key": option.key,
            "range_options": RANGE_OPTIONS,
            "labels": labels,
            "sections": sections,
            "start": start,
            "end": end,
        },
    )
