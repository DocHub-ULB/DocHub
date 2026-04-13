import collections.abc

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet


class RepresentativeRequest(models.Model):
    class Faculty(models.TextChoices):
        DROIT = "droit", "Droit"
        MEDECINE = "medecine", "Médecine"
        MOTRICITE = "motricite", "Motricité"
        PHARMA = "pharma", "Pharmacie"
        PHILO = "philo", "Philosophie et Sciences Sociales"
        POLYTECH = "polytech", "Polytech"
        SCIENCES = "sciences", "Sciences"
        SOLVAY = "solvay", "Solvay"
        OTHER = "other", "Autre"

    class Role(models.TextChoices):
        COURSE = "course", "Délégué cours du cercle"
        BUREAU = "bureau", "Membre du bureau étudiant"
        DELEGATE = "delegate", "Délégué d'année"
        MOTIVATED = "motivated", "Étudiant motivé"
        OTHER = "other", "Autre"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    faculty = models.CharField(
        max_length=255, choices=Faculty.choices, verbose_name="Faculté"
    )
    role = models.CharField(
        max_length=255,
        choices=Role.choices,
    )
    comment = models.TextField(verbose_name="Commentaires", blank=True)

    created = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    rejection_reason = models.TextField(verbose_name="Raison du refus", blank=True)

    def __str__(self):
        return f"Demande d'accès de {self.user.netid}"


class ModerationLog(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    target_field = models.CharField(max_length=512)
    old_value = models.CharField(max_length=512)
    new_value = models.CharField(max_length=512)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user.get_short_name()} a fait une action le {self.timestamp.strftime('%d/%m/%Y')}"

    ### Action translation logic ###

    @property
    def action_text(self):
        """Translates the technical action into a readable French sentence. Acts as a catch-all."""
        if self.target_field == "is_moderator":
            return (
                "a promu modérateur"
                if str(self.new_value) == "True"
                else "a retiré les droits de"
            )
        elif self.target_field == "action_accepter":
            return "a accepté la demande de"
        elif self.target_field == "action_rejeter":
            return "a refusé la demande de"

        # Fallback for all other technical fields (e.g., 'visible', 'is_active', title changes)
        return f"a modifié le champ '{self.target_field}' de"

    @property
    def action_color(self):
        """Assigns a Bootstrap color based on the action type. Acts as a catch-all."""
        if self.target_field == "is_moderator":
            return "success" if str(self.new_value) == "True" else "danger"
        elif self.target_field == "action_accepter":
            return "success"
        elif self.target_field == "action_rejeter":
            return "warning"

        # Specific colors for known fallback fields
        if self.target_field in ["visible", "is_active"]:
            return "success" if str(self.new_value) == "True" else "danger"

        return "secondary"

    @property
    def target_text(self):
        """Smartly retrieves the target NetID or object name. Acts as a catch-all."""
        if not self.content_object:
            return f"Objet supprimé (ID: {self.object_id})"

        if self.content_type.model == "representativerequest":
            return self.content_object.user.netid
        if self.content_type.model == "user":
            return self.content_object.netid

        # Fallback for Documents, Courses, etc.
        return str(self.content_object)

    @property
    def details_text(self):
        """Displays additional details (like the rejection reason or old values for legacy logs)"""
        if self.target_field == "action_rejeter" and self.new_value != "Sans motif":
            return f'Motif : "{self.new_value}"'

        # If it's a technical fallback action, we show what changed
        if self.target_field not in [
            "is_moderator",
            "action_accepter",
            "action_rejeter",
        ]:
            # Truncate strings that are too long to avoid breaking the UI
            old = (
                self.old_value[:40] + "..."
                if len(self.old_value) > 40
                else self.old_value
            )
            new = (
                self.new_value[:40] + "..."
                if len(self.new_value) > 40
                else self.new_value
            )
            return f"Ancienne valeur : {old} ➔ Nouvelle valeur : {new}"

        return ""

    @classmethod
    def track(cls, user, content_object: models.Model, values: dict[str, tuple]):
        """
        Saves a new ModerationLog for each field that has changed
        `values` should be dict where the key is the field name, and the value is a tuple of [old value of the field, new value of the field].
        The old and new values should be strings of lists (in that case, every item of the list is converted to a str and then joined by comas.
        """
        for field, (old, new) in values.items():
            if isinstance(old, (collections.abc.Iterable, QuerySet)) and not isinstance(  # type: ignore
                old, str
            ):
                old = ",".join([str(x) for x in old])  # noqa: PLW2901
            if isinstance(new, (collections.abc.Iterable, QuerySet)) and not isinstance(  # type: ignore
                new, str
            ):
                new = ",".join([str(x) for x in new])  # noqa: PLW2901
            if old != new:
                cls.objects.create(
                    user=user,
                    content_object=content_object,
                    target_field=field,
                    old_value=old,
                    new_value=new,
                )
