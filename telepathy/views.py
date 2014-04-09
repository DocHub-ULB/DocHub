# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.html import escape
from django.contrib.auth.decorators import login_required

from telepathy.forms import NewThreadForm, ReplyForm
from telepathy.models import Thread, Message
from polydag.models import Node


@login_required
def new_thread(request):
    form = NewThreadForm(request.POST)

    if not form.is_valid():
        return HttpResponse('form invalid' + str(form.errors), 'text/html')

    name = escape(form.cleaned_data['name'])
    content = escape(form.cleaned_data['content'])
    parentNode = get_object_or_404(Node, id=form.cleaned_data['parentNode'])
    thread = Thread.objects.create(user=request.user, name=name)
    Message.objects.create(user=request.user, thread=thread, text=content)
    parentNode.add_child(thread)

    return HttpResponseRedirect(reverse('thread_show', args=[thread.id]))


@login_required
def show_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    last_msg = thread.message_set.order_by('-created')[0]
    context = {"object": thread,
               "reply_form": ReplyForm(initial={"thread": thread,
                                                "previous": last_msg})}
    return render(request, "thread.html", context)


@login_required
def reply_thread(request):
    form = ReplyForm(request.POST)

    if form.is_valid():
        content = escape(form.cleaned_data['content'])
        thread = form.cleaned_data['thread']
        previous = form.cleaned_data['previous']
        poster = request.user
        Message.objects.create(user=poster, previous=previous, thread=thread, text=content)

        return HttpResponseRedirect(reverse('thread_show', args=[thread.id]))
    return HttpResponse('form invalid', 'text/html')
