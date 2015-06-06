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
import json

from telepathy.forms import NewThreadForm, MessageForm
from telepathy.models import Thread, Message
from polydag.models import Node
from www.helpers import current_year

@login_required
def new_thread(request, parent_id):
    parentNode = get_object_or_404(Node, id=parent_id)

    if request.method == 'POST':
        form = NewThreadForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            content = form.cleaned_data['content']

            year = "{}-{}".format(current_year(), current_year() + 1)

            thread = Thread.objects.create(user=request.user, name=name, year=year)
            message = Message.objects.create(user=request.user, thread=thread, text=content)
            parentNode.add_child(thread)

            placement = {}
            for opt,typecast in Thread.PLACEMENT_OPTS.iteritems():
                if opt in request.POST:
                    placement[opt] = typecast(request.POST[opt])
            if len(placement) > 0:
                thread.placement = json.dumps(placement)
                thread.save()

            if request.user.auto_follow:
                request.user.follow.add(thread)

            return HttpResponseRedirect(reverse('thread_show', args=[thread.id]) + "#message-" + str(message.id))
    else:
        form = NewThreadForm()

    return render(request, 'new_thread.html', {
        'form': form,
        'parent': parentNode,
    })


def get_thread_context(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    messages = Message.objects.filter(thread__id=thread_id).select_related('user').order_by('created').all()
    return {
        "object": thread,
        "messages": messages,
        "followed": thread.id in request.user.followed_nodes_id(),
        "form": MessageForm(),
        "is_moderator": request.user.is_moderator(thread),
    }

@login_required
def show_thread(request, thread_id):
    context = get_thread_context(request, thread_id)

    # Add page preview if this thread belongs to a document page
    if context['object'].page_no:
        doc = context['object'].parent
        page = doc.page_set.get(numero=context['object'].page_no)
        context['thumbnail'] = page.bitmap_120
        context['preview'] = page.bitmap_600

    return render(request, "thread.html", context)


@login_required
def show_thread_fragment(request, thread_id):
    context = get_thread_context(request, thread_id)
    return render(request, "fragments/thread.html", context)


@login_required
def reply_thread(request, thread_id):
    form = MessageForm(request.POST)
    thread = get_object_or_404(Thread, id=thread_id)
    if form.is_valid():
        content = form.cleaned_data['content']
        poster = request.user
        message = Message.objects.create(user=poster, thread=thread, text=content)
        if request.user.auto_follow:
            request.user.follow.add(thread)

        return HttpResponseRedirect(reverse('thread_show', args=[thread.id]) + "#message-" + str(message.id))
    return HttpResponseRedirect(reverse('thread_show', args=[thread.id]) + "#response-form")


@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    thread = message.thread

    if request.user != message.user and not request.user.is_moderator(thread):
        return HttpResponse('<h1>403</h1>', status=403)

    if request.method == 'POST':
        form = MessageForm(request.POST)

        if form.is_valid():
            message.text = form.cleaned_data['content']
            message.save()
            return HttpResponseRedirect(reverse('thread_show', args=[thread.id]) + "#message-" + str(message.id))
    else:
        form = MessageForm({'content': message.text})

    index = list(thread.message_set.all()).index(message)
    print index

    return render(request, 'edit_message.html', {
        'form': form,
        'object': thread,
        'edited_message': message,
        'edit': True,
    })
