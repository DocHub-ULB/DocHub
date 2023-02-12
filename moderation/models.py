from typing import Tuple

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
        return f"{self.user.get_short_name()} modified {self.content_type.name}#{self.object_id} {self.target_field}: '{self.old_value}' -> '{self.new_value}'"

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
                old = ",".join([str(x) for x in old])
            if isinstance(new, (collections.abc.Iterable, QuerySet)) and not isinstance(  # type: ignore
                new, str
            ):
                new = ",".join([str(x) for x in new])
            if old != new:
                cls.objects.create(
                    user=user,
                    content_object=content_object,
                    target_field=field,
                    old_value=old,
                    new_value=new,
                )
