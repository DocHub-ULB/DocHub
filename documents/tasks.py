# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from celery import shared_task, chain
from os import system, path, makedirs
join = path.join
from shutil import rmtree, move
from urllib2 import urlopen, URLError, HTTPError
from contextlib import closing
import subprocess


from www import settings
from documents.models import Document, Page
from .exceptions import DocumentProcessingError, MissingBinary, UploadError, DownloadError
from .helpers import document_pdir, r, get_image_size


@shared_task(bind=True)
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

    try:  # may fail if download url, don't really care
        system("rm /tmp/TMP402_%d.pdf" % document.id)
    except:
        pass

    return document_id

download.max_retries = 5


@shared_task(bind=True)
def calculate_pdf_length(self, document_id):
    document = Document.objects.get(pk=document_id)

    try:
        sub = subprocess.check_output(['pdfinfo', document.staticfile])
    except OSError:
        raise MissingBinary("pdfinfo")
    except subprocess.CalledProcessError:
        raise DocumentProcessingError('"pdfinfo" has failed')

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


@shared_task(bind=True)
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


@shared_task(bind=True)
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


@shared_task(bind=True)
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
