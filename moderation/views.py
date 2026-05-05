from collections import defaultdict
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from moderation.forms import (
    AddModeratorForm,
    ProcessRepresentativeRequestForm,
    RepresentativeRequestForm,
)
from moderation.models import ModerationLog, RepresentativeRequest

User = get_user_model()


# --- Custom Decorators for 403 Permissions ---


def is_moderator(user):
    return user.is_staff or user.is_moderator


def moderator_required(view_func):
    """Decorator for views that checks that the user is a moderator, raising a 403 if not."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if is_moderator(request.user):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied(
            "Tu n'as pas les droits de modération pour accéder à cette page."
        )

    return _wrapped_view


def admin_required(view_func):
    """Decorator for views that checks that the user is staff, raising a 403 if not."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied(
            "Seul un administrateur système peut effectuer cette action."
        )

    return _wrapped_view


# ---------------------------------------------


@login_required
@moderator_required
def moderation_home(request):
    """Main dashboard for moderators."""
    return render(request, "moderation/home.html")


@login_required
@moderator_required
@require_POST
def process_representative_request(request, request_id):
    """Processes a role request (Accept or Reject) and logs the action."""
    rep_request = get_object_or_404(
        RepresentativeRequest, id=request_id, processed=False
    )
    target_user = rep_request.user

    form = ProcessRepresentativeRequestForm(request.POST)

    if not form.is_valid():
        url = reverse("manage_moderators") + "?error=reason"
        return redirect(url)

    action = form.cleaned_data["action"]

    if action == "accept":
        if not target_user.is_staff and not target_user.is_moderator:
            target_user.is_moderator = True
            target_user.promoted_by = request.user
            target_user.save(update_fields=["is_moderator", "promoted_by"])

            ModerationLog.track(
                user=request.user,
                content_object=rep_request,
                values={"action_accepter": ("", "Acceptée")},
            )

            messages.success(
                request,
                f"La demande a été acceptée. {target_user.netid} est maintenant modérateur·trice !",
            )
        else:
            messages.info(
                request,
                f"{target_user.netid} avait déjà des droits. Demande archivée.",
            )

    elif action == "reject":
        reason = form.cleaned_data["rejection_reason"]
        rep_request.rejection_reason = reason

        ModerationLog.track(
            user=request.user,
            content_object=rep_request,
            values={"action_rejeter": ("", reason if reason else "Sans motif")},
        )

        messages.warning(
            request,
            f"La demande de {target_user.netid} a été refusée.",
        )

    # Mark as processed with update_fields for performance
    rep_request.processed = True
    rep_request.save(update_fields=["processed", "rejection_reason"])

    return redirect("manage_moderators")


@login_required
@moderator_required
def manage_moderators(request):
    """Display moderator requests and direct promotion controls."""
    pending_requests = (
        RepresentativeRequest.objects.filter(processed=False)
        .select_related("user")
        .order_by("-created")
    )
    return render(
        request,
        "moderation/moderators_management.html",
        {"pending_requests": pending_requests},
    )


@login_required
@moderator_required
@require_POST
def moderator_add(request):
    """Add a new moderator using a validated Form."""
    form = AddModeratorForm(request.POST)

    if form.is_valid():
        netid_to_add = form.cleaned_data["netid"]

        try:
            target_user = User.objects.get(netid=netid_to_add)

            if not target_user.is_staff and not target_user.is_moderator:
                target_user.is_moderator = True
                target_user.promoted_by = request.user
                target_user.save(update_fields=["is_moderator", "promoted_by"])

                # FIX : Close any pending request for this user automatically
                RepresentativeRequest.objects.filter(
                    user=target_user, processed=False
                ).update(processed=True, rejection_reason="")

                ModerationLog.track(
                    user=request.user,
                    content_object=target_user,
                    values={"is_moderator": (False, True)},
                )
                messages.success(
                    request, f"{target_user.netid} est maintenant modérateur·trice !"
                )
            else:
                messages.info(request, "Cet utilisateur a déjà des droits.")
        except User.DoesNotExist:
            url = (
                reverse("manage_moderators") + f"?error=not_found&netid={netid_to_add}"
            )
            return redirect(url)

    return redirect("manage_moderators")


