# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.html import escape
from django.contrib.auth.decorators import login_required

from telepathy.forms import NewThreadForm, ReplyForm
from telepathy.models import Thread, Message
from polydag.models import Node


@login_required
def new_thread(request, parent_id):
    parentNode = get_object_or_404(Node, id=parent_id)

    if request.method == 'POST':
        form = NewThreadForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            content = form.cleaned_data['content']

            thread = Thread.objects.create(user=request.user, name=name)
            Message.objects.create(user=request.user, thread=thread, text=content)
            parentNode.add_child(thread)

            return HttpResponseRedirect(reverse('thread_show', args=[thread.id]))
    else:
        form = NewThreadForm()

    return render(request, 'new_thread.html', {
        'form': form,
        'parent': parentNode,
    })


@login_required
def show_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    last_msg = thread.message_set.order_by('-created')[0]
    context = {"object": thread,
                "followed": thread.id in request.user.followed_nodes_id(),
               "form": ReplyForm(initial={"thread": thread,
                                                "previous": last_msg})}
    return render(request, "thread.html", context)


@login_required
def reply_thread(request):
    form = ReplyForm(request.POST)

    if form.is_valid():
        content = form.cleaned_data['content']
        thread = form.cleaned_data['thread']
        previous = form.cleaned_data['previous']
        poster = request.user
        Message.objects.create(user=poster, previous=previous, thread=thread, text=content)

        return HttpResponseRedirect(reverse('thread_show', args=[thread.id]))
    return HttpResponse('form invalid', 'text/html')
