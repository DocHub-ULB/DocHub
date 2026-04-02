from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from moderation.forms import RepresentativeRequestForm
from moderation.models import ModerationLog, RepresentativeRequest

User = get_user_model()


def is_moderator(user):
    # On donne l'accès aux Admins (is_staff) ET aux Modérateurs (is_moderator)
    return user.is_staff or user.is_moderator


@login_required
@user_passes_test(is_moderator)
def moderation_home(request):
    return render(request, "moderation/home.html")


@login_required
@user_passes_test(is_moderator)
def moderators_management(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # ACTION : AJOUTER UN MODÉRATEUR
        if action == "add":
            netid_to_add = request.POST.get("netid", "").strip()
            if netid_to_add:
                try:
                    target_user = User.objects.get(netid=netid_to_add)

                    # Vérifier qu'il n'est ni Admin ni déjà Modérateur
                    if not target_user.is_staff and not target_user.is_moderator:
                        target_user.is_moderator = True
                        target_user.save()

                        # ON CRÉE LE LOG ICI
                        ModerationLog.track(
                            user=request.user,
                            content_object=target_user,
                            values={"is_moderator": (False, True)},
                        )

                        messages.success(
                            request,
                            f"{target_user.netid} est maintenant modérateur !",
                        )
                    else:
                        messages.info(
                            request,
                            "Cet utilisateur a déjà des droits (Modérateur ou Admin).",
                        )
                except User.DoesNotExist:
                    messages.warning(
                        request,
                        f"❌ L'étudiant avec le netid '{netid_to_add}' n'a pas été trouvé.",
                    )

        # ACTION : RETIRER UN MODÉRATEUR
        elif action == "remove":
            user_id = request.POST.get("user_id")
            target_user = get_object_or_404(User, id=user_id)

            # Sécurité : impossible de toucher à un Admin ou de se retirer soi-même
            # Gerer dans le Html en desactivant les boutons, mais on double la sécurité ici
            if target_user.is_staff:
                messages.warning(
                    request,
                    "Impossible de retirer les droits d'un Administrateur Système ici.",
                )
            elif target_user == request.user:
                messages.warning(
                    request, "Vous ne pouvez pas retirer vos propres droits ici."
                )
            elif target_user.is_moderator:
                target_user.is_moderator = False
                target_user.save()

                # ON CRÉE LE LOG ICI
                ModerationLog.track(
                    user=request.user,
                    content_object=target_user,
                    values={"is_moderator": (True, False)},
                )

                messages.success(
                    request, f"🗑️ Les droits de {target_user.netid} ont été retirés."
                )

        return redirect("moderators_management")

    # Affichage de la page (GET) - On liste les Admins et les Modérateurs
    moderators = User.objects.filter(Q(is_staff=True) | Q(is_moderator=True)).order_by(
        "-is_staff", "first_name"
    )

    return render(
        request, "moderation/moderators_management.html", {"moderators": moderators}
    )


@login_required
def representative_request(request):
    if RepresentativeRequest.objects.filter(
        user=request.user, processed=False
    ).exists():
        return render(
            request,
            "moderation/representative_request_received.html",
        )

    if request.method == "POST":
        form = RepresentativeRequestForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.user = request.user
            form.instance.save()
            return redirect("representative_request")
    else:
        form = RepresentativeRequestForm()
    return render(request, "moderation/representative_request.html", {"form": form})
