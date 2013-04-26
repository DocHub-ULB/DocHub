# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django import forms
from telepathy.models import Thread, Message


class NewThreadForm(forms.Form):
    parentNode = forms.CharField(widget=forms.HiddenInput)
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'title'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'content'}))


class ReplyForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'content'}))
    previous = forms.ModelChoiceField(Message.objects, widget=forms.HiddenInput)
    thread = forms.ModelChoiceField(Thread.objects, widget=forms.HiddenInput)
