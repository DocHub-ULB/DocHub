from django import forms


class SearchForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Chercher un cours (exemple : info-h-100 ou Microéconomie)'
    }))
