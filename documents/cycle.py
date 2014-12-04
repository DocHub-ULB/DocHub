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

from tasks import process_document


def add_document_to_queue(document):
    document.state = "IN_QUEUE"
    document.save()
    try:
        process_document.delay(document.id)
    except Exception as e:
        document.state = "READY_TO_QUEUE"
        document.save()
        raise e
