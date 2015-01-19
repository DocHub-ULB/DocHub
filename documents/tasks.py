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
from wand.image import Image

from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile

from documents.models import Document, Page
from notify.models import Notification
from .exceptions import DocumentProcessingError, MissingBinary


class SkipException(StandardError):
    pass


class ExisingChecksum(SkipException):
    pass


def on_failure(self, exc, task_id, args, kwargs, einfo):
    if isinstance(exc, SkipException):
        return None
    did = args[0]
    print("Document {} failed.".format(did))

    document = Document.objects.get(id=did)
    document.state = "ERROR"
    document.save()

    Notification.direct(
        user=document.user,
        text="Une erreur c'est produite pendant la conversion de : {}".format(document.name),
        node=document.parent,
        url=reverse('node_canonic', args=[document.parent.id]),
        icon="x",
    )
    # TODO : alert admins


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

    document.pdf.save(str(uuid.uuid4()), ContentFile(sub))

    tmp.close()

    return document_id


# @doctask
# def compute_pdf_length(self, document_id):

#     document = Document.objects.get(pk=document_id)

#     try:
#         sub = subprocess.Popen(
#             ['pdfinfo', "-"],
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )
#     except OSError:
#         raise MissingBinary("pdfinfo")

#     content = document.pdf.read()
#     out, err = sub.communicate(content)

#     if out == "" or sub.returncode != 0:
#         raise DocumentProcessingError(document, message='"pdfinfo" has failed : {}'.format(err))

#     out = out.decode('ascii', 'ignore')

#     pages = -1
#     for line in out.split('\n'):
#         if line.startswith('Pages'):
#             splitted = line.split(' ')
#             pages = int(splitted[-1])
#     if pages == -1:
#         raise DocumentProcessingError(document, msg="Lenght computation failed")

#     document.pages = pages
#     document.save()

#     return document_id


# @doctask
# def index_pdf(self, document_id):
#     document = Document.objects.get(pk=document_id)

#     try:
#         subprocess.check_output(['pdftotext', '-v'])
#     except OSError:
#         raise MissingBinary("pdftotext")
#     except:
#         print "Unknown error while testing pdftotext presence"
#         raise

#     # TODO : this could fail
#     system("pdftotext " + document.pdf)
#     # change extension
#     words_file = '.'.join(document.pdf.split('.')[:-1]) + ".txt"

#     # TODO : this could fail
#     with open(words_file, 'r') as words:
#         words  # Do a lot of cool things !
#         pass

#     return document_id


@doctask
def preview_pdf(self, document_id):

    document = Document.objects.get(pk=document_id)

    pdf = Image(file=document.pdf)

    document.pages = len(pdf.sequence)
    document.save()

    jpg_obj = pdf.convert('jpg')

    for i in range(document.pages):

        page = Page.objects.create(numero=i)
        document.add_child(page, acyclic_check=False)

        for width in 120, 600, 900:
            with jpg_obj.sequence[i].clone() as cloned:
                cloned.transform(resize=str(width))
                result = cloned.make_blob()
                destination = page.__getattribute__('bitmap_' + str(width))
                destination.save(str(uuid.uuid4()), ContentFile(result))

    jpg_obj.close()
    pdf.close()

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
    # compute_pdf_length.s(),
    preview_pdf.s(),
    finish_file.s()
)

process_office = chain(
    sanity_check.s(),
    checksum.s(),
    convert_office_to_pdf.s(),
    # compute_pdf_length.s(),
    preview_pdf.s(),
    finish_file.s()
)
