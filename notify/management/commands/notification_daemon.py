from django.core.management.base import BaseCommand
from notify.models import PreNotification, Notification
from time import sleep
import signal
import www.settings as settings
from django.db import close_connection

class Command(BaseCommand):

    def handle(self, *args, **options):
        for sig in (signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
            signal.signal(sig, self.terminate)
        try:
            while True:
                self.process_pack(settings.PACK_SIZE)
        except KeyboardInterrupt:
            self.terminate(None,None)

    def process_pack(self, pack_size):
        objects = PreNotification.objects.order_by('created').filter(delivered=False)[:pack_size]
        if len(objects) == 0:
            sleep(2)
        else:
            #Go ahead in pack
            for prenotif in objects:
                nodeset = prenotif.node.ancestors_set()
                nodeset.add(prenotif.node)
                delivered = set()
                #Walk in ancestors graph
                for node in nodeset:
                    #Deliver notifs to followers of ancestor nodes
                    for follower in node.followed.all():
                        user = follower.user
                        if user!=prenotif.user and user not in delivered:
                            delivered.add(user) #avoid duplicate notifs
                            Notification.objects.create(
                                prenotif=prenotif,
                                user=user,
                                node=node
                            )
                prenotif.delivered = True
                prenotif.save()

    def terminate(self,a,b):
        close_connection()
        exit(0)

