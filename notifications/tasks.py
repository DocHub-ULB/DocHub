from actstream.models import Action, followers
from celery import shared_task

from notifications.models import Notification


def user_wants_notification(user, action):
    """With an action and a user as input, determine
    if the user is interested to receive a notification"""

    if action.actor == user:
        # Do not self notify
        return False

    if action.verb == "a édité":
        # Editions are not useful
        return False
    elif action.verb == "a uploadé":
        return user.notify_on_new_doc
    elif action.verb == "a uploadé une nouvelle version de":
        return user.notify_on_new_doc
    elif action.verb == "a posté":
        return user.notify_on_new_thread
    elif action.verb == "a répondu":
        return user.notify_on_response
    elif action.verb == "a été uploadé":
        return user.notify_on_upload
    elif action.verb in ("started following",):
        # Do not notify when another user starts following something
        return False
    else:
        raise Exception(f"Unknown action verb: '{action.verb}'")


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
