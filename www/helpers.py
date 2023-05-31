# TODO: is this dead code ?
from django.utils import timezone


def current_year():
    now = timezone.now().date()
    if now.month < 9:
        return now.year - 1
    elif now.month == 9:
        return now.year - 1 if now.day < 15 else now.year
    else:
        return now.year


def year_choices(backlog=5):
    year = current_year()
    choices = [("%d-%d" % (year - i, year - i + 1),) * 2 for i in range(backlog)]
    choices.append(("Archives",) * 2)
    return choices
