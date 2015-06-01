from django.conf.urls import patterns, url, include
from rest_framework import routers

import users.rest
import documents.rest
import graph.rest

router = routers.DefaultRouter()

router.register(r'users', users.rest.UserViewSet)
router.register(r'documents', documents.rest.DocumentViewSet)
router.register(r'pages', documents.rest.PageViewSet)
router.register(r'courses', graph.rest.CourseViewSet)


urlpatterns = patterns(
    "",
    url(r'^', include(router.urls)),
)
