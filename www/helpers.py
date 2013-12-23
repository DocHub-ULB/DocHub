from datetime import datetime


def current_year():
    now = datetime.today()
    if datetime(now.year, 1, 1) < now < datetime(now.year, 9, 14):
        return now.year - 1
    else:
        return now.year
