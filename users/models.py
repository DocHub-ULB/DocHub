# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

import re
import os
from os.path import join
import identicon

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils import timezone

from www import settings


class CustomUserManager(UserManager):
    PATTERN = re.compile('[\W_]+')

    def _create_user(self, netid, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not netid:
            raise ValueError('The given netid must be set')
        email = self.normalize_email(email)
        user = self.model(netid=netid, email=email, last_login=now, **extra_fields)
        if settings.IDENTICON:
            IDENTICON_SIZE = 120
            if not os.path.exists(join(settings.MEDIA_ROOT, "profile")):
                os.makedirs(join(settings.MEDIA_ROOT, "profile"))
            profile_path = join(settings.MEDIA_ROOT, "profile", "{}.png".format(netid))
            alpha_netid = self.PATTERN.sub('', netid)
            identicon.render_identicon(int(alpha_netid, 36), IDENTICON_SIZE / 3).save(profile_path)
            user.photo = 'png'
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, netid, email=None, password=None, **extra_fields):
        return self._create_user(netid, email, password, **extra_fields)

    def create_superuser(self, netid, email, password, **extra_fields):
        return self._create_user(netid, email, password, is_staff=True, **extra_fields)


class User(AbstractBaseUser):

    USERNAME_FIELD = 'netid'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    DEFAULT_PHOTO = join(settings.STATIC_URL, "images/default.jpg")
    objects = CustomUserManager()

    netid = models.CharField(max_length=20, unique=True, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=127, null=False, blank=False)
    last_name = models.CharField(max_length=127, null=False, blank=False)
    email = models.CharField(max_length=255, null=False, blank=False, unique=True)
    registration = models.CharField(max_length=80, blank=True)
    photo = models.CharField(max_length=10, default="")
    welcome = models.BooleanField(default=True)
    comment = models.TextField(null=True, blank=True)
    followed_courses = models.ManyToManyField('catalog.Course')

    is_staff = models.BooleanField(default=False)
    is_academic = models.BooleanField(default=False)
    is_representative = models.BooleanField(default=False)

    @property
    def get_photo(self):
        photo = self.DEFAULT_PHOTO
        if self.photo != "":
            photo = join(settings.MEDIA_URL, "profile/{0.netid}.{0.photo}".format(self))

        return photo

    @property
    def name(self):
        return "{0.first_name} {0.last_name}".format(self)


class Inscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    faculty = models.CharField(max_length=80, null=True)
    section = models.CharField(max_length=80, null=True)
    year = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = ('user', 'section', 'faculty', 'year')
