# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from www import settings


class User(AbstractBaseUser):

    USERNAME_FIELD = 'netid'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    DEFAULT_PHOTO = "/static/profile/default.jpg"
    objects = UserManager()

    netid = models.CharField(max_length=20, unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=127, null=False, blank=False)
    last_name = models.CharField(max_length=127, null=False, blank=False)
    email = models.CharField(max_length=255, null=False, blank=False)
    registration = models.CharField(max_length=80)
    photo = models.CharField(max_length=10, default="")
    welcome = models.BooleanField(default=True)
    comment = models.TextField(null=True)
    follow = models.ManyToManyField('polydag.Node', related_name='followed')

    @property
    def get_photo(self):
        photo = self.DEFAULT_PHOTO
        if self.photo != "":
            photo = "/static/profile/{0.netid}.{0.photo}".format(self)

        return photo

    @property
    def name(self):
        return "{0.first_name} {0.last_name}".format(self)

    def directly_followed(self):
        return self.follow.all()

    def followed_nodes_id(self):
        direct = self.follow.only('id')
        direct_descendants = map(lambda x: x.descendants_set(True), direct)
        indirect = reduce(lambda x, y: x | y, direct_descendants, set())
        indirect_ids = map(lambda x: x.id, indirect)
        return indirect_ids


class Inscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    section = models.CharField(max_length=80, null=True)
    year = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = ('user', 'section', 'year')
