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
    
