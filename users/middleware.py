from django.conf import settings
from django.core.cache import cache
from django.db.models import F
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from users.models import AccessToken
from www.helpers import wants_json


def allow_token_writes(view):
    """Lets API clients send POST requests to this view with their token."""
    view.allow_token_writes = True
    return view


class AccessTokenMiddleware:
    """Logs in the user of an `Authorization: Bearer dh_...` header.

    Browsers never send this header on their own, so CSRF does not apply. To
    keep API clients from doing anything by mistake, they can only read, except
    on the views marked with `allow_token_writes`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request) -> HttpResponse:
        request.access_token = None
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return self.get_response(request)

        key = header.removeprefix("Bearer ").strip()
        if not AccessToken.is_well_formed(key):
            # Most likely cut or mistyped when it was copied: say so
            return JsonResponse(
                {
                    "error": "Ce token est mal formé : il est sans doute incomplet "
                    "ou mal copié. Vérifie qu'il commence par "
                    f"{AccessToken.PREFIX} et qu'il est copié en entier."
                },
                status=401,
            )

        token = (
            AccessToken.objects.select_related("user")
            .filter(key_hash=AccessToken.hash_key(key))
            .first()
        )
        if token is None:
            return JsonResponse(
                {"error": "Ce token n'existe pas ou a été supprimé."}, status=401
            )

        AccessToken.objects.filter(pk=token.pk).update(
            last_used=timezone.now(), request_count=F("request_count") + 1
        )
        request.access_token = token
        request.user = token.user
        request._dont_enforce_csrf_checks = True
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if (
            request.access_token
            and request.method not in ("GET", "HEAD", "OPTIONS")
            and not getattr(view_func, "allow_token_writes", False)
        ):
            return JsonResponse(
                {"error": "Ton token peut seulement lire, et envoyer des documents."},
                status=403,
            )
        return None


class RateLimitMiddleware:
    """Allows RATE_LIMIT_PER_MINUTE requests per minute to each user (or IP)."""

    SKIPPED_PREFIXES = (settings.STATIC_URL, settings.MEDIA_URL)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request) -> HttpResponse:
        if request.path.startswith(self.SKIPPED_PREFIXES):
            return self.get_response(request)

        minute = timezone.now().strftime("%Y%m%d%H%M")
        key = f"ratelimit:{client_id(request)}:{minute}"
        cache.add(key, 0, timeout=60)
        try:
            count = cache.incr(key)
        except ValueError:  # The dummy cache does not keep anything
            count = 0

        if count > settings.RATE_LIMIT_PER_MINUTE:
            response = too_many_requests(
                request,
                "Tu vas un peu trop vite ! Attends une minute avant de continuer.",
            )
            response["Retry-After"] = "60"
            return response

        return self.get_response(request)


def client_id(request: HttpRequest) -> str:
    if request.user.is_authenticated:
        return f"user:{request.user.pk}"
    # We run behind one reverse proxy (Caddy): it adds the real IP of the
    # visitor at the end of X-Forwarded-For. Earlier values can be forged.
    forwarded = request.headers.get("X-Forwarded-For", "")
    ip = forwarded.split(",")[-1].strip() or request.META.get("REMOTE_ADDR", "")
    return f"ip:{ip}"


def too_many_requests(request, message: str) -> HttpResponse:
    if wants_json(request):
        return JsonResponse({"error": message}, status=429)
    return render(request, "error/429.html", {"message": message}, status=429)
