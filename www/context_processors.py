from django.conf import settings


def read_only(context):
    return {"READ_ONLY": getattr(settings, "READ_ONLY", False)}


def sentry(context):
    return {"SENTRY_DSN": getattr(settings, "SENTRY_DSN", None)}
