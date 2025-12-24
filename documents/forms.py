from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from documents.models import Document, DocumentReport


def validate_uploaded_file(file):
    name = file.name
    if name.endswith(settings.REJECTED_FILE_FORMATS):
        raise ValidationError(
            "Les documents compressés ne sont pas supportés pour le moment."
        )


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ("name", "description", "tags", "staff_pick")
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
            "staff_pick": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "placeholder": "Description (optionnel)",
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


class BulkFilesForm(forms.Form):
    url = forms.URLField()


class ReUploadForm(forms.Form):
    file = forms.FileField(validators=[validate_uploaded_file])


class MultipleUploadFileForm(UploadFileForm):
    pass


class DocumentReportForm(forms.ModelForm):
    class Meta:
        model = DocumentReport
        fields = ("problem_type", "description")
        widgets = {
            "problem_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Description (optionnel)",
                    "rows": 4,
                }
            ),
        }
