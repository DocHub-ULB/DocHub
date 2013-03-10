# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django import forms


class NewThreadForm(forms.Form):
    referer_type = forms.CharField(widget=forms.HiddenInput)
    referer_id = forms.DecimalField(widget=forms.HiddenInput)
    subject = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)
