# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver

from tags.models import Tag


@python_2_unicode_compatible
class Document(models.Model):
    STATES = (
        ('PREPARING', 'En préparation'),
        ('READY_TO_QUEUE', 'Prêt à être ajouté à Celery'),
        ('IN_QUEUE', 'Envoyé à Celery'),
        ('PROCESSING', 'En cours de traitement'),
        ('DONE', 'Rendu fini'),
        ('ERROR', 'Erreur'),
    )

    name = models.CharField(max_length=255, verbose_name='Titre')
    course = models.ForeignKey('catalog.Course', null=True, verbose_name='Cours')

    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Utilisateur')
    tags = models.ManyToManyField('tags.Tag', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    size = models.PositiveIntegerField(default=0)
    pages = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)

    file_type = models.CharField(max_length=255, default='')
    original = models.FileField(upload_to='original_document')
    pdf = models.FileField(upload_to='pdf_document')

    state = models.CharField(max_length=20, choices=STATES, default='PREPARING', db_index=True, verbose_name='État')
    md5 = models.CharField(max_length=32, default='', db_index=True)

    hidden = models.BooleanField(default=False, verbose_name='Est caché')

    def __str__(self):
        return self.name

    def fullname(self):
        return self.__str__()

    def reprocess(self, force=False):
        if self.state != "ERROR" and not force:
            raise Exception("Document is not in error state it is " + self.state)

        for page in self.page_set.all():
            page.delete()

        self.state = 'READY_TO_QUEUE'
        self.md5 = ""
        self.add_to_queue()

    def add_to_queue(self):
        self.state = "IN_QUEUE"
        self.save()
        try:
            process_document.delay(self.id)
        except Exception as e:
            self.state = "READY_TO_QUEUE"
            self.save()
            raise e

    def get_absolute_url(self):
        return reverse('document_show', args=(self.id, ))

    def write_perm(self, user, moderated_courses):
        if user.id == self.user_id:
            return True

        if self.course_id in moderated_courses:
            return True

        return False

    def tag_from_name(self):
        name = self.name.lower().replace(u"é", "e").replace(u"è", "e").replace(u"ê", "e")
        tags = []

        has_month = (
            "janv" in name
            or "aout" in name
            or "sept" in name
            or "juin" in name
            or "mai" in name
        )
        if has_month or "exam" in name:
            tags.append("examen")

        if "corr" in name:
            tags.append("corrigé")

        if "tp" in name or "seance" in name:
            tags.append("tp")

        if "resum" in name or "r?sum" in name or "rsum" in name:
            tags.append("résumé")

        if "slide" in name or "transparent" in name:
            tags.append("slides")

        if "formulaire" in name:
            tags.append("formulaire")

        if "rapport" in name or "labo" in name:
            tags.append("laboratoire")

        for tag in tags:
            tag = Tag.objects.get_or_create(name=tag)[0]
            self.tags.add(tag)


class Page(models.Model):
    numero = models.IntegerField(db_index=True)
    document = models.ForeignKey(Document, db_index=True)

    bitmap_120 = models.ImageField(upload_to='page_120', height_field="height_120")
    bitmap_600 = models.ImageField(upload_to='page_600', height_field="height_600")
    bitmap_900 = models.ImageField(upload_to='page_900', height_field="height_900")

    height_120 = models.PositiveIntegerField(default=0)
    height_600 = models.PositiveIntegerField(default=0)
    height_900 = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['numero']

    def get_absolute_url(self):
        return self.document.get_absolute_url() + "#page-{}".format(self.numero)


@python_2_unicode_compatible
class DocumentError(models.Model):
    document = models.ForeignKey(Document)
    task_id = models.CharField(max_length=255)
    exception = models.CharField(max_length=1000)
    traceback = models.TextField()

    def __str__(self):
        return "#" + self.exception

@receiver(post_delete, sender=Document)
def cleanup_document_files(instance, **kwargs):
    pdf_file_name = instance.pdf.name
    if pdf_file_name != '' and instance.pdf.storage.exists(pdf_file_name):
        instance.pdf.storage.delete(pdf_file_name)

    original_file_name = instance.original.name
    if original_file_name != '' and instance.original.storage.exists(original_file_name):
        instance.original.storage.delete(original_file_name)


@receiver(post_delete, sender=Page)
def cleanup_page_files(instance, **kwargs):

    filename_120 = instance.bitmap_120.name
    if filename_120 != '' and instance.bitmap_120.storage.exists(filename_120):
        instance.bitmap_120.storage.delete(filename_120)

    filename_600 = instance.bitmap_600.name
    if filename_120 != '' and instance.bitmap_600.storage.exists(filename_600):
        instance.bitmap_600.storage.delete(filename_600)

    filename_900 = instance.bitmap_900.name
    if filename_120 != '' and instance.bitmap_900.storage.exists(filename_900):
        instance.bitmap_900.storage.delete(filename_900)

from documents.tasks import process_document
