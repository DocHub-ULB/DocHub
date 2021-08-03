import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import reverse
from django.utils.html import format_html

from catalog.models import Course


def course_autocomplete(request):
    if request.is_ajax():
        query = request.GET.get("term", "")
        qs = Course.objects.filter(name__icontains=query)

        qs = qs.filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        )
        results = []
        for course in qs:
            results.append({
                "name": course.name,
                "slug": course.slug,
                "url": reverse("course_show", kwargs={"slug": course.slug}),
            })

        data = json.dumps(results)
    mimetype = "application/json"
    return HttpResponse(data, mimetype)
