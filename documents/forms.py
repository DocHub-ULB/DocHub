# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError

from multiupload.fields import MultiFileField

from tags.models import Tag


def validate_uploaded_file(file):
    name = file.name
    if name.endswith((".zip", ".tar", ".gz", ".rar")):
        raise ValidationError('Les fichiers compressés ne sont pas supportés pour le moment.')


class FileForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Titre (optionnel)'
    }))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'placeholder': 'Description (optionnel)'
    }))

    tags = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'chosen-select',
                'data-placeholder': 'Tags (optionnel)',
            }
        )
    )


class UploadFileForm(FileForm):
    file = forms.FileField(validators=[validate_uploaded_file])


class MultipleUploadFileForm(forms.Form):
    Mo = 1 << 20
    files = MultiFileField(min_num=1, max_num=25, max_file_size=25 * Mo)
