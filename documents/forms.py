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

from django import forms
from graph.models import Course
from django.core.exceptions import ValidationError


def validate_pdf(file):
    # name = file.name
    # if not len(name) > 4 or not name[-4:].lower() == '.pdf':
    #     raise ValidationError('Only .pdf files are supported for the moment')
    pass


class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_pdf])
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Title (optionnel)'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'placeholder': 'Description (optionnel)'
    }))
