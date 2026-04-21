from django import forms
from django.forms import Textarea

from moderation.models import RepresentativeRequest


class RepresentativeRequestForm(forms.ModelForm):
    class Meta:
        fields = ["faculty", "role", "comment"]
        model = RepresentativeRequest

        labels = {
            "faculty": "Quelle est ta faculté ?",
            "role": "Quel est ton rôle ?",
        }

        widgets = {
            "comment": Textarea(attrs={"rows": 3, "placeholder": "Optionnel"}),
        }


class ProcessRepresentativeRequestForm(forms.Form):
    ACTION_CHOICES = [
        ("accept", "Accepter"),
        ("reject", "Refuser"),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    rejection_reason = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        reason = cleaned_data.get("rejection_reason", "").strip()

        # If the action is 'reject', we require a reason of at least 10 characters
        if action == "reject" and len(reason) < 10:
            self.add_error(
                "rejection_reason",
                "Veuillez fournir une raison d'au moins 10 caractères pour justifier le refus.",
            )

        return cleaned_data


class AddModeratorForm(forms.Form):
    netid = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex: blabevue",
                "id": "netid",
            }
        ),
    )
