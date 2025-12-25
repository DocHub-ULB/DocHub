from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from catalog.forms import SearchForm
from catalog.models import CourseUserView
from documents.models import Document
from users.models import User


def index(request):
    if request.user.is_authenticated:
        following_course = request.user.following_courses
        following = request.user.following_courses
        ndocs = max(5, len(following))
        docs = (
            Document.objects.filter(course__in=following)
            .select_related("user")
            .prefetch_related("tags")
            .order_by("-created")[:ndocs]
        )
        recent_views = (
            CourseUserView.objects.filter(user=request.user)
            .select_related("course")
            .order_by("-last_view")[:5]
        )
        recent_courses = [x.course for x in recent_views]
        context = {
            "search": SearchForm(),
            "recent_docs": docs,
            "recent_courses": recent_courses,
            "following_course": following_course,
        }
        return render(request, "home.html", context)
    else:

        def floor(num, r=1):
            r = 10**r
            return int((num // r) * r) if r != 0 else 0

        if Document.objects.count():
            page_count = Document.objects.all().aggregate(Sum("pages"))["pages__sum"]
        else:
            page_count = 0

        context = {
            "debug": settings.DEBUG,
            "documents": floor(Document.objects.count()),
            "pages": floor(page_count, 2),
            "users": floor(User.objects.count()),
        }
        return render(request, "index.html", context)


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request):
    file = (settings.BASE_DIR / "static" / "root" / "favicon.ico").open("rb")
    return FileResponse(file)
