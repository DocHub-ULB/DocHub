from django.conf import settings


def sentry(context):
    return {
        "SENTRY_DSN": getattr(settings, "SENTRY_DSN", None),
        "SENTRY_RELEASE": getattr(settings, "SENTRY_RELEASE", None),
    }


def version(context):
    return {"GIT_DESCRIBE": getattr(settings, "GIT_DESCRIBE", None)}
