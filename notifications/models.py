# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from actstream.models import Action


class Notification(models.Model):
    user = models.ForeignKey('users.User')
    read = models.BooleanField(default=False)
    action = models.ForeignKey(Action)

    class Meta:
        ordering = ['-id']
        unique_together = (("user", "action"),)


@receiver(post_save, sender=Action)
def action_save_handler(sender, created, instance, **kwargs):
    if not created:
        return
    handle_action.delay(instance.id)


from tasks import handle_action
