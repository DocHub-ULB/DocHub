from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from stats.models import DailyStat, Metric


@receiver(user_logged_in)
def _on_login(sender, request, user, **kwargs):
    DailyStat.track(Metric.LOGIN_SUCCESS)
