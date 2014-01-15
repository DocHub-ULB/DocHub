# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils.html import escape
from xml.dom.minidom import parseString
from users.models import Inscription
from string import printable
from random import choice
from settings import ULB_AUTH, ULB_LOGIN
from urllib2 import urlopen
from base64 import b64encode


# redirect user to ulb intranet auth in respect of the url
def ulb_redirection(request, **kwargs):
    return render(request, 'redirection.html', {'url': ULB_LOGIN})


# redirect user to internal/his profile
def app_redirection(request, **kwargs):
    return HttpResponseRedirect(reverse('home'))


# decorator whom stop anonymous user and give them a 403
def stop_anon(function):
    def stop(request, *args, **kwargs):
        if request.user.is_authenticated():
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden('not authorized')
    return stop


# decorator whom stop non post request and give them a 403
def uniq_post(function):
    def stop(request, *args, **kwargs):
        if request.method == 'POST':
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden('not authorized')
    return stop


def get_text(nodelist):
    rc = [ node.data for node in nodelist if node.nodeType == node.TEXT_NODE ]
    return ''.join(rc)


def get_value(dom, name):
    nodes = dom.getElementsByTagName(name)
    real_node, found = None, 0
    if len(nodes) != 1:
        for n in nodes:
            if found:
                break
            for child in n.parentNode.childNodes:
                if child.nodeName == name:
                    real_node = child
                if (child.nodeName == 'status' and
                    get_text(child.childNodes) == 'registered'):
                    found = 1
        if found == 0:
            raise Exception("xml document not conform for " + name)
    else:
        real_node = nodes[0]
    return escape(get_text(real_node.childNodes))


def parse_user(raw):
    dom = parseString(raw)
    return {
        'ip': get_value(dom, "ipAddress"),
        'username': get_value(dom, "username"),
        'first_name': get_value(dom, "prenom").capitalize(),
        'last_name': get_value(dom, "nom").capitalize(),
        'email': get_value(dom, "email"),
        'registration': get_value(dom, "matricule"),
        'anet': get_value(dom, "anet"),
        'anac': get_value(dom, "anac"),
        'facid': get_value(dom, "facid"),
    }


def create_user(values):
    try:
        user = User.objects.get(username=values['username'])
    except:
        rpwd = ''.join(choice(printable) for _ in xrange(100))
        user = User.objects.create_user(values['username'], values['email'],
                                        rpwd)
        user.last_name = values['last_name']
        user.first_name = values['first_name']
        user.save()

    profile = user.get_profile()
    profile.name = values['first_name'] + " " + values['last_name']
    profile.registration = values['registration']
    profile.email = values['email']
    profile.save()

    try:
        Inscription.objects.create(user=user, year=values['anac'],
                            section=values['facid'] + ':' + values['anet'])
    except:
        pass

    return user


def throw_b64error(request, raw):
    msg = b64encode(raw)
    msg = [ msg[y * 78:(y+1)*78] for y in xrange((len(msg)/78) +1) ]
    return render(request, 'error.html', {'msg': "\n".join(msg)})


def intranet_auth(request, next_url):
    sid, uid = request.GET.get("_sid", False), request.GET.get("_uid", False)
    if len(next_url.strip()) == 0:
        next_url = 'home'
    if sid and uid:
        try:
            print ULB_AUTH % (sid, uid)
            verifier = urlopen(ULB_AUTH % (sid, uid))
            infos = verifier.read()
        except Exception as e:
            return render(request, 'error.html', {'msg': "ulb timeout " + str(e)})

        try:
            values = parse_user(infos)
            user = create_user(values)
        except Exception as e:
            return throw_b64error(request, infos + " -> " + str(e))

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return HttpResponseRedirect(reverse(next_url))
    else:
        return render(request, 'error.html', {'msg': 'url discarded'})
