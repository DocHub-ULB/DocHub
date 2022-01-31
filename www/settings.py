from pathlib import Path

from www.utils import get_env

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = get_env("DEBUG", "1") == "1"

SECRET_KEY = get_env("SECRET_KEY", "zisisverysecraite", required=not DEBUG)
ALLOWED_HOSTS = get_env(
    "ALLOWED_HOSTS", "127.0.0.1,localhost", required=not DEBUG
).split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rest_framework",
    "mptt",
    "rest_framework.authtoken",
    "django.contrib.postgres",
    "sass_processor",
    "www",
    "documents",
    "users",
    "catalog",
    "tags",
    "search",
]

DOCUMENT_STORAGE = "django.core.files.storage.FileSystemStorage"
BASE_URL = "https://dochub.be/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "www.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
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


if get_env("USE_POSTGRES", "0") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": get_env("SQL_DATABASE", "dochub"),
            "HOST": get_env("SQL_HOST"),
            "USER": get_env("SQL_USER"),
            "PASSWORD": get_env("SQL_PASSWORD"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": get_env("SQL_DATABASE", str(BASE_DIR / "db.sqlite")),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"


WSGI_APPLICATION = "www.wsgi.application"
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "index"
LOGIN_URL = "/login"
SITE_ID = 1

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "fr-be"
TIME_ZONE = "Europe/Brussels"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = get_env("STATIC_ROOT", str(BASE_DIR / "collected_static"))
MEDIA_ROOT = get_env("MEDIA_ROOT", str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


BROKER_URL = get_env("REDIS_BROKER", "redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": get_env(
            "CACHE_BACKEND", "django.core.cache.backends.dummy.DummyCache"
        ),
        "LOCATION": get_env("CACHE_LOCATION", "127.0.0.1:11211"),
        "TIMEOUT": int(get_env("CACHE_TIMEOUT", "300")),
    }
}


if DEBUG:
    INSTALLED_APPS.extend(
        [
            "django_extensions",
            "debug_toolbar",
        ]
    )
    MIDDLEWARE.extend(["debug_toolbar.middleware.DebugToolbarMiddleware"])
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
        "0.0.0.0",
    ]
else:
    INSTALLED_APPS.extend(
        [
            "gunicorn",
        ]
    )

    sentry_dsn = get_env("SENTRY_SDK")

    if sentry_dsn is not None:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[DjangoIntegration()],
            traces_sample_rate=1.0,
            send_default_pii=True,
        )

    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
    AWS_S3_ENDPOINT_URL = get_env("STORAGE_ENDPOINT")
    AWS_S3_ACCESS_KEY_ID = get_env("STORAGE_ACCESS_KEY")
    AWS_S3_SECRET_ACCESS_KEY = get_env("STORAGE_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = get_env("STORAGE_MEDIA_BUCKET_NAME")


READ_ONLY = False
REJECTED_FILE_FORMATS = (".zip", ".tar", ".gz", ".rar")
