# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse

from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import unicodedata

from tags.models import Tag

UNCONVERTIBLE_TYPES = [
    '.zip',
    '.rar',
    '.tex',
    '.djvu',
    '.pages',
]


class Document(models.Model):
    STATES = (
        ('PREPARING', 'En préparation'),
        ('READY_TO_QUEUE', 'Prêt à être ajouté à Celery'),
        ('IN_QUEUE', 'Envoyé à Celery'),
        ('PROCESSING', 'En cours de traitement'),
        ('DONE', 'Rendu fini'),
        ('ERROR', 'Erreur'),
        ('REPAIRED', 'Réparé'),
    )

    name = models.CharField(max_length=255, verbose_name='Titre')
    course = models.ForeignKey('catalog.Course', null=True, verbose_name='Cours', on_delete=models.CASCADE)

    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Utilisateur', on_delete=models.CASCADE)
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

    @property
    def votes(self):
        upvotes, downvotes = 0, 0
        # We do the filtering in python as this method is called from REST with all the necessary
        #   data already prefetched. Using self.vote_set.filter() would lead to another roundtrip
        #   to the database for each document. Thats bad.
        for vote in self.vote_set.all():
            vote_type = vote.vote_type
            if vote_type == Vote.UPVOTE:
                upvotes += 1
            elif vote_type == Vote.DOWNVOTE:
                downvotes += 1
            else:
                raise NotImplemented("Vote not of known type.")

        return {"upvotes": upvotes, "downvotes": downvotes}

    def fullname(self):
        return self.__str__()

    def repair(self):
        repair.delay(self.id)

    def is_unconvertible(self):
        return self.file_type in UNCONVERTIBLE_TYPES

    def is_ready(self):
        return self.state in ('DONE', 'REPAIRED')

    def is_processing(self):
        return self.state in ('PREPARING', 'IN_QUEUE', 'PROCESSING')

    @property
    def safe_name(self):
        return unicodedata.normalize("NFKD", self.name)

    def reprocess(self, force=False):
        if self.state != "ERROR" and not force:
            raise Exception("Document is not in error state it is " + self.state)

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
            "janv" in name or
            "aout" in name or
            "sept" in name or
            "juin" in name or
            "mai" in name
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


class Vote(models.Model):
    UPVOTE = "up"
    DOWNVOTE = "down"
    VOTE_TYPE_CHOICES = (
        (UPVOTE, "Upvote"),
        (DOWNVOTE, "Downvote")
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now=True)
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPE_CHOICES)

    class Meta:
        unique_together = ("user", "document")


class DocumentError(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=255)
    exception = models.CharField(max_length=1000)
    traceback = models.TextField()

    def __str__(self):
        return "#" + self.exception


@receiver(pre_delete, sender=Document)
def cleanup_document_files(instance, **kwargs):
    """
    Deletes all files when the database object is deleted.
    Checks that the name is not empty as that is what is returned when there is
        no file associated with the database object.
    """

    pdf_file_name = instance.pdf.name
    if pdf_file_name != '' and instance.pdf.storage.exists(pdf_file_name):
        instance.pdf.storage.delete(pdf_file_name)

    original_file_name = instance.original.name
    if original_file_name != '' and instance.original.storage.exists(original_file_name):
        instance.original.storage.delete(original_file_name)


# Import at the end to avoid circular imports
from documents.tasks import process_document, repair # NOQA
