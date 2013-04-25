import models
from notify.models import PreNotification, Notification
from django.core.urlresolvers import reverse

def document_save(**kwargs):
    assert kwargs['sender'] == models.Document


def pending_document_save(**kwargs):
    assert kwargs['sender'] == models.PendingDocument

    pending = kwargs['instance']
    if pending.state == 'done':
        # Send notification to the uploader
        Notification.direct(
            user=pending.document.user.user,
            text="Finished processing document "+pending.document.name,
            node=pending.document,
            url=reverse('document_show', args=[pending.document.id])
        )

        PreNotification.objects.create(
            node=pending.document,
            text="Nouveau document: "+pending.document.name.encode('utf-8'),
            url=reverse('document_show', args=[pending.document.id]),
            user=pending.document.user.user
        )

def document_delete(**kwargs):
    assert kwargs['sender'] == models.Document

    document = kwargs['instance']
    #TODO: only fire notification if converts failed, not if it is a normal delete
    #TODO: use truncate instead of str[:N]
    Notification.direct(
        user=document.user.user,
        text="Error when processing document: "+str(document.e)[:120],
        node=document.parent,
        #TODO : send to /node/id
        url=reverse('home'),
    )