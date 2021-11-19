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
        following_course = request.user.following_courses
        following = request.user.following_courses
        ndocs = max(5, len(following))
        docs = Document.objects.filter(course__in=following).order_by("-created")[
            :ndocs
        ]
        context = {
            "search": SearchForm(),
            "recent_docs": docs,
            "faculties": Category.objects.get(level=0).children.all(),
            "following_course": following_course
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


def getFacFrame(request, mobile: str) -> HttpResponse:
    root = get_object_or_404(Category, slug="root")
    facs = root.children.all().order_by("name")

    if mobile == "true":
        turbo_id = "mobile"
        futur_turbo_id = "mobile"
    else :
        turbo_id = "facs"
        futur_turbo_id = "programs"

    return render(
        request,
        "finder/fac.html",
        context={
            "facs": facs,
            "turbo_id": turbo_id,
            "futur_turbo_id": futur_turbo_id,
            "mobile": mobile
        }
    )


def getProgramFrame(request, fac_slug: str, mobile: str) -> HttpResponse:
    fac = get_object_or_404(Category, slug=fac_slug)
    programs = fac.children.all().order_by("name")

    programs = buildOrderedProgramList(programs)

    if mobile == "true":
        turbo_id = "mobile"
        futur_turbo_id = "mobile"
    else :
        turbo_id = "programs"
        futur_turbo_id = "blocs"

    return render(
        request,
        "finder/programs.html",
        context={
            "program_types": programs,
            "turbo_id": turbo_id,
            "futur_turbo_id": futur_turbo_id,
            "mobile": mobile
        }
    )


def getBlocFrame(request, program_slug: str, mobile: str) -> HttpResponse:
    program = get_object_or_404(Category, slug=program_slug)
    blocs = program.children.all().order_by("name")

    if mobile == "true":
        turbo_id = "mobile"
        futur_turbo_id = "mobile"
    else :
        turbo_id = "blocs"
        futur_turbo_id = "courses"

    return render(
        request,
        "finder/bloc.html",
        context={
            "blocs": blocs,
            "turbo_id": turbo_id,
            "futur_turbo_id": futur_turbo_id,
            "mobile": mobile
        }
    )


def getCourseFrame(request, bloc_slug: str, mobile: str) -> HttpResponse:
    turbo_id = "courses"

    if bloc_slug == "mycourses":
        courses = request.user.following_courses
        turbo_id = "programs"
    else:
        bloc = get_object_or_404(Category, slug=bloc_slug)
        courses = Course.objects.filter(categories=bloc).order_by("name")

    if mobile == "true":
        turbo_id = "mobile"
    
    return render(
        request,
        "finder/course.html",
        context={
            "courses": courses,
            "turbo_id": turbo_id,
            "mobile": mobile
        }
    )


def finder_turbo(request, id: str, category_slug: str, mobile: str):
    if category_slug == "empty":
        return getEmptyFrame(request, id)
    if id == "facs":
        return getFacFrame(request, mobile)
    if id == "programs":
        return getProgramFrame(request, category_slug, mobile)
    if id == "blocs":
        return getBlocFrame(request, category_slug, mobile)
    if id == "courses":
        return getCourseFrame(request, category_slug, mobile)
    else:
        raise Http404("l'ID recherché est introuvable")


def set_follow_course(request, action: str, course_slug: str):
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
