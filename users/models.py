import re
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(UserManager):
    PATTERN = re.compile(r"[\W_]+")

    def _create_user(self, netid, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not netid:
            raise ValueError("The given netid must be set")
        email = self.normalize_email(email)
        user = self.model(netid=netid, email=email, last_login=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, netid, email=None, password=None, **extra_fields):
        return self._create_user(netid, email, password, **extra_fields)

    def create_superuser(self, netid, email, password, **extra_fields):
        return self._create_user(netid, email, password, is_staff=True, **extra_fields)


class User(AbstractBaseUser):
    USERNAME_FIELD = "netid"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]
    objects = CustomUserManager()

    netid = models.CharField(max_length=512, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=512)
    last_name = models.CharField(max_length=512)
    email = models.CharField(max_length=512, unique=True)
    welcome = models.BooleanField(default=True)
    comment = models.TextField(blank=True, default="")

    register_method = models.CharField(max_length=32)
    last_login_method = models.CharField(max_length=32)

    is_staff = models.BooleanField(default=False)
    is_academic = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    moderator_welcome_dismissed = models.BooleanField(default=False)
    promoted_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="promoted_users",
    )

    @property
    def is_recent(self):
        return timezone.now() - self.created < timedelta(days=30)

    @property
    def name(self):
        return "{0.first_name} {0.last_name}".format(self)

    @property
    def following_courses(self):
        return self.courses_set.all()

    def is_following(self, course):
        return self.courses_set.filter(slug=course.slug).exists()

    def has_module_perms(self, *args, **kwargs):
        return True  # TODO : is this a good idea ?

    def has_perm(self, perm_list, obj=None):
        return self.is_staff

    def moderation_perm(self, obj):
        return self.is_staff or self.is_moderator

    def write_perm(self, obj):
        if obj and (obj.user.id == self.id):
            return True

        return self.moderation_perm(obj)

    def fullname(self):
        return self.name

    def get_short_name(self):
        return self.netid

    def initials(self):
        return self.first_name[0] + self.last_name[0]
