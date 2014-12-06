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
