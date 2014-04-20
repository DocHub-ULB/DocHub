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

from datetime import datetime

from django import forms
from graph.models import Course
from django.core.exceptions import ValidationError
from polydag.models import Keyword
from www.helpers import year_choices


def validate_pdf(file):
    # name = file.name
    # if not len(name) > 4 or not name[-4:].lower() == '.pdf':
    #     raise ValidationError('Only .pdf files are supported for the moment')
    pass


def tag_choices():
    return map(lambda x: (x.pk, x.name), Keyword.objects.exclude(name__in=map(lambda x: x[0], year_choices())))


class FileForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Titre (optionnel)'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'placeholder': 'Description (optionnel)'
    }))

    year = forms.ChoiceField(choices=year_choices())

    tags = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Keyword.objects.exclude(name__startswith="20"),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'chosen-select',
                'data-placeholder': 'Tags (optionnel)',
                'style': "width: 100%; margin-bottom: 15px;"
            }
        )
    )


class UploadFileForm(FileForm):
    file = forms.FileField(validators=[validate_pdf])

# TODO
# class UrlFileForm(FileForm):
