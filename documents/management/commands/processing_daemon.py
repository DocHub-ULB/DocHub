# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from sys import exit
from time import sleep
from signal import signal, SIGTERM
from django.core.management.base import BaseCommand
from www.settings import UPLOAD_DIR, UPLOAD_LOG, PARSING_WORKERS, SEARCH_SYSTEM
from documents.models import Page, PendingDocument as Task
from django.db import close_connection
from os import system, path, makedirs
from multiprocessing import Process
from urllib2 import urlopen
import subprocess

# TODO : rtfm django logging
import logging
logger = logging.getLogger('das_logger')
hdlr = logging.FileHandler(UPLOAD_LOG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Start tha processing deamon'

    def convert_page(self, document, source, pagenum):
        '''extract page and make some thumbnails with graphicsmagick'''
        destination = "{}/{}/{:0>6}_{:0>6}_{{}}.jpg".format(
            UPLOAD_DIR, document.parent.id, document.id, pagenum)

        #mini thumbnail
        h_120 = self.make_jepg(120, pagenum, source, destination.format('m'))
        #normal image
        h_600 = self.make_jepg(600, pagenum, source, destination.format('n'))
        #big image
        h_900 = self.make_jepg(900, pagenum, source, destination.format('b'))

        close_connection()
        page = Page.objects.create(numero=pagenum, height_120=h_120,
                                   height_600=h_600,
                                   height_900=h_900)
        document.attach(page,acyclic_check=False)


    def make_jepg(self, width, pagenum, source, destination):
        system('gm convert -geometry %dx -quality 90 %s "%s[%d]" %s' %
               (width, ' -density 350', source, pagenum, destination))
        height = int(subprocess.check_output(['gm', 'identify', '-format',
                                              '%h', destination]).strip())
        return height


    def parse_file(self, document, upfile):
        logger.info('Starting processing of document {} (from {}) : {}'.format(
                document.id, document.user.name, document.name.encode('utf-8')))
        filename = "{}/{}/{:0>4}.pdf".format(UPLOAD_DIR, document.parent.id,
                                       document.id)

        # check if course subdirectory exist
        if not path.exists(UPLOAD_DIR + '/' + str(document.parent.id)):
            makedirs(UPLOAD_DIR + '/' + str(document.parent.id))

        # original file saving
        fd = open(filename, 'w')
        fd.write(upfile.read())
        fd.close()

        # sauvegarde du nombre de page
        document.pages = len(subprocess.check_output(['gm', 'identify',
                                                filename]).split('\n')) - 1
        document.save()

        if SEARCH_SYSTEM:
            # activate the search system
            system("pdftotext " + filename)
            words = open("%s/%s/%04d.txt" % (UPLOAD_DIR, document.reference.slug,
                                             document.id), 'r')
            words.close()

        # iteration page a page, transform en png + get page size
        for pagenum in xrange(document.pages):
            self.convert_page(document, filename, pagenum)

        logger.info('End of processing of document %d' % document.id)


    def download_file(self, doc, url):
        logger.info('Starting download of document %d : %s' % (doc.id, url))
        return urlopen(url)


    def process_file(self, pending_id):
        close_connection()
        pending = Task.objects.get(pk=pending_id)
        try:
            pending.state = 'download'
            pending.save()
            raw = self.download_file(pending.document, pending.url)
            pending.state = 'process'
            pending.save()
            self.parse_file(pending.document, raw)
            pending.state = 'done'
            pending.save()

            # may fail if download url, don't really care
            system("rm /tmp/TMP402_%d.pdf" % pending.document.id)

        except Exception as e:
            logger.error('Process file error of document %d (from %s) : %s' %
                         (pending.document.id, pending.document.user.name,
                          str(e)))
            pending.document.delete()
            # TODO : do not delete, enqueue and retry later (2-3 times ?)
            # when we actualy delete, do this a bit more proprely
            # and maybe warn the user ?


    # drop here when the deamon is killed
    def terminate(self, a, b):
        close_connection()
        for worker, pending in self.workers:
            try:
                worker.terminate()
                pending.document.done = 0
                pending.document.save()
                pending.state = 'queued'
                pending.save()
        # fail quietly, not a good idea, but hey, we've got already been kill,
        # so what the hell?
            except:
                pass
        exit(0)


    def handle(self, *args, **options):
        self.workers = list()
        signal(SIGTERM, self.terminate)
        try:
            while True:
                sleep(10)
                close_connection()
                self.workers = [ (w,p) for w, p in self.workers if w.is_alive() ]
                # Avoid useless SQL queries
                if len(self.workers) >= PARSING_WORKERS:
                    continue

                # Pool seem less flexible
                pendings = list(Task.objects.filter(state='queued').order_by('id'))
                while len(self.workers) < PARSING_WORKERS and len(pendings) > 0:
                    pending = pendings.pop(0)
                    process = Process(target=self.process_file, args=(pending.id,))
                    process.start()
                    self.workers.append((process, pending))
        except KeyboardInterrupt:
            self.terminate(None,None)


