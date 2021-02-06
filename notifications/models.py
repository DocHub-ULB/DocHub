from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from actstream.models import Action


class Notification(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']
        unique_together = (("user", "action"),)


@receiver(post_save, sender=Action)
def action_save_handler(sender, created, instance, **kwargs):
    if not created:
        return
    handle_action.delay(instance.id)


# Import at the end to avoid cyclic imports
from notifications.tasks import handle_action  # NOQA
