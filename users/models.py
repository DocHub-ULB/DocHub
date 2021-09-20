import collections
import itertools
import os
import re
from os.path import join

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.authtoken.models import Token

from catalog.models import Category, Course


class CustomUserManager(UserManager):
    PATTERN = re.compile(r'[\W_]+')

    def _create_user(self, netid, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not netid:
            raise ValueError('The given netid must be set')
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

    USERNAME_FIELD = 'netid'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    DEFAULT_PHOTO = join(settings.STATIC_URL, "images/default.jpg")
    objects = CustomUserManager()

    netid = models.CharField(max_length=20, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=127)
    last_name = models.CharField(max_length=127)
    email = models.CharField(max_length=255, unique=True)
    registration = models.CharField(max_length=80, blank=True)
    welcome = models.BooleanField(default=True)
    comment = models.TextField(blank=True, default='')

    register_method = models.CharField(max_length=32)
    last_login_method = models.CharField(max_length=32)

    inferred_faculty = models.TextField(blank=True)
    inscription_faculty = models.TextField(blank=True)

    is_staff = models.BooleanField(default=False)
    is_academic = models.BooleanField(default=False)
    is_representative = models.BooleanField(default=False)

    moderated_courses = models.ManyToManyField('catalog.Course', blank=True)

    notify_on_response = models.BooleanField(default=True)
    notify_on_new_doc = models.BooleanField(default=True)
    notify_on_new_thread = models.BooleanField(default=True)
    notify_on_upload = True

    def __init__(self, *args, **kwargs):
        self._moderated_courses = None
        super().__init__(*args, **kwargs)

    @property
    def name(self):
        return "{0.first_name} {0.last_name}".format(self)

    @property
    def api_token(self):
        token, _created = Token.objects.get_or_create(user=self)

        return token

    # def getPrograms(self):
    #     """Returns a QS of the programs in which a course is followed by the user"""
    #     blocs = Category.objects.filter(course__in=self.following_courses).select_related('parent')
    #     programs = [bloc.parent.slug for bloc in blocs.all()]
    #     return Category.objects.filter(level=2, slug__in=programs).annotate(
    #         slug_=models.functions.Cast(
    #             models.functions.Concat(
    #                 models.Value("mycourses-"), 'slug'
    #             ), output_field=models.SlugField()
    #         ),
    #     )

    # def getBlocs(self, program_slug):
    #     """Returns a QS of blocs that contain a course the user follows"""
    #     return set(Category.objects.filter(
    #         level=3, parent__slug=program_slug,
    #         course__in=self.following_courses
    #     ))

    @property
    def following_courses(self):
        return self.courses_set.all()

    def is_following(self, course: Course):
        return self.courses_set.filter(slug=course.slug).exists()

    def has_module_perms(self, *args, **kwargs):
        return True # TODO : is this a good idea ?

    def has_perm(self, perm_list, obj=None):
        return self.is_staff

    def write_perm(self, obj):
        if self.is_staff:
            return True

        if obj is None:
            return False

        if self._moderated_courses is None:
            ids = [course.id for course in self.moderated_courses.only('id')]
            self._moderated_courses = ids

        return obj.write_perm(self, self._moderated_courses)

    def fullname(self):
        return self.name

    def get_short_name(self):
        return self.netid

    def update_inscription_faculty(self):
        inscription = self.inscription_set.order_by("-year").first()
        if inscription:
            self.inscription_faculty = inscription.faculty
            self.save()

    def update_inferred_faculty(self):
        courses = self.following_courses
        categories = [x.categories.all() for x in courses]
        categories = list(itertools.chain.from_iterable(categories))

        faculties = [x.get_ancestors().filter(level=1).all() for x in categories]
        faculties = list(itertools.chain.from_iterable(faculties))

        counts = collections.Counter(faculties)
        if counts:
            faculty = counts.most_common()[0][0]
            self.inferred_faculty = faculty.name
            self.save()


class Inscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    faculty = models.CharField(max_length=80, blank=True, default='')
    section = models.CharField(max_length=80, blank=True, default='')
    year = models.PositiveIntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'section', 'faculty', 'year')
