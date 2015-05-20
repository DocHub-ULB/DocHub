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
from django.db.models import Sum

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
        Print("{} views\n".format(Document.objects.aggregate(Sum('views'))['views__sum']))
        Print("{} downloads\n".format(Document.objects.aggregate(Sum('downloads'))['downloads__sum']))
        Print("{} pages\n".format(Page.objects.count()))
        Print("{} future pages ({} doc not counted)\n".format(
            (
                Document.objects.aggregate(Sum('pages'))['pages__sum']
                - Page.objects.count()
            ),
            Document.objects.exclude(state="ERROR").filter(pages=0).count()
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
        course_followed_by_user = list(map(lambda x: len(x.followed_courses()), User.objects.all()))
        course_folowed = sum(course_followed_by_user) / float(len(course_followed_by_user))
        Print("{} followed courses/user\n".format(round(course_folowed, 2)))
        Print("\n")

        Print("Notifications summary:\n")
        read = Notification.objects.filter(read=True).count()
        unread = Notification.objects.filter(read=False).count()
        Print("Read : {}, unread: {}".format(read, unread))
        user_count = User.objects.count()
        read_u = round(read / float(user_count), 1)
        unread_u = round(unread / float(user_count), 1)
        Print("Read (per user) : {}, unread (per user): {}".format(read_u, unread_u))
