# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

from reversion import revisions as reversion


@reversion.register()
@python_2_unicode_compatible
class Question(models.Model):
    text = models.TextField(max_length=2000)
    context = models.CharField(max_length=500, default="")

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    course = models.ForeignKey('catalog.Course')

    def __str__(self):
        return self.text

    def fullname(self):
        return self.__str__()

    class Meta:
        ordering = ['-edited']


@reversion.register()
@python_2_unicode_compatible
class Answer(models.Model):
    text = models.TextField()

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    question = models.ForeignKey('questions.Question')

    def __str__(self):
        return self.text

    def fullname(self):
        return self.__str__()

    class Meta:
        ordering = ['-edited']


@python_2_unicode_compatible
class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    answer = models.ForeignKey('questions.Answer', related_name='votes')

    def __str__(self):
        return "%s voted on %s" % (self.user, self.answer)

    def fullname(self):
        return self.__str__()

    class Meta:
        unique_together = (("user", "answer"),)
