import json
from dataclasses import dataclass
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.detail import DetailView

from catalog.models import Category, Course
from catalog.slug import normalize_slug
from documents.models import Vote


def slug_redirect(view):
    @wraps(view)
    def wrapper(request: HttpRequest, slug: str, *args, **kwargs):
        try:
            normalized = normalize_slug(slug)
        except ValueError:
            raise Http404("This is not a valid course slug.")
        if normalized != slug:
            return redirect(request.path.replace(slug, normalized))
        return view(request, slug, *args, **kwargs)

    return wrapper


@slug_redirect
def show_course(request, slug: str):
    course = get_object_or_404(Course, slug=slug)

    documents = (
        course.document_set.exclude(state="ERROR", hidden=True)
        .select_related("course", "user")
        .prefetch_related("tags", "vote_set")
        .annotate(upvotes=Count("vote", filter=Q(vote__vote_type=Vote.VoteType.UPVOTE)))
        .annotate(
            downvotes=Count("vote", filter=Q(vote__vote_type=Vote.VoteType.DOWNVOTE))
        )
        .order_by("-edited")
    )

    context = {
        "course": course,
        "tags": {tag for doc in documents for tag in doc.tags.all()},
        "documents": documents,
        "following": course.followed_by.filter(id=request.user.id).exists(),
    }

    if request.user.is_authenticated:
        template = "catalog/course.html"
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
    else:
        course.followed_by.remove(request.user)
    course.save()
    nextpage = request.GET.get("next", reverse("catalog:course_show", args=[slug]))
    return HttpResponseRedirect(nextpage)


@login_required
@slug_redirect
def join_course(request: HttpRequest, slug: str):
    return set_follow_course(request, slug, "follow")


@login_required
@slug_redirect
def leave_course(request: HttpRequest, slug: str):
    return set_follow_course(request, slug, "leave")


@login_required
def my_courses(request):
    # "suggestions": suggest(request.user),
    return render(
        request,
        "catalog/my_courses.html",
    )


@login_required
def unfollow_all_courses(request):
    request.user.courses_set.clear()
    return redirect("home")


@dataclass
class Column:
    category: Category
    children: list[Category]
    depth: int
    category_prefix: str


def finder(request, slugs: str = ""):
    slug_list = slugs.split("/")
    categories = [get_object_or_404(Category, slug=x) for x in slug_list]

    for i in range(len(categories) - 1, 0, -1):
        if categories[i].parent != categories[i - 1]:
            raise Http404(f"Invalid category path, {i}")

    columns = []
    max_depth = len(categories)
    for i, category in enumerate(categories):
        depth = max_depth - i
        path_list = ["."] + [".."] * (depth - 1)
        columns.append(
            Column(
                category,
                category.get_children().order_by("name"),
                depth,
                "/".join(path_list),
            )
        )

    return render(
        request,
        "catalog/finder.html",
        {"columns": columns, "extra_columns": range(4 - len(columns))},
    )