@login_required
@admin_required
@require_POST
def moderator_remove(request, user_id):
    """Remove moderator rights from a user (Admin only)."""
    target_user = get_object_or_404(User, id=user_id)

    if target_user.is_staff:
        messages.warning(
            request, "Impossible de retirer les droits d'un Administrateur Système ici."
        )
    elif target_user == request.user:
        messages.warning(request, "Tu ne peux pas retirer tes propres droits ici.")
    elif target_user.is_moderator:
        target_user.is_moderator = False
        target_user.promoted_by = None
        target_user.save(update_fields=["is_moderator", "promoted_by"])

        ModerationLog.track(
            user=request.user,
            content_object=target_user,
            values={"is_moderator": (True, False)},
        )
        messages.warning(request, f"Les droits de {target_user.netid} ont été retirés.")

    return redirect("manage_moderators")


@login_required
def representative_request(request):
    """Handle student requests to become a moderator."""
    if is_moderator(request.user):
        raise PermissionDenied(
            "Tu es déjà modérateur (ou admin), tu n'as pas besoin de faire de demande."
        )

    if RepresentativeRequest.objects.filter(
        user=request.user, processed=False
    ).exists():
        return render(
            request,
            "moderation/representative_request_received.html",
        )

    rejection_msg = None
    last_req = (
        RepresentativeRequest.objects.filter(user=request.user, processed=True)
        .order_by("-created")
        .first()
    )
    if last_req and last_req.rejection_reason:
        rejection_msg = last_req.rejection_reason

    if request.method == "POST":
        form = RepresentativeRequestForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.user = request.user
            form.instance.save()
            return redirect("representative_request")
    else:
        form = RepresentativeRequestForm()

    return render(
        request,
        "moderation/representative_request.html",
        {"form": form, "rejection_reason": rejection_msg},
    )


@login_required
def public_logs(request):
    """Public ledger of moderation actions for accountability (accessible to all logged users)."""

    # Fetch all relevant moderation logs
    log_list = (
        ModerationLog.objects.select_related("user", "content_type")
        .prefetch_related("content_object")
        .order_by("-timestamp")
    )

    # Set up pagination (e.g., 50 logs per page)
    paginator = Paginator(log_list, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "moderation/public_logs.html",
        {"logs": page_obj},
    )


@login_required
def moderation_tree(request):
    """Public page showing who promoted whom as moderator."""
    moderators = (
        User.objects.filter(Q(is_staff=True) | Q(is_moderator=True))
        .select_related("promoted_by")
        .annotate(
            action_count=Count("moderationlog", distinct=True),
            document_count=Count("document", distinct=True),
        )
        .order_by("first_name")
    )

    all_ids = {u.id for u in moderators}
    children = defaultdict(list)
    roots = []

    for u in moderators:
        if u.promoted_by_id and u.promoted_by_id in all_ids:
            children[u.promoted_by_id].append(u)
        else:
            roots.append(u)

    def build_subtree(user):
        return [{"user": c, "children": build_subtree(c)} for c in children[user.id]]

    tree = [{"user": r, "children": build_subtree(r)} for r in roots]

    return render(request, "moderation/tree.html", {"tree": tree})


@login_required
def moderation_profile(request, netid):
    """Public profile page showing a moderator's actions."""
    profile_user = get_object_or_404(User, netid=netid)
    has_moderation_history = ModerationLog.objects.filter(user=profile_user).exists()
    if not (
        profile_user.is_staff or profile_user.is_moderator or has_moderation_history
    ):
        raise PermissionDenied("Ce profil n'a pas d'activité de modération publique.")

    logs = (
        ModerationLog.objects.filter(user=profile_user)
        .select_related("content_type")
        .prefetch_related("content_object")
        .order_by("-timestamp")
    )
    return render(
        request,
        "moderation/profile.html",
        {"profile_user": profile_user, "logs": logs},
    )


@login_required
def moderation_about(request):
    """Public page explaining the moderation system."""
    return render(request, "moderation/about.html")
