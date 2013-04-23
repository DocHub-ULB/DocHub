from django.db import models
from polydag.models import Node
from users.models import User


# 1. Event occurs in graph
# 2. Pre notif created
# 3. Notif daemon match against followers and create notif
# 4. User get notif and read it

class PreNotification(models.Model):
    created = models.DateTimeField(auto_now=True)
    node = models.ForeignKey(Node) # The node that initiated the notif
    text = models.CharField(max_length=160)
    delivered = models.BooleanField(default=False)
    url = models.URLField()
    user = models.ForeignKey(User) #The user that created the notification


class Notification(models.Model):
    user = models.ForeignKey(User)
    node = models.ForeignKey(Node) # The effective node followed by user
    prenotif = models.ForeignKey(PreNotification)
    read = models.BooleanField(default=False)

    @staticmethod
    def unread(user):
        """Return all unread notifications for user"""
        return Notification.objects.filter(user=user, read=False)

