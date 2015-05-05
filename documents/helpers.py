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

import importlib
from www.settings import DOCUMENT_STORAGE


def r(self):
    return 60 * (1 + self.request.retries * 2)


def get_document_storage():
    module_name = '.'.join(DOCUMENT_STORAGE.split('.')[:-1])
    module = importlib.import_module(module_name)

    name = DOCUMENT_STORAGE.split('.')[-1]
    try:
        storage = module.__getattribute__(name)
    except AttributeError:
        raise ImportError("{} does not exist in module {}".format(name, module_name))

    return storage()
