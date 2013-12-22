# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models.signals import post_syncdb
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app


# when create the DB with these models, don't create a super user
post_syncdb.disconnect(create_superuser, sender=auth_app, dispatch_uid="django.contrib.auth.management.create_superuser")
