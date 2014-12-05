# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

import models
from notify.models import PreNotification, Notification
from django.core.urlresolvers import reverse
#from tasks import process_upload


def pre_document_save(**kwargs):
    assert kwargs['sender'] == models.Document

    document = kwargs['instance']
    try:
        old_doc = models.Document.objects.get(pk=document.pk)
    except models.Document.DoesNotExist:
        # New Document
        pass  # Do nothing
    else:
        if not old_doc.state == document.state:  # State changed
            if document.state == 'DONE':
                Notification.direct(
                    user=document.user,
                    text='Conversion de "{}" terminée'.format(document.name),
                    node=document,
                    url=reverse('document_show', args=[document.id]),
                    icon="check"
                )

                PreNotification.objects.create(
                    node=document,
                    text="Nouveau document : {} dans {}".format(document.name, document.parent.slug),
                    url=reverse('document_show', args=[document.id]),
                    user=document.user,
                    sender_type="Document",
                    icon="page-copy"
                )

        else:  # State not changed
            pass  # Do nothing


# def post_document_save(**kwargs):
#     assert kwargs['sender'] == models.Document
#     document = kwargs['instance']

#     if kwargs['created'] and document.state in ('pending', 'preparing'):
#         process_upload.delay(document.id)
