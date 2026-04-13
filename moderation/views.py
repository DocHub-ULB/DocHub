from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from moderation.forms import ProcessRepresentativeRequestForm, RepresentativeRequestForm
from moderation.models import ModerationLog, RepresentativeRequest

User = get_user_model()


def is_moderator(user):
    # Grant access to Admins (is_staff) AND Moderators (is_moderator)
    return user.is_staff or user.is_moderator


@login_required
@user_passes_test(is_moderator, login_url="/")
def moderation_home(request):
    # Fetch all pending requests, from newest to oldest
    pending_requests = (
        RepresentativeRequest.objects.filter(processed=False)
        .select_related("user")
        .order_by("-created")
    )

    return render(
        request,
        "moderation/home.html",
        {"pending_requests": pending_requests},
    )


@login_required
@user_passes_test(is_moderator, login_url="/")
@require_POST
def process_representative_request(request, request_id):
    """Processes a role request (Accept or Reject) and logs the action"""
    rep_request = get_object_or_404(RepresentativeRequest, id=request_id)
    target_user = rep_request.user

    # Pass POST data to the Django form
    form = ProcessRepresentativeRequestForm(request.POST)

    if not form.is_valid():
        # If the form is invalid (e.g., rejection reason is too short)
        url = reverse("moderation_home") + "?error=reason"
        return redirect(url)

    action = form.cleaned_data["action"]

    # Dictionary of changes for the logging system
    log_values = {"processed": (False, True)}

    if action == "accept":
        # Check if the user already has rights (in case another mod already processed it)
        if not target_user.is_staff and not target_user.is_moderator:
            target_user.is_moderator = True
            target_user.save()

            # Create the moderation log
            ModerationLog.track(
                user=request.user,
                content_object=target_user,
                values={"is_moderator": (False, True)},
            )
            messages.success(
                request,
                f"La demande a été acceptée. {target_user.netid} est maintenant modérateur !",
            )
        else:
            messages.info(
                request,
                f"{target_user.netid} avait déjà des droits. Demande archivée.",
            )

    elif action == "reject":
        # Get the rejection reason from the validated form
        reason = form.cleaned_data["rejection_reason"]
        rep_request.rejection_reason = reason
        log_values["rejection_reason"] = ("", reason)

        messages.warning(
            request,
            f"La demande de {target_user.netid} a été refusée.",
        )

    # Log that the request was processed (and potentially the reason)
    ModerationLog.track(
        user=request.user, content_object=rep_request, values=log_values
    )

    rep_request.processed = True
    rep_request.save()

    return redirect("moderation_home")


@login_required
@user_passes_test(is_moderator, login_url="/")
def moderators_list(request):
    """Display the list of all Admins and Moderators"""
    moderators = User.objects.filter(Q(is_staff=True) | Q(is_moderator=True)).order_by(
        "-is_staff", "first_name"
    )
    return render(
        request, "moderation/moderators_management.html", {"moderators": moderators}
    )


@login_required
@user_passes_test(is_moderator, login_url="/")
@require_POST
def moderator_add(request):
    """Add a new moderator using their NetID"""
    netid_to_add = request.POST.get("netid", "").strip()
    if netid_to_add:
        try:
            target_user = User.objects.get(netid=netid_to_add)

            if not target_user.is_staff and not target_user.is_moderator:
                target_user.is_moderator = True
                target_user.save()

                ModerationLog.track(
                    user=request.user,
                    content_object=target_user,
                    values={"is_moderator": (False, True)},
                )
                messages.success(
                    request, f"{target_user.netid} est maintenant modérateur !"
                )
            else:
                messages.info(
                    request, "Cet utilisateur a déjà des droits (Modérateur ou Admin)."
                )
        except User.DoesNotExist:
            messages.warning(
                request,
                f"❌ L'étudiant avec le netid '{netid_to_add}' n'a pas été trouvé.",
            )

    return redirect("moderators_list")


@login_required
@user_passes_test(lambda u: u.is_staff, login_url="/")  # 🔒 Only Admins can remove
@require_POST
def moderator_remove(request, user_id):
    """Remove moderator rights from a user (Admin only)"""
    target_user = get_object_or_404(User, id=user_id)

    if target_user.is_staff:
        messages.warning(
            request, "Impossible de retirer les droits d'un Administrateur Système ici."
        )
    elif target_user == request.user:
        messages.warning(request, "Vous ne pouvez pas retirer vos propres droits ici.")
    elif target_user.is_moderator:
        target_user.is_moderator = False
        target_user.save()

        ModerationLog.track(
            user=request.user,
            content_object=target_user,
            values={"is_moderator": (True, False)},
        )
        messages.success(
            request, f"🗑️ Les droits de {target_user.netid} ont été retirés."
        )

    return redirect("moderators_list")


@login_required
def representative_request(request):
    # Check if there is a pending request
    if RepresentativeRequest.objects.filter(
        user=request.user, processed=False
    ).exists():
        return render(
            request,
            "moderation/representative_request_received.html",
        )

    # Get the last rejection reason if the user is not Admin or Mod
    rejection_msg = None
    if not request.user.is_moderator and not request.user.is_staff:
        last_req = (
            RepresentativeRequest.objects.filter(user=request.user, processed=True)
            .order_by("-created")
            .first()
        )
        if last_req and last_req.rejection_reason:
            rejection_msg = last_req.rejection_reason

    # Standard processing
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

    # Fetch all relevant logs, excluding noisy backend fields
    log_list = (
        ModerationLog.objects.exclude(
            target_field__in=["processed", "rejection_reason", "statut"]
        )
        .select_related("user", "content_type")
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
