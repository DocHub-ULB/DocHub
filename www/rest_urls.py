# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from rest_framework_extensions.routers import NestedRouterMixin
from rest_framework.routers import DefaultRouter

import users.rest
import documents.rest
import catalog.rest
import telepathy.rest


class SimpleRouterWithNesting(NestedRouterMixin, DefaultRouter):
    pass

router = SimpleRouterWithNesting()

router.register(r'users', users.rest.UserViewSet)
router.register(r'pages', documents.rest.PageViewSet)
router.register(r'courses', catalog.rest.CourseViewSet)
router.register(r'categories', catalog.rest.CategoryViewSet)
router.register(r'threads', telepathy.rest.ThreadViewSet)
router.register(r'messages', telepathy.rest.MessageViewSet)

docs = router.register(r'documents', documents.rest.DocumentViewSet)
docs.register(
    r'page_set',
    documents.rest.PageViewSet,
    base_name='page-set',
    parents_query_lookups=['document'],
)

urlpatterns = [
    url("upvote/document/", documents.rest.UpvoteView.as_view(), name='upvote_document'),
    url("downvote/document/", documents.rest.DownvoteView.as_view(), name='downvote_document'),
] + router.urls
