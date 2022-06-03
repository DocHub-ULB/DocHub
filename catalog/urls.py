from django.urls import path
from django.views.generic import RedirectView

import catalog.views

urlpatterns = [
    path("course/<slug:slug>", catalog.views.show_course, name="course_show"),
    path("join/<slug:slug>", catalog.views.join_course, name="join_course"),
    path("leave/<slug:slug>", catalog.views.leave_course, name="leave_course"),
    path(
        "unfollow_all_courses/",
        catalog.views.unfollow_all_courses,
        name="unfollow_all_courses",
    ),
    path("", catalog.views.finder_root, name="finder_root"),
    path("f/", RedirectView.as_view(pattern_name="catalog:finder_root")),
    path("f/<path:slugs>/", catalog.views.finder, name="finder"),
]
