from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render
from django.template.loader import get_template
from django.views.generic import TemplateView

from actstream.models import user_stream

from catalog.forms import SearchForm
from catalog.models import Category
from documents.models import Document
from telepathy.models import Thread
from users.authBackend import UlbCasBackend
from users.models import User


def index(request):
    if request.user.is_authenticated:
        following = request.user.following_courses()
        ndocs = max(5, len(following))
        docs = Document.objects.filter(course__in=following).order_by("-created")[
            :ndocs
        ]
        context = {
            "search": SearchForm(),
            "stream": user_stream(request.user).exclude(verb="started following")[:10],
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
            "users": floor(User.objects.count()),
            "threads": floor(Thread.objects.count()),
        }
        return render(request, "index.html", context)


class HelpView(TemplateView):
    def get_context_data(self):
        r = super().get_context_data()
        r["faq_md"] = get_template("faq.md").render()
        return r
