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

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from graph.models import Course
from www import settings
from django.db.models import Q
import re
from django.utils import timezone


class CustomUserManager(UserManager):

    def _create_user(self, netid, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not netid:
            raise ValueError('The given netid must be set')
        email = self.normalize_email(email)
        user = self.model(netid=netid, email=email, last_login=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, netid, email=None, password=None, **extra_fields):
        return self._create_user(netid, email, password, **extra_fields)

    def create_superuser(self, netid, email, password, **extra_fields):
        return self._create_user(netid, email, password, **extra_fields)


class User(AbstractBaseUser):

    USERNAME_FIELD = 'netid'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    DEFAULT_PHOTO = "/static/profile/default.jpg"
    objects = CustomUserManager()

    netid = models.CharField(max_length=20, unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=127, null=False, blank=False)
    last_name = models.CharField(max_length=127, null=False, blank=False)
    email = models.CharField(max_length=255, null=False, blank=False)
    registration = models.CharField(max_length=80, blank=True)
    photo = models.CharField(max_length=10, default="")
    welcome = models.BooleanField(default=True)
    comment = models.TextField(null=True, blank=True)
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

    get_full_name = name

    def directly_followed(self):
        return self.follow.all()

    def followed_nodes_id(self):
        return map(lambda x: x.id, self.follow.only('id').non_polymorphic())

    def followed_courses(self):
        return self.directly_followed().instance_of(Course)

    def is_moderator(self, node):
        return False

    @property
    def auto_follow(self):
        # TODO use user prefs
        return True

    @property
    def is_staff(self):
        # TODO bad idea !!
        return True

    def has_module_perms(self, *args, **kwargs):
        return self.is_staff

    def has_perm(self, *args, **kwargs):
        return self.is_staff

    def get_short_name(self, *args, **kwargs):
        return self.netid


class Inscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    faculty = models.CharField(max_length=80, null=True)
    section = models.CharField(max_length=80, null=True)
    year = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = ('user', 'section', 'faculty', 'year')

    @property
    def level(self):
        place = re.search('\d', self.section)
        if place:
            return int(self.section[place.start()])
        else:
            return None

    @property
    def type(self):
        place = re.search('\d', self.section)
        if place:
            return self.section[:place.start()]
        else:
            return self.section

    @property
    def next(self):
        next_starts = "{}{}".format(self.type, self.level + 1)
        # TODO : should use category slugs and not Inscriptions
        return Inscription.objects.filter(section__startswith=next_starts)
