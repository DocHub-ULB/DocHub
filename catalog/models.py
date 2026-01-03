from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True, unique=True)
    description = models.TextField(blank=True, default="")
    parents = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="children",
    )

    is_archive = models.BooleanField(default=False)

    class CategoryType(models.TextChoices):
        BACHELOR = "BA", _("Bachelier")
        MASTER = "MA", _("Master")
        MASTER_SPECIALIZATION = "MS", _("Master de spécialisation")
        CERTIFICATE = "CERT", _("Certificat")
        AGGREGATION = "AGG", _("Agrégation")
        UNIVERSITY = "UNI", _("Université")
        FACULTY = "FAC", _("Faculté")
        BLOC = "BLOC", _("Bloc")

    type = models.CharField(
        max_length=4,
        choices=CategoryType.choices,
        default=None,
        null=True,
    )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["id"]

    def __str__(self):
        return self.name

    def better_name(self):
        name = self.name
        name = (
            name.removeprefix("Faculté de ")
            .removeprefix("Faculté d'")
            .removeprefix("Faculté des ")
        )
        name = name.replace(
            "Agrégation de l'enseignement secondaire supérieur - ", ""
        ).replace(
            "Certificat d'aptitude pédagogique approprié à l'enseignement supérieur - ",
            "",
        )
        name = name.replace("Master en enseignement section ", "Enseignement ")

        name = name.removeprefix("Bachelier en ").removeprefix("Bachelier : ")
        name = (
            name.removeprefix("Master en ")
            .removeprefix("Master : ")
            .removeprefix("Master de spécialisation en ")
            .removeprefix("Master de ")
        )

        if "orientation" in name:
            name = name.replace("orientation générale", "orientation Général").replace(
                "orientation ", "("
            ) + ")".replace("Général à finalité", "")
        rr = {
            "Haute Ecole Libre de Bruxelles": "HELB",
            "Institut des Hautes Etudes des Communications Sociales": "IHECS",
            "Solvay": "Solvay",
        }
        for k, v in rr.items():
            if k in name:
                name = v

        name = name.replace("sciences de la santé publique à finalité", "")
        name = name.replace(", (", " (")

        if "sciences de l'ingénieur (" in name:
            name = name.replace("sciences de l'ingénieur (", "").replace(")", "")

        name = name.replace("(Général)", "")

        name = name.replace(" ,", ",").replace("( ", "(")

        name = name.replace(", option Bruxelles", "")
        name = name.replace("(Site de Charleroi)", "(Charleroi)")
        name = name.replace("(Site de Mons)", "(Mons)")
        name = name.replace("(Général à finalité ", "(")

        name = name.replace("option SOIR", "(soir)")
        name = name.replace("option JOUR", "")

        name = name.replace("), (", ", ")
        name = name.removesuffix(", ")

        return name


class PeriodType(models.TextChoices):
    FIRST = "Q1", _("1er quadri")
    SECOND = "Q2", _("2ème quadri")
    BOTH = "Y", _("Toute l'année")
    UNKNOWN = "?", _("Inconnu")


class Course(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    categories = models.ManyToManyField(Category, through="CourseCategory")  # type: ignore
    description = models.TextField(default="")
    period = models.CharField(
        max_length=4,
        choices=PeriodType,
        default=PeriodType.UNKNOWN,
    )

    followed_by = models.ManyToManyField("users.User", related_name="courses_set")
    is_archive = models.BooleanField(default=False)

    class Meta:
        ordering = ["slug"]

    def gehol_url(self):
        slug = self.slug.replace("-", "").upper()
        return f"https://gehol.ulb.ac.be/gehol/Vue/HoraireCours.php?cours={slug}"

    def get_absolute_url(self):
        return reverse("catalog:course_show", args=(self.slug,))

    def __str__(self):
        return self.slug

    def fullname(self):
        return f"{self.name} ({self.slug.lower()})"

    @property
    def followers_count(self) -> int:
        return self.followed_by.count()


class CourseCategory(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    mandatory = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "category"], name="unique_course_category"
            ),
        ]


class CourseUserView(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    views = models.IntegerField(default=1)
    last_view = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="unique_user_course_view"
            ),
        ]

    @classmethod
    def visit(cls, user, course: Course):
        obj, created = cls.objects.get_or_create(user=user, course=course)
        if not created and (timezone.now() - obj.last_view) > timedelta(minutes=5):
            # Do not use F("views") + 1 here as we DO want a race condition to happen.
            # Indeed, if the user loads 2 pages at the same instant, we want to count only
            # one of them (as we count a new page view every 5 min only)
            obj.views = obj.views + 1
            obj.save()
