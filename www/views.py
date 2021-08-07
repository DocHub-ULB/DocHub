from django.conf import settings
from django.db.models import Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.views.generic import TemplateView

from catalog.forms import SearchForm
from catalog.models import Category, Course
from documents.models import Document
from users.authBackend import UlbCasBackend
from users.models import User
from www.utils import buildOrderedProgramList


def index(request):
    if request.user.is_authenticated:
        following = request.user.following_courses
        ndocs = max(5, len(following))
        docs = Document.objects.filter(course__in=following).order_by("-created")[
            :ndocs
        ]
        context = {
            "search": SearchForm(),
            "recent_docs": docs,
            "faculties": Category.objects.get(level=0).children.all(),
        }
        return render(request, "home.html", context)
    else:

        def floor(num, r=1):
            r = 10 ** r
            return int((num // r) * r) if r != 0 else 0

        if Document.objects.count():
            page_count = Document.objects.all().aggregate(Sum("pages"))["pages__sum"]
        else:
            page_count = 0

        context = {
            "debug": settings.DEBUG,
            "documents": floor(Document.objects.count()),
            "pages": floor(page_count, 2),
            "users": floor(User.objects.count())
        }
        return render(request, "index.html", context)


def getEmptyFrame(request, id: str) -> HttpResponse:
    return render(
        request,
        "finder/empty.html",
        context={
            "id": id,
        }
    )


def getFacFrame(request) -> HttpResponse:
    root = get_object_or_404(Category, slug="root")
    facs = root.children.all().order_by("name")

    return render(
        request,
        "finder/fac.html",
        context={
            "facs": facs
        }
    )


def getProgramFrame(request, fac_slug: str) -> HttpResponse:
    if fac_slug == "mycourses":
        programs = request.user.getPrograms()
    else:
        fac = get_object_or_404(Category, slug=fac_slug)
        programs = fac.children.all().order_by("name")

    programs = buildOrderedProgramList(programs)

    return render(
        request,
        "finder/programs.html",
        context={
            "program_types": programs
        }
    )


def getBlocFrame(request, program_slug: str) -> HttpResponse:
    if program_slug.split('-')[0] == "mycourses":
        _, program_slug = program_slug.split('-', 1)
        blocs = request.user.getBlocs(program_slug)
    else:
        program = get_object_or_404(Category, slug=program_slug)
        blocs = program.children.all().order_by("name")

    return render(
        request,
        "finder/bloc.html",
        context={
            "blocs": blocs
        }
    )


def getCourseFrame(request, bloc_slug: str) -> HttpResponse:
    bloc = get_object_or_404(Category, slug=bloc_slug)
    courses = Course.objects.filter(categories=bloc).order_by("name")

    return render(
        request,
        "finder/course.html",
        context={
            "courses": courses,
            "bloc_slug": bloc.slug
        }
    )


def finder_turbo(request, id: str, category_slug: str):
    if category_slug == "empty":
        return getEmptyFrame(request, id)
    if id == "facs":
        return getFacFrame(request)
    if id == "programs":
        return getProgramFrame(request, category_slug)
    if id == "blocs":
        return getBlocFrame(request, category_slug)
    if id == "courses":
        return getCourseFrame(request, category_slug)
    else:
        raise Http404("l'ID recherché est introuvable")


def set_follow_course(request, action: str, course_slug: str, bloc_slug: str):
    course = get_object_or_404(Course, slug=course_slug)
    if action == "follow":
        course.followed_by.add(request.user)
    else:
        course.followed_by.remove(request.user)
    course.save()
    return JsonResponse({
        "status": "success"
    })

class HelpView(TemplateView):
    def get_context_data(self):
        r = super().get_context_data()
        r["faq_md"] = get_template("faq.md").render()
        return r
