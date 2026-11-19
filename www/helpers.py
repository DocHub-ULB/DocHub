# TODO: is this dead code ?
from django.http import JsonResponse
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
    choices = [(f"{year - i}-{year - i + 1}",) * 2 for i in range(backlog)]
    choices.append(("Archives",) * 2)
    return choices


def wants_json(request) -> bool:
    """API clients add ?format=json to a page to get its data as JSON."""
    return request.GET.get("format") == "json"


def login_required_json() -> JsonResponse:
    """Anonymous visitors only see what the public pages show, so no JSON."""
    return JsonResponse(
        {"error": "Connecte-toi ou utilise un token, voir /llms.txt"}, status=401
    )
