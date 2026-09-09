from collections import Counter
from dataclasses import dataclass
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.db.models import Case, Count, F, Q, Value, When
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from catalog.models import CatalogEdition, Category, Course, CourseUserView
from catalog.slug import normalize_slug
from documents.models import Vote
from stats.models import DailyStat, Metric


def slug_redirect(view):
    @wraps(view)
    def wrapper(request: HttpRequest, slug: str, *args, **kwargs):
        try:
            normalized = normalize_slug(slug)
        except ValueError:
            raise Http404("This is not a valid course slug.") from None
        if normalized != slug:
            return redirect(request.path.replace(slug, normalized))
        return view(request, slug, *args, **kwargs)

    return wrapper


@slug_redirect
def show_course(request, slug: str):
    course = get_object_or_404(Course, slug=slug)

    if not request.user.is_authenticated:
        display = Q(hidden=False)
    elif request.user.is_staff:
        display = Q()
    else:
        display = Q(hidden=True, user=request.user) | Q(hidden=False)

    documents = (
        course.document_set.exclude(state="ERROR")
        .filter(display)
        .select_related("course", "user")
        .prefetch_related("tags", "vote_set")
        .annotate(upvotes=Count("vote", filter=Q(vote__vote_type=Vote.VoteType.UPVOTE)))
        .annotate(
            downvotes=Count("vote", filter=Q(vote__vote_type=Vote.VoteType.DOWNVOTE))
        )
        .annotate(net_votes=F("upvotes") - F("downvotes"))
    )

    total_count = documents.count()
    staff_pick_count = documents.filter(staff_pick=True).count()

    only_staff_picks = "staff_pick" in request.GET
    if only_staff_picks:
        documents = documents.filter(staff_pick=True)

    sort = request.GET.get("sort")
    if sort == "top":
        documents = documents.order_by("-net_votes", "-created")
    elif sort == "dl":
        documents = documents.order_by("-downloads", "-created")
    else:
        sort = "recent"
        documents = documents.order_by("-created")

    primary_category = (
        course.categories.filter(type=Category.CategoryType.FACULTY).first()
        or course.categories.first()
    )

    course_name_first, _, course_name_rest = course.name.partition(" ")

    context = {
        "course": course,
        "course_name_first": course_name_first,
        "course_name_rest": course_name_rest,
        "tag_counts": Counter(
            tag for doc in documents for tag in doc.tags.all()
        ).most_common(),
        "documents": documents,
        "following": course.followed_by.filter(id=request.user.id).exists(),
        "sort": sort,
        "only_staff_picks": only_staff_picks,
        "total_count": total_count,
        "staff_pick_count": staff_pick_count,
        "primary_category": primary_category,
    }

    if request.user.is_authenticated:
        template = "catalog/course.html"
        CourseUserView.visit(request.user, course)
        DailyStat.track(Metric.COURSE_PAGE_VIEW)
    else:
        template = "catalog/noauth/course.html"

    return render(request, template, context)


@login_required
@slug_redirect
def set_follow_course(request, slug: str, action: str) -> HttpResponse:
    """Makes a user either follow or unfollow a course"""
    course = get_object_or_404(Course, slug=slug)
    if action == "follow":
        course.followed_by.add(request.user)
        DailyStat.track(Metric.COURSE_FOLLOW)
    else:
        course.followed_by.remove(request.user)
        DailyStat.track(Metric.COURSE_UNFOLLOW)
    course.save()
    nextpage = request.GET.get("next", reverse("catalog:course_show", args=[slug]))
    return HttpResponseRedirect(nextpage)


@login_required
@slug_redirect
@require_POST
def join_course(request: HttpRequest, slug: str):
    return set_follow_course(request, slug, "follow")


@login_required
@slug_redirect
@require_POST
def leave_course(request: HttpRequest, slug: str):
    return set_follow_course(request, slug, "leave")


@dataclass
class ChildCategory:
    category: Category
    url: str


@dataclass
class Column:
    category: Category
    children: list[ChildCategory]
    title: str


# Diplomas first (bachelor, then master, then specialisation), everything else last.
_CATEGORY_TYPE_ORDER = Case(
    When(type=Category.CategoryType.BACHELOR, then=Value(0)),
    When(type=Category.CategoryType.MASTER, then=Value(1)),
    When(type=Category.CategoryType.MASTER_SPECIALIZATION, then=Value(2)),
    default=Value(3),
)


def finder(request: HttpRequest, slugs: str = "") -> HttpResponse:
    edition = get_object_or_404(CatalogEdition, status=CatalogEdition.Status.ACTIVE)
    return _show_edition(request, edition, _split_slugs(slugs))


