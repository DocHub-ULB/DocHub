# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from notify.models import PreNotification, Notification
from time import sleep
import signal
import www.settings as settings
from django.db import close_connection
from optparse import make_option

from logbook import Logger, FileHandler

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE"),
        )

    def handle(self, *args, **options):
        if options['filename']:
            log_handler = FileHandler(options['filename'])
            log_handler.push_application()
        self.log = Logger('Notification')

        self.log.notice('Start deamon')

        for sig in (signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
            signal.signal(sig, self.terminate)
        try:
            while True:
                self.process_pack(settings.PACK_SIZE)
        except KeyboardInterrupt:
            print ""
            self.terminate(None,None)

    def process_pack(self, pack_size):
        objects = PreNotification.objects.order_by('created').filter(delivered=False)[:pack_size]
        if len(objects) == 0:
            sleep(2)
        else:
            #Go ahead in pack
            for prenotif in objects:
                self.log.debug('Processing a notification : "{}"'.format(prenotif))
                notif_counter = 0
                nodeset = prenotif.node.ancestors_set()
                nodeset.add(prenotif.node)
                delivered = set()
                #Walk in ancestors graph
                for node in nodeset:
                    #Deliver notifs to followers of ancestor nodes
                    for follower in node.followed.all():
                        user = follower.user
                        if user!=prenotif.user and user not in delivered:
                            notif_counter += 1
                            delivered.add(user) #avoid duplicate notifs
                            Notification.objects.create(
                                prenotif=prenotif,
                                user=user,
                                node=node
                            )
                prenotif.delivered = True
                self.log.debug('Notification delivered {} time(s)'.format(notif_counter))
                prenotif.save()

    def terminate(self, signal_code, frame):
        if signal_code == None:
            signal_code = 'KeyboardInterrupt'
        self.log.notice('Caught signal #{}, exiting.'.format(signal_code))
        close_connection()
        self.log.info('Shutdown.')
        exit(0)

