from django.urls import path

import catalog.views

urlpatterns = [
    path("course/<slug:slug>", catalog.views.show_course, name="course_show"),
    path("join/<slug:slug>", catalog.views.join_course, name="join_course"),
    path("leave/<slug:slug>", catalog.views.leave_course, name="leave_course"),
    path("", catalog.views.finder, name="finder_root"),
    path("archives/", catalog.views.archive_index, name="archive_index"),
    path(
        "archives/<slug:edition_key>/",
        catalog.views.archive_finder,
        name="archive_edition",
    ),
    path(
        "archives/<slug:edition_key>/<path:slugs>/",
        catalog.views.archive_finder,
        name="archive_finder",
    ),
    path("f/", catalog.views.legacy_finder_redirect),
    path("f/<path:slugs>/", catalog.views.legacy_finder_redirect),
    path("<path:slugs>/", catalog.views.finder, name="finder"),
]
