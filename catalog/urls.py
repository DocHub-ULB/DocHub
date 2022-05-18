from django.urls import path

import catalog.views
from catalog.autocomplete import course_autocomplete
from catalog.views import CategoryDetailView

urlpatterns = [
    path("course/<slug:slug>", catalog.views.show_course, name="course_show"),
    path("category/<int:pk>", CategoryDetailView.as_view(), name="category_show"),
    path("join/<slug:slug>", catalog.views.join_course, name="join_course"),
    path("leave/<slug:slug>", catalog.views.leave_course, name="leave_course"),
    path("subscribed_courses/", catalog.views.my_courses, name="show_courses"),
    path(
        "unfollow_all_courses/",
        catalog.views.unfollow_all_courses,
        name="unfollow_all_courses",
    ),
    path("search/autocomplete", course_autocomplete, name="course-autocomplete"),
]
