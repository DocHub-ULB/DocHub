# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.utils.html import escape
from telepathy.forms import NewThreadForm, ReplyForm
from telepathy.models import Thread, Message
from graph.models import Course
from documents.models import Document, Page


def get_multi_object(object_type, object_id):
    if object_type == "course":
        return get_object_or_404(Course, id=object_id)
    elif object_type == "document":
        return get_object_or_404(Document, id=object_id)
    elif object_type == "page":
        return get_object_or_404(Page, id=object_id)
    else:
        raise Exception("object_type not found")


def new_thread(request):
    form = NewThreadForm(request.POST)

    if form.is_valid():
        subject = escape(form.cleaned_data['subject'])
        content = escape(form.cleaned_data['content'])
        referer_type = escape(form.cleaned_data['referer_type'])
        referer_id = escape(form.cleaned_data['referer_id'])
        object = get_multi_object(referer_type, referer_id)
        thread = Thread.objects.create(user=request.user.get_profile(),
                                       referer_content=referer_type,
                                       referer_id=referer_id,
                                       subject=subject)
        message = Message.objects.create(user=request.user.get_profile(),
                                         thread=thread, text=content)
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
