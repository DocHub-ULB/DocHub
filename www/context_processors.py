from django.conf import settings


def version(context):
    return {"GIT_DESCRIBE": getattr(settings, "GIT_DESCRIBE", None)}
