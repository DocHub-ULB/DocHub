import models
from notify.models import PreNotification
from django.core.urlresolvers import reverse

def thread_save(**kwargs):
    assert kwargs['sender'] == models.Thread

    if kwargs['created']:
        thread = kwargs['instance']
        PreNotification.objects.create(
            node=thread,
            text="Nouvelle discussion: "+thread.name.encode('utf-8'),
            url=reverse('thread_show', args=[thread.id]),
            user=thread.user.user
        )


def message_save(**kwargs):
    assert kwargs['sender'] == models.Message

    message = kwargs['instance']
    thread = message.thread
    poster = message.user

    if kwargs['created']:
        if message.previous:
            PreNotification.objects.create(
                node=thread,
                text="Answer to {} by {}".format(
                    thread.name.encode('utf-8'), poster.name.encode('utf-8')
                ),
                url=reverse('thread_show', args=[thread.id]),
                user=message.user.user
            )