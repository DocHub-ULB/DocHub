from django.conf import settings


def raven(context):
    return {'RAVEN_DSN': getattr(settings, "RAVEN_DSN", None)}
