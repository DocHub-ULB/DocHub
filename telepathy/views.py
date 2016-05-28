# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from actstream import action, actions

from telepathy.forms import NewThreadForm, MessageForm
from telepathy.models import Thread, Message
from catalog.models import Course
from documents.models import Document


@login_required
def new_thread(request, course_slug=None, document_id=None):
    if document_id is not None:
        document = get_object_or_404(Document, id=document_id)
        course = document.course
    else:
        course = get_object_or_404(Course, slug=course_slug)
        document = None

    if request.method == 'POST':
        form = NewThreadForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            content = form.cleaned_data['content']

            thread = Thread.objects.create(user=request.user, name=name, course=course, document=document)
            message = Message.objects.create(user=request.user, thread=thread, text=content)

            placement = {}
            for opt, typecast in Thread.PLACEMENT_OPTS.items():
                if opt in request.POST:
                    placement[opt] = typecast(request.POST[opt])
            if len(placement) > 0:
                thread.placement = json.dumps(placement)
                thread.save()

            actions.follow(request.user, thread, actor_only=False)
            action.send(request.user, verb="a posté", action_object=thread, target=course, markdown=message.text)

            return HttpResponseRedirect(
                reverse('thread_show', args=[thread.id]) + "#message-" + str(message.id)
            )
    else:
        form = NewThreadForm()

    return render(request, 'telepathy/new_thread.html', {
        'form': form,
        'course': course,
    })


def get_thread_context(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    messages = thread.message_set.select_related('user').order_by('created')
    return {
        "thread": thread,
        "messages": messages,
        "form": MessageForm(),
    }


@login_required
def show_thread(request, pk):
    context = get_thread_context(request, pk)
    thread = context['thread']

    # Add page preview if this thread belongs to a document page
    if thread.document:
        page = thread.document.page_set.get(numero=thread.page_no)
        context['thumbnail'] = page.bitmap_120
        context['preview'] = page.bitmap_600

    return render(request, "telepathy/thread.html", context)


@login_required
def show_thread_fragment(request, pk):
    context = get_thread_context(request, pk)
    return render(request, "fragments/thread.html", context)


@login_required
def reply_thread(request, pk):
    form = MessageForm(request.POST)
    thread = get_object_or_404(Thread, pk=pk)
    if form.is_valid():
        content = form.cleaned_data['content']
        poster = request.user
        message = Message.objects.create(user=poster, thread=thread, text=content)

        actions.follow(request.user, thread, actor_only=False)
        action.send(request.user, verb="a répondu", action_object=message, target=thread)

        return HttpResponseRedirect(
            reverse('thread_show', args=[thread.id]) + "#message-" + str(message.id)
        )
    return HttpResponseRedirect(reverse('thread_show', args=[thread.id]) + "#response-form")


@login_required
def edit_message(request, pk):
    message = get_object_or_404(Message, pk=pk)
    thread = message.thread

    if not request.user.write_perm(obj=message):
        return HttpResponse('You may not edit this message.', status=403)

    if request.method == 'POST':
        form = MessageForm(request.POST)

        if form.is_valid():
            message.text = form.cleaned_data['content']
            message.save()

            actions.follow(request.user, thread, actor_only=False)
            action.send(request.user, verb="a édité", action_object=message, target=thread)

            return HttpResponseRedirect(reverse('thread_show', args=[thread.id]) + "#message-" + str(message.id))
    else:
        form = MessageForm({'content': message.text})

    return render(request, 'telepathy/edit_message.html', {
        'form': form,
        'thread': thread,
        'edited_message': message,
        'edit': True,
    })


@login_required
def join_thread(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    actions.follow(request.user, thread, actor_only=False)
    return HttpResponseRedirect(reverse('thread_show', args=[id]))


@login_required
def leave_thread(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    actions.unfollow(request.user, thread)
    return HttpResponseRedirect(reverse('thread_show', args=[id]))
