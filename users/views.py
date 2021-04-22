import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from actstream.models import actor_stream
from PIL import Image, ImageOps
from rest_framework.authtoken.models import Token

from users.authBackend import NetidBackend
from users.forms import SettingsForm


@login_required
def user_settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)

        if form.is_valid():
            im = Image.open(request.FILES['profile_pic'])
            im = ImageOps.fit(im, (120, 120), Image.ANTIALIAS)

            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "profile")):
                os.makedirs(os.path.join(settings.MEDIA_ROOT, "profile"))

            im.save(os.path.join(settings.MEDIA_ROOT, f"profile/{request.user.netid}.png"))
            request.user.photo = "png"
            request.user.save()

            messages.success(request, 'Ton profil a été mis à jour.')

            return render(request, "users/settings.html", {'form': SettingsForm()})
    else:
        form = SettingsForm()

    token, created = Token.objects.get_or_create(user=request.user)

    return render(request, 'users/settings.html', {
        'form': form,
        'stream': actor_stream(request.user)[:5],
        'token': token,
    })


@login_required
def reset_token(request):
    Token.objects.filter(user=request.user).delete()
    Token.objects.create(user=request.user)
    messages.success(request, "La clé d'API a été regénérée")

    return HttpResponseRedirect(reverse('settings'))


@login_required
def panel_hide(request):
    request.user.welcome = False
    request.user.save()

    return HttpResponseRedirect(reverse('index'))


def login_view(request):
    next = request.GET.get('next')
    return_url = NetidBackend.login_url().url
    resp = HttpResponseRedirect(return_url)
    if next:
        resp.set_cookie('next_url', next, max_age=10 * 60) # 10 minutes
    return resp


def auth_ulb(request):
    ticket = request.GET.get("ticket", False)

    if ticket:
        user = authenticate(ticket=ticket)
        if user is not None:
            login(request, user)
            next_url = request.COOKIES.get("next_url")
            if next_url and next_url.startswith("/"):
                resp = HttpResponseRedirect(next_url)
                resp.set_cookie('next_url', "", max_age=-100000)
                return resp
            return HttpResponseRedirect("/")

    return HttpResponseForbidden("Error while authenticating with NetID")
