import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from requests.exceptions import ConnectionError, SSLError

from users.authBackend import (
    CasParseError,
    CasRejectError,
    CasRequestError,
    UlbCasBackend,
)

logger = logging.getLogger(__name__)


@login_required
def panel_hide(request):
    request.user.welcome = False
    request.user.save()

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
    except CasRejectError as e:
        logger.exception("CAS rejected")
        return TemplateResponse(
            request, "users/auth/error.html", {"code": e.args[0], "debug": e.args[1]}
        )
    except CasRequestError as e:
        logger.exception("CAS request error")
        cas_request = e.args[0]
        return TemplateResponse(
            request,
            "users/auth/error.html",
            {
                "code": f"REQUEST_{cas_request.status_code}",
                "debug": f"{cas_request.url}\n{cas_request.text[:1000]}",
            },
        )
    except CasParseError as e:
        logger.exception("CAS parse error")
        return TemplateResponse(
            request, "users/auth/error.html", {"code": e.args[0], "debug": e.args[1]}
        )
    except (ConnectionError, SSLError) as e:
        logger.exception("CAS SSL error")
        return TemplateResponse(
            request, "users/auth/error.html", {"code": "SSL", "debug": e.args[0]}
        )
    except Exception as e:
        logger.exception("CAS unknown error")
        return TemplateResponse(
            request, "users/auth/error.html", {"code": "UNKNOWN", "debug": e.args[0]}
        )

    if user is None:
        return TemplateResponse(request, "users/auth/unknown-error.html", {})

    login(request, user)

    next_url = request.COOKIES.get("next_url")

    if next_url and next_url.startswith("/"):
        resp = HttpResponseRedirect(next_url)
        # remove cookie with negative expiration date
        resp.set_cookie("next_url", "", max_age=-100000)
        return resp
    return HttpResponseRedirect("/")
