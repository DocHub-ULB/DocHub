# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from celery import shared_task, chain
from os import system, path, makedirs
import os
join = path.join
from shutil import rmtree, move
from urllib2 import urlopen, URLError, HTTPError
from contextlib import closing
import subprocess

from django.core.urlresolvers import reverse

from www import settings
from documents.models import Document, Page
from notify.models import Notification
from .exceptions import DocumentProcessingError, MissingBinary, UploadError, DownloadError
from .helpers import document_pdir, r, get_image_size


def on_failure(self, exc, task_id, args, kwargs, einfo):
    id = args[0]
    print("Document {} failed.".format(id))
    document = Document.objects.get(id=id)
    # TODO
    # document.failed = True
    # document.save()
    Notification.direct(
        user=document.user,
        text="Error when processing document: {}".format(document.name),
        node=document.parent,
        url=reverse('node_canonic', args=[document.parent.id]),
    )
    # TODO : alert admins


def doctask(*args, **kwargs):
    return shared_task(*args, bind=True, on_failure=on_failure, **kwargs)


@doctask
def download(self, document_id):
    document = Document.objects.get(pk=document_id)
    tmp_path = document_pdir(document)

    # Delete some old tries if any
    if path.exists(tmp_path):
        rmtree(tmp_path)

    makedirs(tmp_path)
    document.type = 'pdf'
    destination_name = join(tmp_path, "{}.{}".format(document_id, document.type))

    try:
        with closing(urlopen(document.source)) as original:
            try:
                with open(destination_name, 'w') as destination:
                    destination.write(original.read())
            except Exception as e:
                self.retry(countdown=r(), exc=e)

    except URLError as e:  # error on our side
        # TODO : warn operators
        raise UploadError(document, exc=e)

    except HTTPError as e:
        if e.code // 100 == 4:  # Bad url
            # TODO : warn operators and user
            raise DownloadError(document, e)
        else:
            self.retry(countdown=r(), exc=e)

    document.staticfile = destination_name
    document.save()

    try:
        if document.source.startswith("file://"):
            os.unlink(document.source[7:])
    except os.error:
        pass

    return document_id

download.max_retries = 5


@doctask
def calculate_pdf_length(self, document_id):

    document = Document.objects.get(pk=document_id)

    try:
        sub = subprocess.check_output(['pdfinfo', document.staticfile])
    except OSError:
        raise MissingBinary("pdfinfo")
    except subprocess.CalledProcessError:
        raise DocumentProcessingError('"pdfinfo" has failed')

    sub = sub.decode('ascii', 'ignore')

    pages = -1
    for line in sub.split('\n'):
        if line.startswith('Pages'):
            splitted = line.split(' ')
            pages = int(splitted[-1])
    if pages == -1:
        raise DocumentProcessingError("Lenght computation failed")

    document.pages = pages
    document.save()

    return document_id


@doctask
def index_pdf(self, document_id):
    document = Document.objects.get(pk=document_id)

    try:
        subprocess.check_output(['pdftotext', '-v'])
    except OSError:
        raise MissingBinary("pdftotext")
    except:
        print "Unknown error while testing pdftotext presence"
        raise

    # TODO : this could fail
    system("pdftotext " + document.staticfile)
    # change extension
    words_file = '.'.join(document.staticfile.split('.')[:-1]) + ".txt"

    # TODO : this could fail
    with open(words_file, 'r') as words:
        words  # Do a lot of cool things !
        pass

    return document_id


@doctask
def preview_pdf(self, document_id):
    try:
        subprocess.check_output(['gm', 'help'])
    except OSError:
        raise MissingBinary("gm")

    document = Document.objects.get(pk=document_id)
    source = document.staticfile

    destination_dir = join(document_pdir(document), "images")
    if not path.exists(destination_dir):
        makedirs(destination_dir)

    for pagenum in range(document.pages):
        heights = {}

        for width, size_name in [(120, 'm'), (600, 'n'), (900, 'b')]:
            destination = join(destination_dir, "{:0>6}_{}.jpg".format(pagenum, size_name))
            args = (width, ' -density 350', source, pagenum, destination)

            system('gm convert -geometry %dx -quality 90 %s "%s[%d]" %s' % args)

            width, height = get_image_size(destination)
            heights["height_{}".format(width)] = height

        page = Page.objects.create(numero=pagenum, **heights)
        document.add_child(page, acyclic_check=False)

    return document_id


@doctask
def finish_file(self, document_id):
    document = Document.objects.get(pk=document_id)
    tmp_path = document_pdir(document)

    destination = join(settings.UPLOAD_DIR, str(document.parent.id))

    if not path.exists(destination):
        makedirs(destination)

    move(tmp_path, destination)

    document.state = 'done'
    document.staticfile = join(destination, 'doc-{}'.format(document.id), '{}.pdf'.format(document.id))
    document.save()

    return document_id

process_pdf = chain(download.s(), calculate_pdf_length.s(), preview_pdf.s(), finish_file.s())
