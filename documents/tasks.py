# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from celery import shared_task
from os import system, path, makedirs, rename
join = path.join
from shutil import rmtree, move
from urllib2 import urlopen
from contextlib import closing
import subprocess


from www import settings 
from documents.models import Document, Page

def document_pdir(document):
    return join(settings.PROCESSING_DIR,"doc-{}".format(document.id))

def get_document(id):
    return Document.objects.get(pk=id)
    

@shared_task(bind=True)
def download(self, document_id, url):
    document = get_document(document_id)
    tmp_path = document_pdir(document)

    # Delete some old tries if any
    if path.exists(tmp_path):
        rmtree(tmp_path)

    makedirs(tmp_path)
    document.type = 'pdf'
    destination_name = join(tmp_path,"{}.{}".format(document_id,document.type))

    with closing(urlopen(url)) as original:
        with open(destination_name, 'w') as destination:
            destination.write(original.read())

    document.staticfile = destination_name
    document.save()

    try: # may fail if download url, don't really care
        system("rm /tmp/TMP402_%d.pdf" % pending.document.id)
    except:
        pass

    return document_id 


@shared_task(bind=True)
def pdf_lenght(self, document_id):
    document = get_document(document_id)
    filename = document.staticfile

    sub = subprocess.check_output(['gm', 'identify', filename])
    pages = len(sub.split('\n')) - 1

    document.pages = pages
    document.save()

    return document_id 

@shared_task(bind=True)
def index_pdf(self, document_id):
    document = get_document(document_id)
    filename = document.staticfile

    system("pdftotext " + filename)
    # change extension
    words_file = '.'.join(filename.split('.')[:-1]) + ".txt"

    with open(words_file, 'r') as words:
        # Do a lot of cool things !
        pass

    return document_id 

@shared_task(bind=True)
def preview_pdf(self, document_id):
    document = get_document(document_id)
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

            height = int(subprocess.check_output(['gm', 'identify', '-format', '%h', destination]).strip())
            heights["height_{}".format(width)] = height

        page = Page.objects.create(numero=pagenum, **heights)
        document.add_child(page, acyclic_check=False)

    return document_id 

@shared_task(bind=True)
def finish_file(self, document_id):
    document = get_document(document_id)
    tmp_path = document_pdir(document)

    destination = join(settings.UPLOAD_DIR, str(document.parent.id))

    if not path.exists(destination):
        makedirs(destination)

    move(tmp_path, destination)

    document.state = 'done'
    document.save()

    return document_id 