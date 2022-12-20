from django.db import models


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
