from django.conf.urls import patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    (r'^(\d+)\.?(html|json)?$', 'polydag.views.getNode'),
) + staticfiles_urlpatterns()