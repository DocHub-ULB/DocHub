import models
from notify.models import PreNotification
from django.core.urlresolvers import reverse

def thread_save(**kwargs):
    assert kwargs['sender'] == models.Thread

    thread = kwargs['instance']
    #TODO: use truncate instead of str[:N]
    PreNotification.objects.create(
        node=thread,
        text="Nouvelle discussion: "+thread.name[:50]+"...",
        url=reverse('thread_show', args=[thread.id]),
        user=thread.user.user
    )

def message_save(**kwargs):
    assert kwargs['sender'] == models.Message

    message = kwargs['instance']
    thread = message.thread
    poster = message.user

    #TODO: use truncate instead of str[:N]
    PreNotification.objects.create(
        node=thread,
        text="Answer to {} by {}".format(thread.name[:50],poster.name),
        url=reverse('thread_show', args=[thread.id]),
        user=message.user.user
    )