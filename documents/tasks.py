# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import subprocess
import hashlib
import uuid
import tempfile
import os


from celery import shared_task, chain
from PyPDF2 import PdfFileReader
from django.core.files.base import ContentFile, File
from actstream import action

from documents.models import Document, DocumentError
from .exceptions import DocumentProcessingError, MissingBinary, SkipException, ExisingChecksum


def on_failure(self, exc, task_id, args, kwargs, einfo):
    if isinstance(exc, SkipException):
        return None

    doc_id = args[0]
    print("Document {} failed.".format(doc_id))

    document = Document.objects.get(id=doc_id)
    document.state = "ERROR"
    document.save()
    action.send(document.user, verb="upload failed", action_object=document, target=document.course, public=False)

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
    else:
        raise DocumentProcessingError(document, "Wrong state : {}".format(document.state))

    if document.file_type in ('.pdf', 'application/pdf'):
        document.pdf = document.original
        document.save()
        process_pdf.delay(document_id)
    elif document.is_unconvertible():
        process_unconvertible.delay(document_id)
    else:
        process_office.delay(document_id)


@doctask
def checksum(self, document_id):
    document = Document.objects.get(pk=document_id)

    contents = document.original.read()
    hashed = hashlib.md5(contents).hexdigest()
    duplicata = Document.objects.filter(md5=hashed).exclude(md5='').first()

    if duplicata and duplicata.hidden:
        # If there exists a document with the same checksum
        # But the existing document is hidden, we delete the old
        # document and accept the new one
        duplicata.delete()
    elif duplicata:
        # Else, we reject the upload
        document.delete()
        # and break the task chain in celery
        self.request.callbacks = None
        raise ExisingChecksum("Document {} had the same checksum as {}".format(document_id, duplicata.id))

    document.md5 = hashed
    document.save()

    return document_id


checksum.throws = (ExisingChecksum,)


@doctask
def convert_office_to_pdf(self, document_id):
    document = Document.objects.get(pk=document_id)

    tmpfile = tempfile.NamedTemporaryFile()
    tmpfile.write(document.original.read())
    tmpfile.flush()

    try:
        sub = subprocess.check_output(['unoconv', '-f', 'pdf', '--stdout', tmpfile.name])
    except OSError:
        raise MissingBinary("unoconv")
    except subprocess.CalledProcessError as e:
        raise DocumentProcessingError(document, exc=e, message='"unoconv" has failed')

    document.pdf.save(str(uuid.uuid4()) + ".pdf", ContentFile(sub))

    tmpfile.close()

    return document_id


@doctask
def mesure_pdf_length(self, document_id):
    document = Document.objects.get(pk=document_id)
    reader = PdfFileReader(document.pdf)
    document.pages = reader.getNumPages()
    document.save()

    return document_id


@doctask
def finish_file(self, document_id):
    document = Document.objects.get(pk=document_id)
    document.state = 'DONE'
    document.save()

    action.send(document.user, verb="a uploadé", action_object=document, target=document.course)
    action.send(document.user, verb="upload success", action_object=document, target=document.course, public=False)

    return document_id


@doctask
def repair(self, document_id):
    document = Document.objects.get(pk=document_id)

    pdf_is_original = document.pdf == document.original

    tmpfile = tempfile.NamedTemporaryFile(prefix="dochub_pdf_repair_", suffix=".broken.pdf")
    tmpfile.write(document.pdf.read())
    tmpfile.flush()

    try:
        fd, output_path = tempfile.mkstemp(prefix="dochub_pdf_repair_", suffix=".repaired.pdf")
        os.close(fd)

        try:
            subprocess.check_output(["mutool", "clean", tmpfile.name, output_path], stderr=subprocess.STDOUT)
        except OSError:
            raise MissingBinary("mutool")
        except subprocess.CalledProcessError as e:
            raise DocumentProcessingError(document, exc=e, message='mutool clean has failed : %s' % e.output)

        with open(output_path, 'rb') as fd:
            document.pdf.save(str(uuid.uuid4()) + ".pdf", File(fd))
            document.pdf.close()

        tmpfile.close()
    finally:
        os.remove(output_path)

    if pdf_is_original:
        document.original = document.pdf

    document.state = 'REPAIRED'
    document.save()

    return document_id


process_pdf = chain(
    checksum.s(),
    mesure_pdf_length.s(),
    finish_file.s()
)

process_office = chain(
    checksum.s(),
    convert_office_to_pdf.s(),
    mesure_pdf_length.s(),
    finish_file.s()
)

process_unconvertible = chain(
    checksum.s(),
    finish_file.s()
)
