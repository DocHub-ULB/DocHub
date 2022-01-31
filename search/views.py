from django.views.generic.list import ListView

import search.logic
from catalog.models import Course


class CourseSearchView(ListView):

    model = Course
    paginate_by = 30
    template_name = "search/course_list.html"

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        return search.logic.search_course(query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("query", "")
        return context
