from django.conf.urls import patterns

urlpatterns = patterns('',
    (r'^get.json$', 'notify.views.notifications_get'),
    (r'^(?P<id>[^/]*)/read$', 'notify.views.notification_read')
)