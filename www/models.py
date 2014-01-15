# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from users.models import Profile
from django.db.models.signals import post_save
from django.contrib.auth.models import User


# for all user creation, create profile with default value
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, registration=0)

post_save.connect(create_user_profile, sender=User)


from django.db.models.signals import post_syncdb
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app


# when create the DB with these models, don't create a super user
post_syncdb.disconnect(create_superuser, sender=auth_app,
                dispatch_uid="django.contrib.auth.management.create_superuser")
