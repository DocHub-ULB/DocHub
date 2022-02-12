from django import forms

from catalog.models import Course
from users.models import User


class SettingsForm(forms.Form):
    profile_pic = forms.ImageField()


class UserModeratedCourseForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    courses = forms.ModelMultipleChoiceField(queryset=Course.objects.all())
