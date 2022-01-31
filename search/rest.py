# TODO: is this dead code ?
from rest_framework import viewsets
from rest_framework.response import Response

import search.logic
from search.serializers import CourseSearchSerializer


class CourseSearchViewSet(viewsets.ViewSet):
    """
    Search for a course in the catalog.
    This endpoint is made for somthing like a live autocomplete, it returns max 30 items

    This endpoint is meant to be called only with a GET request and the `query` parameter.

    Try a query like <a href="?query=bas%20de%20doné">"?query=bas de doné"</a>
    to see the power of this endpoint.

    If in the query parameter we find something looking like a course slug (abcd-e-123, abcd-e1234, ABCD-E-123, ...)
    and the slug exists as an exact match, we only return that course as a result.
    Like <a href="?query=Info-H303">"?query=Info-H303</a>
    """

    def get_queryset(self):
        query = self.request.query_params.get("query", "")
        return search.logic.search_course(query)[:30]

    def list(self, request, format=None):
        serializer = CourseSearchSerializer(
            self.get_queryset(), context={"request": request}, many=True
        )
        return Response(serializer.data)
