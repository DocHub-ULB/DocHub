from django import forms


class NewThreadForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Sujet'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Message'}))


class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Message'}))
