from django.core.management.base import BaseCommand
from notify.models import PreNotification, Notification
from time import sleep

class Command(BaseCommand):
    PACK_SIZE = 20
    
    def handle(self, *args, **options):
        while True:
            # Get a pack of 20 notifs and send it to users
            objects = PreNotification.objects.order_by('created').filter(delivered=False)[:self.PACK_SIZE]
            if len(objects) == 0:
                sleep(10)
            else:
                #Go ahead in pack
                for prenotif in objects:
                    nodeset = prenotif.node.ancestors_set()
                    nodeset.add(prenotif.node)
                    #Walk in ancestors graph
                    for node in nodeset:
                        #Deliver notifs to followers of ancestor nodes
                        for follower in node.followed.all():
                            if follower!=prenotif.user:
                                Notification.objects.create(
                                    prenotif=prenotif, 
                                    user=follower.user, 
                                    node=node
                                )
                    prenotif.delivered = True
                    prenotif.save()
    
