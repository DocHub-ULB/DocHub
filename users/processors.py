# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def user(request):
    if hasattr(request, 'user') and request.user.is_authenticated():
        return {'user': request.user}
    return {}