def archive_index(request: HttpRequest) -> HttpResponse:
    archives = [
        {"name": edition.title, "url": _archive_finder_url(edition.key, [])}
        for edition in _archived_editions().order_by("-key")
    ]
    return render(request, "catalog/archive_index.html", {"archives": archives})


def archive_finder(
    request: HttpRequest, edition_key: str, slugs: str = ""
) -> HttpResponse:
    edition = get_object_or_404(
        CatalogEdition, key=edition_key, status=CatalogEdition.Status.ARCHIVED
    )
    return _show_edition(request, edition, _split_slugs(slugs))


def legacy_finder_redirect(request: HttpRequest, slugs: str = "") -> HttpResponse:
    # Old catalog URLs were /f/ULB/<faculty>/... for the active tree and
    # /f/archives/archives-<year>/arch-<year>-<slug>/... for the archives. Both
    # carried a redundant ULB root and per-edition slug prefixes; strip those and
    # 301 onto the new /<faculty>/... and /archives/<year>/<slug>/... routes.
    parts = _split_slugs(slugs)
    if not parts:
        return redirect("catalog:finder_root", permanent=True)
    if parts[0].lower() == "ulb":
        clean = [part.lower() for part in parts[1:]]
        return redirect(_active_finder_url(clean), permanent=True)
    if parts[0].lower() != "archives":
        raise Http404("Unknown legacy catalog path.")
    if len(parts) == 1:
        return redirect("catalog:archive_index", permanent=True)
    edition_key = parts[1].removeprefix("archives-").lower()
    remaining = parts[2:]
    prefix = f"arch-{edition_key}-"
    if remaining and remaining[0].lower() == f"{prefix}ulb":
        remaining = remaining[1:]
    clean = [part.lower().removeprefix(prefix) for part in remaining]
    return redirect(_archive_finder_url(edition_key, clean), permanent=True)


def _split_slugs(slugs: str) -> list[str]:
    return [slug for slug in slugs.split("/") if slug]


def _archived_editions():
    return CatalogEdition.objects.filter(
        status=CatalogEdition.Status.ARCHIVED,
        categories__slug="ULB",
    ).distinct()


def _active_finder_url(parts: list[str]) -> str:
    if not parts:
        return reverse("catalog:finder_root")
    return reverse("catalog:finder", args=["/".join(parts)])


def _archive_finder_url(edition_key: str, parts: list[str]) -> str:
    if not parts:
        return reverse("catalog:archive_edition", args=[edition_key])
    return reverse("catalog:archive_finder", args=[edition_key, "/".join(parts)])


def _edition_finder_url(edition: CatalogEdition, parts: list[str]) -> str:
    if edition.status == CatalogEdition.Status.ACTIVE:
        return _active_finder_url(parts)
    return _archive_finder_url(edition.key, parts)


def _resolve_category_path(root: Category, slug_list: list[str]) -> list[Category]:
    """Walk down from the ULB root, matching one child category per slug."""
    categories = []
    parent = root
    for slug in slug_list:
        matches = list(
            parent.children.filter(edition=root.edition, slug__iexact=slug)[:2]
        )
        if len(matches) != 1:
            raise Http404(f"Invalid category path segment: {slug}")
        parent = matches[0]
        categories.append(parent)
    return categories


def _show_edition(
    request: HttpRequest, edition: CatalogEdition, slug_list: list[str]
) -> HttpResponse:
    root = get_object_or_404(Category, edition=edition, slug="ULB")
    resolved = _resolve_category_path(root, slug_list)
    canonical = [category.slug.lower() for category in resolved]
    if slug_list != canonical:
        return redirect(_edition_finder_url(edition, canonical), permanent=True)

    DailyStat.track(Metric.FINDER_VIEW)
    if len(resolved) >= 2:
        DailyStat.track(Metric.FINDER_VIEW_DEEP)

    is_archive = edition.status == CatalogEdition.Status.ARCHIVED
    columns: list[Column] = []
    for depth, category in enumerate([root, *resolved]):
        children = category.children.filter(edition=edition)
        if depth == 0:
            children = children.filter(type=Category.CategoryType.FACULTY)
        children = children.order_by(_CATEGORY_TYPE_ORDER, "name")
        columns.append(
            Column(
                category,
                [
                    ChildCategory(
                        child,
                        _edition_finder_url(
                            edition, [*canonical[:depth], child.slug.lower()]
                        ),
                    )
                    for child in children
                ],
                edition.title if depth == 0 and is_archive else category.name,
            )
        )

    archive_index_url = None
    if not is_archive and not slug_list and _archived_editions().exists():
        archive_index_url = reverse("catalog:archive_index")

    return render(
        request,
        "catalog/finder.html",
        {
            "columns": columns,
            "extra_columns": range(max(0, 4 - len(columns))),
            "is_archive": is_archive,
            "archive_index_url": archive_index_url,
        },
    )
