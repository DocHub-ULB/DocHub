from django.conf import settings


def raven(context):
    return {'RAVEN_DSN': getattr(settings, "RAVEN_DSN", None)}


def read_only(context):
    return {'READ_ONLY': getattr(settings, "READ_ONLY", False)}
