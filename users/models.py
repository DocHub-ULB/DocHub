# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    DEFAULT_PHOTO = "http://faculty.sites.uci.edu/ltemplate/files/2011/04/generic_profile.jpg"
    
    user = models.OneToOneField(User)
    name = models.CharField(max_length=127)
    email = models.CharField(max_length=255)
    registration = models.CharField(max_length=80)
    welcome = models.BooleanField(default=True)
    comment = models.TextField(null=True)
    photo = models.CharField(max_length=80, null=True)
    follow = models.ManyToManyField('polydag.Node', related_name='followed')
    
    @property
    def get_photo(self):
        return self.photo if self.photo else self.DEFAULT_PHOTO


class Inscription(models.Model):
    user = models.ForeignKey(Profile)
    section = models.CharField(max_length=80, null=True)
    year = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = ('user', 'section', 'year')
