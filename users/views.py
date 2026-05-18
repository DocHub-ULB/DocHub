import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from requests.exceptions import ConnectionError, SSLError

from users.authBackend import (
    CasInvalidService,
    CasInvalidTicket,
    CasParseError,
    CasRejectError,
    CasRequestError,
    UlbCasBackend,
)
from users.models import CasFailure

logger = logging.getLogger(__name__)


@login_required
def panel_hide(request):
    request.user.welcome = False
    request.user.save()

    return HttpResponseRedirect(reverse("index"))


@login_required
@require_POST
def moderator_banner_hide(request):
    request.user.moderator_welcome_dismissed = True
    request.user.save(update_fields=["moderator_welcome_dismissed"])

    return HttpResponseRedirect(reverse("index"))


def login_view(request):
    next = request.GET.get("next")
    return_url = UlbCasBackend.get_login_url()
    resp = HttpResponseRedirect(return_url)
    if next:
        resp.set_cookie("next_url", next, max_age=10 * 60)  # 10 minutes
    return resp


def auth_ulb(request):
    ticket = request.GET.get("ticket", False)

    if not ticket:
        return TemplateResponse(
            request, "users/auth/no-ticket.html", {"args": request.GET}
        )

    try:
        user = authenticate(ticket=ticket)
    except (CasInvalidService, CasInvalidTicket) as e:
        already_retried = request.COOKIES.get("cas_autoretry") == "1"
        if already_retried:
            # Show an error page to the user
            logger.exception("CAS rejected after recovery attempt")
            _log_cas_failure(request, ticket, e.code, e.debug)
            return TemplateResponse(
                request, "users/auth/error.html", {"code": e.code, "debug": e.debug}
            )
        else:
            # If it's the first try, just redirect the user to the login page
            # so they get an automatic retry.
            # Also set a 60s cookie to avoid a second (or more) retry and an infinite redirect loop
            _log_cas_failure(request, ticket, f"AUTORETRY__{e.code}", e.debug)
            resp = HttpResponseRedirect(reverse("login"))
            resp.set_cookie("cas_autoretry", "1", max_age=60)
            return resp
    except CasRejectError as e:
        logger.exception("CAS rejected")
        _log_cas_failure(request, ticket, e.code, e.debug)
        return TemplateResponse(
            request, "users/auth/error.html", {"code": e.code, "debug": e.debug}
        )
    except CasRequestError as e:
        logger.exception("CAS request error")
        cas_request = e.args[0]
        code = f"REQUEST_{cas_request.status_code}"
        debug = f"{cas_request.url}\n{cas_request.text[:1000]}"
        _log_cas_failure(request, ticket, code, debug)
        return TemplateResponse(
            request, "users/auth/error.html", {"code": code, "debug": debug}
        )
    except CasParseError as e:
        logger.exception("CAS parse error")
        _log_cas_failure(request, ticket, e.code, e.debug)
        return TemplateResponse(
            request, "users/auth/error.html", {"code": e.code, "debug": e.debug}
        )
    except (ConnectionError, SSLError) as e:
        logger.exception("CAS SSL error")
        code = "SSL"
        debug = str(e.args[0])
        _log_cas_failure(request, ticket, code, debug)
        return TemplateResponse(
            request, "users/auth/error.html", {"code": code, "debug": debug}
        )
    except Exception as e:
        logger.exception("CAS unknown error")
        code = "UNKNOWN"
        debug = str(e)
        _log_cas_failure(request, ticket, code, debug)
        return TemplateResponse(
            request, "users/auth/error.html", {"code": code, "debug": debug}
        )

    if user is None:
        _log_cas_failure(request, ticket, "AUTH_RETURNED_NONE", "")
        return TemplateResponse(request, "users/auth/unknown-error.html", {})

    login(request, user)

    next_url = request.COOKIES.get("next_url")

    if next_url and next_url.startswith("/"):
        resp = HttpResponseRedirect(next_url)
        # remove cookie with negative expiration date
        resp.set_cookie("next_url", "", max_age=-100000)
        return resp
    return HttpResponseRedirect("/")


def _log_cas_failure(request, ticket, code, details):
    CasFailure.objects.create(
        code=code,
        details=details,
        ticket=ticket or "",
        ip_address=request.META.get("REMOTE_ADDR"),
    )
