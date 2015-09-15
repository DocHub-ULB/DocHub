# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014-2015, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from django.test import TestCase
from django.contrib.auth import get_user_model

from graph.models import Course, Category
from documents.models import Document
from telepathy.models import Thread

from .tasks import find_candidates
from .models import PreNotification


class NotificationTaskTest(TestCase):
    def setUp(self):
        """
        Category
          +- Course
               +- ThreadCourse
               +- Document
                    +- ThreadDoc
        """
        user = get_user_model().objects.create(
            netid="42", email="test@ulb.ac.be",
            first_name="Test", last_name="de Test")
        self.course = Course.objects.create(
            slug="TEST-F-101", description="Cours de test")
        self.cat = Category.objects.create(
            slug="CAT-1", description="Categorie de test")
        self.doc = Document.objects.create(
            user=user, description="Document de test")
        self.thread_course = Thread.objects.create(
            name="Thread Course", user=user)
        self.thread_doc = Thread.objects.create(
            name="Thread Document", user=user)

        self.cat.add_child(self.course)
        self.course.add_child(self.doc)
        self.course.add_child(self.thread_course)
        self.doc.add_child(self.thread_doc)

        self.cat.save()
        self.course.save()
        self.doc.save()
        self.thread_doc.save()
        self.thread_course.save()

    def test_find_candidates_for_course(self):
        # Already on course
        notif = PreNotification(node=self.course)
        assert find_candidates(notif) == set([self.course])

    def test_find_candidates_for_category(self):
        # Empty for categories
        notif = PreNotification(node=self.cat)
        assert find_candidates(notif) == set()

    def test_find_candidates_for_doc(self):
        # Go up to course
        notif = PreNotification(node=self.doc)
        assert find_candidates(notif) == set([self.course])

    def test_find_candidates_for_thread(self):
        # When notifying new message, go up to thread
        notif = PreNotification(node=self.thread_course, sender_type="Message")
        assert find_candidates(notif) == set([self.thread_course])
        notif = PreNotification(node=self.thread_doc, sender_type="Message")
        assert find_candidates(notif) == set([self.thread_doc])

        # When notifying a new thread, go up to course
        notif = PreNotification(node=self.thread_course)
        assert find_candidates(notif) == set([self.course])
        notif = PreNotification(node=self.thread_doc)
        assert find_candidates(notif) == set([self.course])
