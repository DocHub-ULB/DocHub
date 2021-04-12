from django.urls import path

import catalog.views
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
]
