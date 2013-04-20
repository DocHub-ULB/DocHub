from django.conf.urls import patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    (r'^unread.json$', 'notify.views.notifications_get'),
    (r'^read.json$', 'notify.views.notifications_read')
)