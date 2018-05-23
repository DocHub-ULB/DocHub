# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import subprocess
import hashlib
import uuid
import tempfile
import os
import contextlib
import re

from celery import shared_task, chain
from PyPDF2 import PdfFileReader
from django.core.files.base import ContentFile, File
from actstream import action
from django.conf import settings
from celery.exceptions import SoftTimeLimitExceeded

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


def short_doctask(*args, **kwargs):
    return shared_task(*args, bind=True, on_failure=on_failure, soft_time_limit=60, hard_time_limit=90, **kwargs)


@doctask
def process_document(self, document_id):
    if settings.READ_ONLY:
        raise Exception("Documents are read-only.")

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

        # Warn the user
        action.send(
            document.user,
            verb="a uploadé un doublon de",
            action_object=duplicata,
            target=document.course,
            public=False
        )
        raise ExisingChecksum(
            "Document {} had the same checksum as {}".format(document_id, duplicata.id)
        )

    document.md5 = hashed
    document.save()

    return document_id


checksum.throws = (ExisingChecksum,)


@short_doctask
def convert_office_to_pdf(self, document_id):
    try:
        document = Document.objects.get(pk=document_id)

        with file_as_local(document.original, prefix="dochub_unoconv_input_") as tmpfile:
            try:
                sub = subprocess.check_output(['unoconv', '-f', 'pdf', '--stdout', tmpfile.name])
            except OSError:
                raise MissingBinary("unoconv")
            except subprocess.CalledProcessError as e:
                raise DocumentProcessingError(document, exc=e, message='"unoconv" has failed: %s' % e.output[:800])

        document.pdf.save(str(uuid.uuid4()) + ".pdf", ContentFile(sub))

        return document_id

    except SoftTimeLimitExceeded as e:
        # If we timeouted, kill the faulty openoffice daemon
        # it will respawn at the next unoconv invocation
        os.system("killall soffice.bin")
        # Still raise the exception so the pipeline for this
        # document is still stopped
        raise e


@short_doctask
def mesure_pdf_length(self, document_id):
    document = Document.objects.get(pk=document_id)

    try:
        reader = PdfFileReader(document.pdf)
        num_pages = reader.getNumPages()
    except:
        num_pages = mutool_get_pages(document)
    document.pages = num_pages
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


@short_doctask
def repair(self, document_id):
    document = Document.objects.get(pk=document_id)

    pdf_is_original = document.pdf == document.original

    with file_as_local(document.pdf, prefix="dochub_pdf_repair_", suffix=".broken.pdf") as tmpfile:
        with temporary_file_path(prefix="dochub_pdf_repair_", suffix=".repaired.pdf") as output_path:
            try:
                subprocess.check_output(["mutool", "clean", "-gggg", "-l", tmpfile.name, output_path], stderr=subprocess.STDOUT)
            except OSError:
                raise MissingBinary("mutool")
            except subprocess.CalledProcessError as e:
                raise DocumentProcessingError(document, exc=e, message='mutool clean has failed : %s' % e.output[:900])

            with open(output_path, 'rb') as fd:
                document.pdf.save(str(uuid.uuid4()) + ".pdf", File(fd))
                document.pdf.close()

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


@contextlib.contextmanager
def file_as_local(fileobj, prefix="", suffix=""):
    tmpfile = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix)
    tmpfile.write(fileobj.read())
    tmpfile.flush()

    try:
        yield tmpfile
    finally:
        tmpfile.close()


@contextlib.contextmanager
def temporary_file_path(prefix="", suffix=""):
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.close(fd)

    try:
        yield path
    finally:
        os.remove(path)


def mutool_get_pages(document):
    with file_as_local(document.pdf, prefix="dochub_pdf_len_") as tmpfile:
        try:
            output = subprocess.check_output(["mutool", "info", tmpfile.name], stderr=subprocess.STDOUT)
        except OSError:
            raise MissingBinary("mutool")
        except subprocess.CalledProcessError as e:
            raise DocumentProcessingError(document, exc=e, message='mutool info has failed : %s' % e.output)

    lines = output.split(b'\n')
    for line in lines:
        match = re.match(rb'Pages: (\d+)', line)
        if match:
            return int(match.group(1))

    # Sliently fail if we did not find a page count
    return None
