from django.conf import settings
from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from catalog.forms import SearchForm
from catalog.models import CourseUserView
from documents.models import Document, Vote
from users.models import User


def index(request):
    if request.user.is_authenticated:
        following = request.user.following_courses
        following_course = following.annotate(documents_count=Count("document"))
        ndocs = max(5, len(following))
        docs = (
            Document.objects.filter(course__in=following)
            .select_related("user", "course")
            .prefetch_related("tags")
            .order_by("-created")[:ndocs]
        )
        recent_views = (
            CourseUserView.objects.filter(user=request.user)
            .select_related("course")
            .order_by("-last_view")[:5]
        )
        recent_courses = [x.course for x in recent_views]
        staff_pick = (
            Document.objects.filter(staff_pick=True, hidden=False)
            .select_related("user", "course")
            .order_by("-created")
            .first()
        )

        # Onboarding checklist state; the copy for each step lives in the
        # template. Every flag flips once the user has performed the matching
        # action, and the whole checklist disappears once all four are done.
        is_following_any = following.exists()
        onboarding = {
            "viewed_course": bool(recent_courses),
            "following": is_following_any,
            "voted": Vote.objects.filter(user=request.user).exists(),
            "uploaded": Document.objects.filter(user=request.user).exists(),
        }
        onboarding_done = all(onboarding.values())

        context = {
            "search": SearchForm(),
            "recent_docs": docs,
            "recent_courses": recent_courses,
            "following_course": following_course,
            "staff_pick": staff_pick,
            "onboarding": onboarding,
            "onboarding_done": onboarding_done,
            # First week (or before following any course) gets the warm welcome
            # greeting; after that, the classic "N new documents" tagline, which
            # only makes sense once the user actually follows courses.
            "show_welcome_greeting": request.user.is_first_week or not is_following_any,
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
