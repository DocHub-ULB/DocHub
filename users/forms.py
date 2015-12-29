# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms


class SettingsForm(forms.Form):
    profile_pic = forms.ImageField()
