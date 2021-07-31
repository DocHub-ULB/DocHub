from django.conf import settings


def read_only(context):
    return {"READ_ONLY": getattr(settings, "READ_ONLY", False)}
