from django import forms


class SettingsForm(forms.Form):
    profile_pic = forms.ImageField()
