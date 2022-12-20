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
