from django.core.management.base import BaseCommand
from notify.models import PreNotification, Notification

class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            # Get a pack of 20 notifs and send it to users
            objects = PreNotification.objects.order_by('created').filter(delivered=False)[:20]
            if len(objects) == 0:
                sleep(10)
            else
                for prenotif in objects:
                    nodeset = set([node])+node.parent_set()
                    for node in nodeset:
                        for follower in prenotif.node.followed:
                            Notification.objects.create(prenotif=prenotif, user=follower)
                            prenotif.delivered = True
                            prenotif.save()
    
