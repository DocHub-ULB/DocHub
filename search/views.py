# TODO: is this dead code ?
from django.db import connection
from django.http import JsonResponse
from django.views.generic.list import ListView

import search.logic
from catalog.models import Course
from stats.models import DailyStat, Metric
from www.helpers import wants_json


class CourseSearchView(ListView):
    model = Course
    paginate_by = 30
    template_name = "search/course_list.html"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if query and self.request.user.is_authenticated:
            DailyStat.track(self.request, Metric.SEARCH_QUERY)
        return search.logic.search_course(query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["simplified"] = connection.vendor != "postgresql"
        # When the picker asks (?target=upload), point results at the upload
        # form instead of the course page.
        context["target"] = self.request.GET.get("target", "")
        return context

    def render_to_response(self, context, **response_kwargs):
        if not wants_json(self.request):
            return super().render_to_response(context, **response_kwargs)

        page = context["page_obj"]
        return JsonResponse(
            {
                "query": context["query"],
                "courses": [course.as_json() for course in page],
                "page": page.number,
                "has_next_page": page.has_next(),
            }
        )
