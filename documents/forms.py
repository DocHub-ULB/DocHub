# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()
    description = forms.CharField(widget=forms.Textarea, required=False)
