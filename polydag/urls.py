from django.conf.urls import patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    (r'^(\d+)\.?(html|json)?$', 'polydag.views.getNode'),
    (r'^(\d+)/short\.?(html|json)?$', 'polydag.views.getNodeShort'),
) + staticfiles_urlpatterns()