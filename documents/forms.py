from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from documents.models import Document
from tags.models import Tag


def validate_uploaded_file(file):
    name = file.name
    if name.endswith(settings.REJECTED_FILE_FORMATS):
        raise ValidationError(
            "Les documents compressés ne sont pas supportés pour le moment."
        )


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ("name", "description", "tags", "certified")
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Titre (optionnel)"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-input", "placeholder": "Description (optionnel)"}
            ),
            "tags": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                    "data-placeholder": "Ajoute des tags",
                    "data-controller": "tom-select",
                }
            ),
        }


class UploadFileForm(DocumentForm):
    file = forms.FileField(
        validators=[validate_uploaded_file],
        widget=forms.FileInput(
            attrs={
                "class": "file-upload",
            }
        ),
    )


class BulkFilesForm(FileForm):
    url = forms.URLField()


class ReUploadForm(forms.Form):
    file = forms.FileField(validators=[validate_uploaded_file])


class MultipleUploadFileForm(UploadFileForm):
    pass
