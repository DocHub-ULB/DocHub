import models
from notify.models import PreNotification
from django.core.urlresolvers import reverse

def thread_save(**kwargs):
    assert kwargs['sender'] == models.Thread

    if kwargs['created']:
        thread = kwargs['instance']
        #TODO: use truncate instead of str[:N]
        PreNotification.objects.create(
            node=thread,
            text="Nouvelle discussion: "+thread.name[:50].encode('utf-8')+"...",
            url=reverse('thread_show', args=[thread.id]),
            user=thread.user.user
        )
    else:
        #TODO : maybe send a notif when a post is edited
        pass


def message_save(**kwargs):
    assert kwargs['sender'] == models.Message

    message = kwargs['instance']
    thread = message.thread
    poster = message.user

    if kwargs['created']:
        if message.previous:
            #TODO: use truncate instead of str[:N]
            PreNotification.objects.create(
                node=thread,
                text="Answer to {} by {}".format(
                    thread.name[:50].encode('utf-8'), poster.name.encode('utf-8')
                ),
                url=reverse('thread_show', args=[thread.id]),
                user=message.user.user
            )
    else:
        #TODO : maybe send a notif when a message is edited
        pass