import hashlib
import re
import zlib
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import RANDOM_STRING_CHARS, get_random_string


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
    def is_first_week(self):
        return timezone.now() - self.created < timedelta(days=7)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def following_courses(self):
        return self.courses_set.all()

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


class CasFailure(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=64)
    details = models.TextField(blank=True, default="")
    ticket = models.CharField(max_length=512, blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.code} ({self.created:%Y-%m-%d %H:%M})"


class AccessToken(models.Model):
    """A key a user gives to a program (an AI agent, a script...) for the API.

    We only store a hash of the key: the user sees it once, when it is created.

    A key has 3 parts, one after the other, like GitHub's keys:

        dh_  xY3kP9...(32 characters)...Qa7  0aZ9bC
        |    |                               |
        |    random part                     checksum
        prefix

    - The prefix (PREFIX) tells people and secret scanners that it is a
      DocHub key, for example when someone pushes it to GitHub by mistake.
    - The random part (RANDOM_LENGTH letters and digits, from Django's
      get_random_string) is the secret itself: about 190 bits.
    - The checksum (CHECKSUM_LENGTH letters and digits) is the CRC32 of the
      random part, see checksum(). With it, is_well_formed() spots a
      mistyped or cut key without a database query, and the middleware
      tells the user that their key is badly copied rather than unknown.

    The random part and the checksum use only letters and digits, so they
    never need escaping in a URL, a header or a shell.
    """

    PREFIX = "dh_"
    RANDOM_LENGTH = 32  # About 190 bits
    CHECKSUM_LENGTH = 6

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="access_tokens"
    )
    name = models.CharField(max_length=100, verbose_name="Nom")
    key_hash = models.CharField(max_length=64, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    request_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.name} ({self.user.netid})"

    @staticmethod
    def hash_key(key: str) -> str:
        # Not make_password(): it is salted, so we could not find a token from
        # its key, and slow on purpose, which we do not need for random keys.
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    def checksum(cls, random_part: str) -> str:
        """The CRC32 of the random part, written with letters and digits."""
        number = zlib.crc32(random_part.encode())
        digits = ""
        for _ in range(cls.CHECKSUM_LENGTH):
            number, digit = divmod(number, len(RANDOM_STRING_CHARS))
            digits = RANDOM_STRING_CHARS[digit] + digits
        return digits

    @classmethod
    def is_well_formed(cls, key: str) -> bool:
        random_part = key.removeprefix(cls.PREFIX)[: cls.RANDOM_LENGTH]
        return key == cls.PREFIX + random_part + cls.checksum(random_part)

    @classmethod
    def create_for(cls, user: "User", name: str) -> tuple["AccessToken", str]:
        """Returns the new token and its key, which we cannot show again later."""
        random_part = get_random_string(cls.RANDOM_LENGTH)
        key = cls.PREFIX + random_part + cls.checksum(random_part)
        token = cls.objects.create(user=user, name=name, key_hash=cls.hash_key(key))
        return token, key

    def as_json(self) -> dict:
        return {
            "id": self.pk,
            "name": self.name,
            "created": self.created.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "request_count": self.request_count,
        }


class DailyUsage(models.Model):
    """How many documents a user downloaded and uploaded on a given day.

    The browser and the API tokens of a user share the same counters, so the
    API cannot go around the daily caps.
    """

    class Kind(models.TextChoices):
        DOWNLOAD = ("downloads", "Téléchargements")
        UPLOAD = ("uploads", "Envois")

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="daily_usages"
    )
    day = models.DateField()
    downloads = models.PositiveIntegerField(default=0)
    uploads = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "day"], name="unique_usage_day")
        ]

    @classmethod
    def today_for(cls, user: "User") -> "DailyUsage":
        usage, _ = cls.objects.get_or_create(user=user, day=timezone.localdate())
        return usage

    @classmethod
    def consume(cls, user: "User", kind: Kind) -> bool:
        """Counts one more download or upload, unless the daily cap is reached."""
        usage = cls.today_for(user)
        if getattr(usage, kind) >= settings.DAILY_CAPS[kind]:
            return False
        cls.objects.filter(pk=usage.pk).update(**{kind: F(kind) + 1})
        return True
