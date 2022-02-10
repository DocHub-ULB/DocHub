from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default="")
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    categories = models.ManyToManyField(Category)
    description = models.TextField(default="")

    followed_by = models.ManyToManyField("users.User", related_name="courses_set")

    class Meta:
        ordering = ["slug"]

    def gehol_url(self):
        slug = self.slug.replace("-", "").upper()
        return f"https://gehol.ulb.ac.be/gehol/Vue/HoraireCours.php?cours={slug}"

    def get_absolute_url(self):
        return reverse("course_show", args=(self.slug,))

    def __str__(self):
        return self.slug.upper()

    def fullname(self):
        return f"{self.name} ({self.slug.lower()})"

    @property
    def followers_count(self) -> int:
        return self.followed_by.count()


class CourseUserView(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    views = models.IntegerField(default=1)
    last_view = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "course")

    @classmethod
    def visit(cls, user, course: Course):
        obj, created = cls.objects.get_or_create(user=user, course=course)
        if not created and (timezone.now() - obj.last_view) > timedelta(minutes=5):
            # Do not use F("views") + 1 here as we DO want a race condition to happen.
            # Indeed, if the user loads 2 pages at the same instant, we want to count only
            # one of them (as we count a new page view every 5 min only)
            obj.views = obj.views + 1
            obj.save()
