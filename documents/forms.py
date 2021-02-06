from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings

from multiupload.fields import MultiFileField

from tags.models import Tag


def validate_uploaded_file(file):
    name = file.name
    if name.endswith(settings.REJECTED_FILE_FORMATS):
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


class ReUploadForm(forms.Form):
    file = forms.FileField(validators=[validate_uploaded_file])


class MultipleUploadFileForm(forms.Form):
    Mo = 1 << 20
    files = MultiFileField(min_num=1, max_num=25, max_file_size=40 * Mo)
