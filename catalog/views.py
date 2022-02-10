import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.generic.detail import DetailView

from mptt.utils import get_cached_trees

from catalog.models import Category, Course, CourseUserView
from documents.models import Vote


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = "catalog/category.html"
    context_object_name = "category"


def view_course(request, slug):
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

    tags = {tag for doc in documents for tag in doc.tags.all()}
    documents = documents

    if request.user.is_authenticated:
        template = "catalog/course.html"
        CourseUserView.visit(request.user, course)
    else:
        template = "catalog/noauth/course.html"

    return render(
        request, template, {"tags": tags, "course": course, "documents": documents}
    )


def set_follow_course(request, slug: str, action: str) -> HttpResponse:
    """Makes a user either follow or unfollow a course"""
    course = get_object_or_404(Course, slug=slug)
    if action == "follow":
        course.followed_by.add(request.user)
    else:
        course.followed_by.remove(request.user)
    course.save()
    nextpage = request.GET.get("next", reverse("course_show", args=[slug]))
    return HttpResponseRedirect(nextpage)


@login_required
def join_course(request: HttpRequest, slug: str):
    return set_follow_course(request, slug, "follow")


@login_required
def leave_course(request: HttpRequest, slug: str):
    return set_follow_course(request, slug, "leave")


@login_required
def show_courses(request):
    # "suggestions": suggest(request.user),
    return render(
        request,
        "catalog/my_courses.html",
    )


@cache_page(60 * 60)
@login_required
def course_tree(request):
    def course(node: Course):
        return {
            "name": node.name,
            "id": node.id,
            "slug": node.slug,
        }

    def category(node: Category):
        return {
            "name": node.name,
            "id": node.id,
            "children": list(map(category, node.get_children())),
            "courses": list(map(course, node.course_set.all())),
        }

    categories = list(
        map(
            category,
            get_cached_trees(Category.objects.prefetch_related("course_set").all()),
        )
    )
    return HttpResponse(json.dumps(categories), content_type="application/json")


@login_required
def unfollow_all_courses(request):
    request.user.courses_set.clear()
    return redirect("show_courses")
