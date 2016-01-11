# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from celery import shared_task
from actstream.models import followers, Action

from notifications.models import Notification


def user_wants_notification(user, action):
    if action.actor == user:
        return False

    if action.verb == "a édité":
        return False
    elif action.verb == "a uploadé":
        return user.notify_on_new_doc
    elif action.verb == "a posté":
        return user.notify_on_new_thread
    elif action.verb == "a répondu":
        return user.notify_on_response
    elif action.verb == "a mentionné":
        return user.notify_on_rmention
    elif action.verb == "a été uploadé":
        return user.notify_on_upload
    elif action.verb in ("started following",):
        return False
    else:
        raise Exception("Unknown action verb: '{}'".format(action.verb))


@shared_task
def handle_action(action_id):
    action = Action.objects.get(pk=action_id)
    if action.public:
        users = followers(action.target)
        users = [user for user in users if user_wants_notification(user, action)]
        notifications = [Notification(user=user, action=action) for user in users]

        Notification.objects.bulk_create(notifications)
    else:
        user = action.actor
        Notification.objects.create(user=user, action=action)
