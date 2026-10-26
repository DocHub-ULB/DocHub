from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.html import format_html

from documents.bulk import MAX_FILES
from documents.exceptions import ExisingChecksum
from documents.logic import check_document_is_unique
from documents.models import Document, DocumentReport


def duplicate_file_error(exc: ExisingChecksum) -> ValidationError:
    if exc.document is None:
        return ValidationError(str(exc))
    return ValidationError(
        format_html(
            "Ce document est déjà sur DocHub ! Pas besoin de le partager à nouveau. "
            'Tu peux consulter <a href="{}">{}</a>.',
            exc.document.get_absolute_url(),
            exc.document.name,
        )
    )


def validate_uploaded_file(file):
    name = file.name
    if name.lower().endswith(settings.REJECTED_FILE_FORMATS):
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
            "staff_pick": forms.CheckboxInput(),
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
    url = forms.URLField(
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": "https://...",
                "id": "url",
            }
        ),
        error_messages={
            "invalid": "Le lien fourni n'est pas valide. Entre une URL complète (ex: https://...)."
        },
    )


class ReUploadForm(forms.ModelForm):
    file = forms.FileField(validators=[validate_uploaded_file])

    class Meta:
        model = Document
        fields = ()

    def clean_file(self) -> UploadedFile:
        file = self.cleaned_data["file"]
        try:
            self.checksum = check_document_is_unique(file, self.instance.pk)
        except ExisingChecksum as exc:
            raise duplicate_file_error(exc) from exc
        return file


class MultipleUploadFileForm(UploadFileForm):
    pass


class BulkUploadCheckForm(forms.Form):
    """The paths and sizes of the files in the folder, sent as JSON."""

    entries = forms.JSONField(error_messages={"required": "Ce dossier est vide."})

    def clean_entries(self) -> list[tuple[str, int]]:
        files = self.cleaned_data["entries"]
        try:
            entries = [(str(file["path"]), int(file["size"])) for file in files]
        except (TypeError, KeyError, ValueError) as exc:
            raise ValidationError("La liste des fichiers n'est pas valide.") from exc
        if not entries:
            raise ValidationError("Ce dossier est vide.")
        if any(size < 0 for _, size in entries):
            raise ValidationError("La liste des fichiers n'est pas valide.")
        # Some phones open a file picker instead: the files come without folders.
        if not any("/" in path for path, _ in entries):
            raise ValidationError(
                "Ton navigateur n'a pas envoyé de dossier, seulement des fichiers. "
                "Essaie depuis un ordinateur."
            )
        if len(entries) > MAX_FILES:
            raise ValidationError(
                f"Ce dossier contient trop de fichiers ({len(entries)}). "
                f"Envoie-les en plusieurs fois, {MAX_FILES} au maximum à la fois."
            )
        return entries


class BulkUploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_uploaded_file])


class DocumentReportForm(forms.ModelForm):
    class Meta:
        model = DocumentReport
        fields = ("problem_type", "description")
        # problem_type has no widget here: the template renders its choices as
        # radio cards so each one can carry its description.
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }
