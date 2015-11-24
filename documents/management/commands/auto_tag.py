# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from django.core.management.base import BaseCommand
from documents.models import Document


class Command(BaseCommand):

    help = 'Auto-tag documents based on their name'

    def handle(self, *args, **options):
        self.stdout.write('Auto-tagging ... ')
        for doc in Document.objects.all():
            doc.tag_from_name()

        self.stdout.write('Done \n')
