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

from django.core.management.base import BaseCommand

from users.models import User
from telepathy.models import Thread, Message
from documents.models import Document, Page
from notify.models import PreNotification, Notification


class Command(BaseCommand):

    help = 'Numbers on b402'

    def handle(self, *args, **options):
        Print = self.stdout.write

        Print("User summary :\n")
        Print("{} users\n".format(User.objects.count()))
        Print("\n")

        Print("Document summary :\n")
        Print("{} documents\n".format(Document.objects.count()))
        Print(" - {} IN_QUEUE\n".format(Document.objects.filter(state="IN_QUEUE").count()))
        Print(" - {} PROCESSING\n".format(Document.objects.filter(state="PROCESSING").count()))
        Print(" - {} PREPARING\n".format(Document.objects.filter(state="PREPARING").count()))
        Print(" - {} READY_TO_QUEUE\n".format(Document.objects.filter(state="READY_TO_QUEUE").count()))
        Print(" - {} ERROR\n".format(Document.objects.filter(state="ERROR").count()))
        Print(" - {} DONE\n".format(Document.objects.filter(state="DONE").count()))
        Print("{} views\n".format(sum(map(lambda x: x.views, Document.objects.all()))))
        Print("{} downloads\n".format(sum(map(lambda x: x.downloads, Document.objects.all()))))
        Print("{} pages\n".format(Page.objects.count()))
        Print("{} future pages ({} doc not counted)\n".format(
            sum(map(lambda x: x.pages, Document.objects.all())) - Page.objects.count(),
            Document.objects.filter(pages=0).count()
        ))
        Print("\n")

        Print("Thread summary :\n")
        Print("{} threads\n".format(Thread.objects.count()))
        Print("{} messages\n".format(Message.objects.count()))
        Print("\n")

        Print("Events summary :\n")
        Print("{} events\n".format(PreNotification.objects.count()))
        Print("{} fired notifications\n".format(Notification.objects.count()))
        ratio = round(float(Notification.objects.count()) / PreNotification.objects.count(), 2)
        Print("{} ratio fired/event\n".format(ratio))
        Print("\n")

        Print("Following summary :\n")
        course_followed_by_user = map(lambda x: len(x.followed_courses()), User.objects.all())
        course_folowed = sum(course_followed_by_user) / float(len(course_followed_by_user))
        node_folowed_by_user = map(lambda x: len(x.followed_nodes_id()), User.objects.all())
        node_folowed = sum(node_folowed_by_user) / float(len(node_folowed_by_user))
        Print("{} mean followed courses ({} max)\n".format(round(course_folowed, 2), max(course_followed_by_user)))
        Print("{} mean followed (other)\n".format(node_folowed - course_folowed))
        Print("\n")

        Print("Notifications summary:\n")
        read = Notification.objects.filter(read=True).count()
        unread = Notification.objects.filter(read=False).count()
        Print("Read : {}, unread: {}".format(read, unread))
        user_count = User.objects.count()
        Print("Read (per user) : {}, unread (per user): {}".format(read / float(user_count), unread / float(user_count)))
