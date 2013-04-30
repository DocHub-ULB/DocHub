# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django import forms
from graph.models import Course


class UploadFileForm(forms.Form):
    file = forms.FileField()
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder':'Rename...'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs= {
        'placeholder': 'Description...'
    }))
    course = forms.ModelChoiceField(Course.objects, widget=forms.HiddenInput)
