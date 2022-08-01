# TODO: is this dead code ?
from django.db import connection
from django.db.models import Count
from django.views.generic.list import ListView

import search.logic
from catalog.models import Course


class CourseSearchView(ListView):

    model = Course
    paginate_by = 30
    template_name = "search/course_list.html"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        qs = search.logic.search_course(query)

        return qs.annotate(category_count=Count("categories"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["simplified"] = connection.vendor != "postgresql"
        return context
