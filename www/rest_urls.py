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
router.register(r'courses', catalog.rest.CourseViewSet)
router.register(r'categories', catalog.rest.CategoryViewSet)
router.register(r'threads', telepathy.rest.ThreadViewSet)
router.register(r'messages', telepathy.rest.MessageViewSet)
router.register(r'documents', documents.rest.DocumentViewSet)

urlpatterns = [
    url(r"vote/document/(?P<pk>\d+)", documents.rest.VoteView.as_view(), name='vote_document'),
] + router.urls
