from pathlib import Path

import environ

# First checks if the secrets are not stored in tmpfs by Docker
# https://django-environ.readthedocs.io/en/latest/tips.html#docker-style-file-based-variables
env = environ.FileAwareEnv()

# Set the project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env.bool("DEBUG", default=True)

# Require the secret key if we are not in debug mode
if DEBUG:
    SECRET_KEY = env("SECRET_KEY", default="zisisverysecraite")
else:
    SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost", "*"])
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=True)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "mptt",
    "django.contrib.postgres",
    "www",
    "documents",
    "users",
    "catalog",
    "tags",
    "search",
]

DOCUMENT_STORAGE = "django.core.files.storage.FileSystemStorage"
BASE_URL = env("BASE_URL", default="https://dochub.be/")

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

DATABASES = {
    "default": env.db_url("DB_URL", default=f'sqlite:///{BASE_DIR / "db.sqlite"}')
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

AUTHENTICATION_BACKENDS = [
    "users.authBackend.UlbCasBackend",
    "django.contrib.auth.backends.ModelBackend",
]

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

STATIC_ROOT = env("STATIC_ROOT", default=BASE_DIR / "collected_static")
MEDIA_ROOT = env("MEDIA_ROOT", default=BASE_DIR / "media")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


BROKER_URL = env("REDIS_BROKER", default="redis://localhost:6379/0")

CACHES = {"default": env.cache_url("CACHE_URL", default="dummycache://")}


if DEBUG:
    INSTALLED_APPS.extend(
        [
            "django_extensions",
            # "debug_toolbar",
        ]
    )
    # MIDDLEWARE.extend(["debug_toolbar.middleware.DebugToolbarMiddleware"])
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

    sentry_dsn = env("SENTRY_SDK", default=None)

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
    WHITENOISE_ROOT = BASE_DIR / "static" / "root"

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
    AWS_S3_ENDPOINT_URL = env("STORAGE_ENDPOINT")
    AWS_S3_ACCESS_KEY_ID = env("STORAGE_ACCESS_KEY")
    AWS_S3_SECRET_ACCESS_KEY = env("STORAGE_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = env("STORAGE_MEDIA_BUCKET_NAME")


READ_ONLY = False
REJECTED_FILE_FORMATS = (".zip", ".tar", ".gz", ".rar")


# Add an escape hatch if we really need to customise something
# special at the end in production or elsewhere
# PS: you should try with environment variables first.
try:
    from .local_settings import *
except ImportError:
    pass
