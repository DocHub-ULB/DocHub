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

from __future__ import absolute_import
from __future__ import unicode_literals

from celery import shared_task, chain
from os import path
import subprocess
import hashlib
import uuid
join = path.join
import tempfile
from pyPdf import PdfFileReader

from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile

from documents.models import Document, Page, DocumentError
from notify.models import Notification
from .exceptions import DocumentProcessingError, MissingBinary


class SkipException(StandardError):
    pass


class ExisingChecksum(SkipException):
    pass


def on_failure(self, exc, task_id, args, kwargs, einfo):
    if isinstance(exc, SkipException):
        return None

    doc_id = args[0]
    print("Document {} failed.".format(doc_id))

    document = Document.objects.get(id=doc_id)
    document.state = "ERROR"
    document.save()

    # Notify the uploader
    Notification.direct(
        user=document.user,
        text="Une erreur c'est produite pendant la conversion de : {}".format(document.name),
        node=document.parent,
        url=reverse('node_canonic', args=[document.parent.id]),
        icon="x",
    )

    # Warn the admins
    DocumentError.objects.create(
        document=document,
        task_id=task_id,
        exception=exc,
        traceback=einfo.traceback,
    )


def doctask(*args, **kwargs):
    return shared_task(*args, bind=True, on_failure=on_failure, **kwargs)


@doctask
def process_document(self, document_id):
    document = Document.objects.get(pk=document_id)

    if document.state == "IN_QUEUE":
        document.state = "PROCESSING"
        document.save()
    elif document.state in ("PREPARING", "PROCESSING", "READY_TO_QUEUE"):
        raise DocumentProcessingError(document_id, "Wrong state : {}".format(document.state))
    elif document.state in ("DONE", "ERROR"):
        raise NotImplementedError(document_id, document.state)
        # TODO : clean destination + celery.send_task()

    if document.file_type in ('.pdf', 'application/pdf'):
        document.pdf = document.original
        document.save()
        process_pdf.delay(document_id)
    else:
        process_office.delay(document_id)


@doctask
def sanity_check(self, document_id):
    document = Document.objects.get(pk=document_id)

    if not document.original:
        raise DocumentProcessingError(document_id, "Missing original")

    return document_id


@doctask
def checksum(self, document_id):
    document = Document.objects.get(pk=document_id)

    contents = document.original.read()

    hashed = hashlib.md5(contents).hexdigest()
    query = Document.objects.filter(md5=hashed).exclude(md5='')
    if query.count() != 0:
        dup = query.first()
        Notification.direct(
            user=document.user,
            text='Votre document "{}" a été refusé car c\'est une copie conforme de {}'.format(document.name, dup.name),
            node=document.parent,
            url=reverse('node_canonic', args=[dup.id]),
            icon="x",
        )
        did = document.id
        document.delete()
        raise ExisingChecksum("Document {} has the same checksum as {}".format(did, dup.id))
    else:
        document.md5 = hashed
        document.save()

    return document_id

checksum.throws = (ExisingChecksum,)


@doctask
def convert_office_to_pdf(self, document_id):
    document = Document.objects.get(pk=document_id)

    tmp = tempfile.NamedTemporaryFile()
    tmp.write(document.original.read())
    tmp.flush()

    try:
        sub = subprocess.check_output(['unoconv', '-f', 'pdf', '--stdout', tmp.name])
    except OSError:
        raise MissingBinary("unoconv")
    except subprocess.CalledProcessError as e:
        raise DocumentProcessingError(document, exc=e, message='"unoconv" has failed')

    document.pdf.save(str(uuid.uuid4()) + ".pdf", ContentFile(sub))

    tmp.close()

    return document_id


@doctask
def mesure_pdf_length(self, document_id):
    document = Document.objects.get(pk=document_id)
    reader = PdfFileReader(document.pdf)
    document.pages = reader.getNumPages()
    document.save()

    return document_id


@doctask
def preview_pdf(self, document_id):
    try:
        subprocess.check_output(['gm', 'help'])
    except OSError:
        raise MissingBinary("gm")

    document = Document.objects.get(pk=document_id)

    for i in range(document.pages):
        page = Page.objects.create(numero=i, document=document)

        for width in 120, 600, 900:
            args = [
                "gm", "convert",
                "-geometry", "{}x".format(width),
                "-quality", "90",
                "-density", "300",
                "pdf:{}[{}]".format(document.pdf.path, i),
                "jpg:-"
            ]
            converter = subprocess.Popen(args, stdout=subprocess.PIPE)
            destination = page.__getattribute__('bitmap_' + str(width))
            destination.save(str(uuid.uuid4()) + ".jpg", ContentFile(converter.stdout.read()))

    return document_id


@doctask
def finish_file(self, document_id):
    document = Document.objects.get(pk=document_id)
    document.state = 'DONE'
    document.save()

    return document_id

process_pdf = chain(
    sanity_check.s(),
    checksum.s(),
    mesure_pdf_length.s(),
    preview_pdf.s(),
    finish_file.s()
)

process_office = chain(
    sanity_check.s(),
    checksum.s(),
    convert_office_to_pdf.s(),
    mesure_pdf_length.s(),
    preview_pdf.s(),
    finish_file.s()
)
