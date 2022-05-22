from django.urls import path

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
    path("finder/", catalog.views.finder, name="finder"),
    path("finder/<path:slugs>/", catalog.views.finder, name="finder"),
]
