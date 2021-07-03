# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

import re
from os.path import dirname, join, normpath

BASE_DIR = dirname(dirname(dirname(__file__)))

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
)

STATICFILES_DIRS = (join(BASE_DIR, "static"),)

INTERNAL_IPS = ["127.0.0.1", "localhost", "0.0.0.0"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "www.urls"
LANGUAGE_CODE = "fr-be"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

IGNORABLE_404_URLS = (
    re.compile(r"\.(php|cgi)$"),
    re.compile(r"^/phpmyadmin/"),
    re.compile(r"^/apple-touch-icon.*\.png$"),
    re.compile(r"^/favicon\.ico$"),
    re.compile(r"^/robots\.txt$"),
)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = ""
MEDIA_ROOT = join(BASE_DIR, "media")

# SECRET_KEY configuration
SECRET_FILE = normpath(join(BASE_DIR, "www", "secret_key.txt"))

try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except OSError:
    try:
        with open(SECRET_FILE, "w") as f:
            import random

            SECRET_KEY = "".join(
                [
                    random.SystemRandom().choice(
                        "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
                    )
                    for i in range(50)
                ]
            )
            f.write(SECRET_KEY)
    except OSError:
        raise Exception(
            "Cannot open file `%s` for writing the secret_key" % SECRET_FILE
        )
