from django.urls import path

import catalog.views
from catalog.autocomplete import course_autocomplete
from catalog.views import CategoryDetailView, CourseDetailView

urlpatterns = [
    path("course/<slug:slug>", CourseDetailView.as_view(), name="course_show"),
    path("category/<int:pk>", CategoryDetailView.as_view(), name="category_show"),
    path("join/<slug:slug>", catalog.views.join_course, name="join_course"),
    path("leave/<slug:slug>", catalog.views.leave_course, name="leave_course"),
    path("subscribed_courses/", catalog.views.show_courses, name="show_courses"),
    path(
        "unfollow_all_courses/",
        catalog.views.unfollow_all_courses,
        name="unfollow_all_courses",
    ),
    path("course_tree.json", catalog.views.course_tree, name="course_tree"),
    path("search/autocomplete", course_autocomplete, name="course-autocomplete"),
    path(
        "finder/<slug:id>/<slug:category_slug>/<str:mobile>",
        catalog.views.finder_turbo,
        name="finder_turbo",
    ),
    path(
        "finder/<slug:action>/<slug:course_slug>",
        catalog.views.finder_follow_course,
        name="set_course_follow",
    ),
]
