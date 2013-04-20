from notify.models import Notification

def notify(request):
    if hasattr(request, 'user'):
        notifications = Notification.objects.filter(read=False,user=request.user)
        return {'notifcount':len(notifications) }
    return {}