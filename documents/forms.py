# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django import forms
from graph.models import Course
from django.core.exceptions import ValidationError

def validate_pdf(file):
    name = file.name
    if not len(name) > 4 or not name[-4:].lower() == '.pdf':
        raise ValidationError('Only .pdf files are supported for the moment')

class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_pdf])
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder':'Rename...'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs= {
        'placeholder': 'Description...'
    }))
    course = forms.ModelChoiceField(Course.objects, widget=forms.HiddenInput)
