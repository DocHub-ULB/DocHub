from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from catalog.models import Category, Course


def programTypeAndSlug(program) -> tuple:
    """Returns the type of the program (Bachelier, Master, CAP, ...)"""
    # FIXME : Maybe find a more elegant solution to define a program's type ?
    if "bachelier" in program.name.lower():
        return "Bachelier", "aaaaba"
    if "master de spécialisation" in program.name.lower():
        return "Master de spécialisation", "aamas"
    if "master" in program.name.lower():
        return "Master", "aaama"
    if "certificat" in program.name.lower():
        return "Certificat", "cap"
    if "agrégation" in program.name.lower():
        return "Agrégation", "aess"
    else:
        return "Autre", "zaut"


def buildOrderedProgramList(programs) -> list:
    """Builds a list of program types (Bachelier, Master, CAP) with the corresping programs in it"""
    program_dict: dict = {}

    for program in programs:
        program_type, type_slug = programTypeAndSlug(program)
        if type_slug not in program_dict.keys():
            program_dict[type_slug] = {
                "name": program_type,
                "slug": type_slug,
                "programs": [program],
            }
        else:
            program_dict[type_slug]["programs"].append(program)

    return sorted(
        (program for _, program in program_dict.items()), key=lambda x: x["slug"]
    )


def getEmptyFrame(request, id: str) -> HttpResponse:
    """Returns an empty frame"""
    return render(
        request,
        "finder/empty.html",
        context={
            "id": id,
        },
    )


def getFacFrame(request, mobile: str) -> HttpResponse:
    """Returns a redered turbo-frame containing a list of the facs"""
    root = get_object_or_404(Category, slug="root")
    facs = root.children.all().order_by("name")

    if mobile == "true":
        turbo_id = "mobile"
        futur_turbo_id = "mobile"
    else:
        turbo_id = "facs"
        futur_turbo_id = "programs"

    return render(
        request,
        "finder/fac.html",
        context={
            "facs": facs,
            "turbo_id": turbo_id,
            "futur_turbo_id": futur_turbo_id,
            "mobile": mobile,
        },
    )


def getProgramFrame(request, fac_slug: str, mobile: str) -> HttpResponse:
    """Returns a rendered turbo-frame containing a list of programs from the given fac"""
    fac = get_object_or_404(Category, slug=fac_slug)
    programs = fac.children.all().order_by("name")

    programs = buildOrderedProgramList(programs)

    if mobile == "true":
        turbo_id = "mobile"
        futur_turbo_id = "mobile"
    else:
        turbo_id = "programs"
        futur_turbo_id = "blocs"

    return render(
        request,
        "finder/programs.html",
        context={
            "program_types": programs,
            "turbo_id": turbo_id,
            "futur_turbo_id": futur_turbo_id,
            "mobile": mobile,
        },
    )


def getBlocFrame(request, program_slug: str, mobile: str) -> HttpResponse:
    """Returns a rendered turbo-frame containing the list of blocs from the given program"""
    program = get_object_or_404(Category, slug=program_slug)
    blocs = program.children.all().order_by("name")

    if mobile == "true":
        turbo_id = "mobile"
        futur_turbo_id = "mobile"
    else:
        turbo_id = "blocs"
        futur_turbo_id = "courses"

    return render(
        request,
        "finder/bloc.html",
        context={
            "blocs": blocs,
            "turbo_id": turbo_id,
            "futur_turbo_id": futur_turbo_id,
            "mobile": mobile,
        },
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
        context={"courses": courses, "turbo_id": turbo_id, "mobile": mobile},
    )