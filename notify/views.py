# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from json import dumps, loads
from notify.models import Notification

def jsonise_notifications(notifs):
    return {
        "notifs": [
            {'id': n.pk,
             'text': n.prenotif.text,
             'date': n.prenotif.created.isoformat(),
             'emitter': n.prenotif.node.id,
             'followed_node': n.node.id
            } for n in notifs
        ]
    }


def notifications_get(request):
    notifs = list(Notification.unread(request.user))
    if len(notifs) < 5:
        notifs += list(Notification.objects.filter(user=request.user, read=True)[:(5-len(notifs))])
    return HttpResponse(dumps(jsonise_notifications(notifs)), mimetype='application/json')


# POST /notifications/read/
# postdata: notifs_id=[<id>,<id>]
def notifications_read(request):
    if request.method == 'POST':
        notifs_id = loads(request.POST['notifs_id'])
        notifs = get_list_or_404(Notification, id__in=notifs_id)
        changed = notifs.update(read=True)
        return HttpResponse(dumps({'changed': changed}), mimetype='application/json')
