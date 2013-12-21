# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import models
from notify.models import PreNotification, Notification
from django.core.urlresolvers import reverse
from tasks import process_pdf
def pre_document_save(**kwargs):
    assert kwargs['sender'] == models.Document

    document = kwargs['instance']
    try:
        old_doc = models.Document.objects.get(pk=document.pk)
    except models.Document.DoesNotExist:
        # New Document
        pass # Do nothing
    else:
        if not old_doc.state == document.state: # State changed
            if document.state == 'done':
                Notification.direct(
                    user=document.user.user,
                    text="Finished processing document " + document.name,
                    node=document,
                    url=reverse('document_show', args=[document.id])
                )

                PreNotification.objects.create(
                    node=document,
                    text="Nouveau document: " + document.name,
                    url=reverse('document_show', args=[document.id]),
                    user=document.user.user
                )

        else: # State not changed
            pass # Do nothing
   
def post_document_save (**kwargs):
    assert kwargs['sender'] == models.Document
    document = kwargs['instance']

    if kwargs['created'] and document.state == 'pending':
        process_pdf.delay(document.id)


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