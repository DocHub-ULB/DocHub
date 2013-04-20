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
from telepathy.forms import NewThreadForm, ReplyForm
from telepathy.models import Thread, Message
from polydag.models import Node
from notify.models import PreNotification

def new_thread(request):
    form = NewThreadForm(request.POST)

    if form.is_valid():
        name = escape(form.cleaned_data['name'])
        content = escape(form.cleaned_data['content'])
        parentNode = get_object_or_404(Node, id=form.cleaned_data['parentNode'])
        thread = Thread.objects.create(user=request.user.get_profile(), name=name)
        message = Message.objects.create(user=request.user.get_profile(),
                                         thread=thread, text=content)
        parentNode.add_child(thread)
        PreNotification.objects.create(
            node=parentNode, text="Nouvelle discussion: "+name[:50]+"..."
        )
        return HttpResponseRedirect(reverse('thread_show', args=[thread.id]))
    return HttpResponse('form invalid', 'text/html')


def show_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    context = {"object": thread,
               "reply_form": ReplyForm(initial={"thread": thread})}
    return render(request, "thread.html", context)


def reply_thread(request):
    form = ReplyForm(request.POST)

    if form.is_valid():
        content = escape(form.cleaned_data['content'])
        thread = form.cleaned_data['thread']
        message = Message.objects.create(user=request.user.get_profile(),
                                         thread=thread, text=content)
        return HttpResponseRedirect(reverse('thread_show', args=[thread.id]))
    return HttpResponse('form invalid', 'text/html')
