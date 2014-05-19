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


class MissingBinary(EnvironmentError):
    pass


class DocumentProcessingError(Exception):

    def __init__(self, document, exc=None, message=None):
        super(Exception, self).__init__()
        self.document = document
        self.exc = exc
        self.message = message

    def __repr__(self):
        if not self.message:
            return "DocumentProcessingError on document {0.id}".format(self.document)
        else:
            return "DocumentProcessingError('{0}'') on document {1.id}".format(self.message, self.document)

    __str__ = __repr__


class UploadError(DocumentProcessingError):

    def __repr__(self):
        return "UploadError('Document {0.id} was not properly uploaded by django.')".format(self.document)


class DownloadError(DocumentProcessingError):

    def __repr__(self):
        return "UploadError('Downloading doc {0.id} from {0.source} failed')".format(self.document)
