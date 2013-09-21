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
    if document.e:
        Notification.direct(
            user=document.user.user,
            text="Error when processing document: "+str(document.e),
            node=document.parent,
            url=reverse('node_canonic',args=[nodeid]),
        )