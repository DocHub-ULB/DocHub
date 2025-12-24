import unicodedata

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse

UNCONVERTIBLE_TYPES = [
    ".zip",
    ".rar",
    ".tex",
    ".djvu",
    ".pages",
    ".goodnotes",
    ".apkg",
    ".one",
    ".mp4",
]


class Document(models.Model):
    class DocumentState(models.TextChoices):
        PREPARING = ("PREPARING", "En préparation")
        READY_TO_QUEUE = ("READY_TO_QUEUE", "Prêt à être ajouté à Celery")
        IN_QUEUE = ("IN_QUEUE", "Envoyé à Celery")
        PROCESSING = ("PROCESSING", "En cours de traitement")
        DONE = ("DONE", "Rendu fini")
        ERROR = ("ERROR", "Erreur")
        REPAIRED = ("REPAIRED", "Réparé")

    name = models.CharField(max_length=255, verbose_name="Titre")
    course = models.ForeignKey(
        "catalog.Course", null=True, verbose_name="Cours", on_delete=models.CASCADE
    )

    description = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Utilisateur", on_delete=models.CASCADE
    )
    tags = models.ManyToManyField("tags.Tag", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    size = models.PositiveIntegerField(default=0)
    pages = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)

    file_type = models.CharField(max_length=255, default="")
    original = models.FileField(upload_to="original_document")
    pdf = models.FileField(upload_to="pdf_document")
    thumbnail = models.FileField(upload_to="thumbnail", blank=True, default="")

    state = models.CharField(
        max_length=20,
        choices=DocumentState.choices,
        default=DocumentState.PREPARING,
        db_index=True,
        verbose_name="État",
    )
    md5 = models.CharField(max_length=32, default="", db_index=True)

    staff_pick = models.BooleanField(default=False, verbose_name="Staff pick")
    hidden = models.BooleanField(default=False, verbose_name="Est caché")

    import_source = models.CharField(
        max_length=1024, null=True, verbose_name="Importé depuis", blank=True
    )

    def __str__(self) -> str:
        return self.name

    @property
    def imported(self) -> bool:
        return self.import_source is not None

    @property
    def is_pdf(self) -> bool:
        return self.file_type in (".pdf", "application/pdf")

    # TODO use typed dict
    @property
    def votes(self):
        upvotes, downvotes = 0, 0
        # We do the filtering in python as this method is called from REST with all the necessary
        #   data already prefetched. Using self.vote_set.filter() would lead to another roundtrip
        #   to the database for each document. Thats bad.
        for vote in self.vote_set.all():
            vote_type = vote.vote_type
            if vote_type == Vote.VoteType.UPVOTE:
                upvotes += 1
            elif vote_type == Vote.VoteType.DOWNVOTE:
                downvotes += 1
            else:
                raise NotImplementedError("Vote not of known type.")

        return {"upvotes": upvotes, "downvotes": downvotes}

    def fullname(self) -> str:
        return self.__str__()

    def repair(self) -> None:
        if settings.READ_ONLY:
            raise Exception("Documents are read-only.")
        repair.delay(self.pk)

    def is_unconvertible(self) -> bool:
        return self.file_type in UNCONVERTIBLE_TYPES

    def is_ready(self) -> bool:
        return self.state in (
            Document.DocumentState.DONE,
            Document.DocumentState.REPAIRED,
        )

    def is_processing(self):
        return self.state in (
            Document.DocumentState.PREPARING,
            Document.DocumentState.IN_QUEUE,
            Document.DocumentState.PROCESSING,
        )

    @property
    def safe_name(self) -> str:
        return unicodedata.normalize("NFKD", self.name)

    def reprocess(self, force=False) -> None:
        if settings.READ_ONLY:
            raise Exception("Documents are read-only.")

        if self.state != Document.DocumentState.ERROR and not force:
            raise Exception("Document is not in error state it is " + self.state)

        self.state = Document.DocumentState.READY_TO_QUEUE
        self.md5 = ""
        self.add_to_queue()

    def add_to_queue(self) -> None:
        if settings.READ_ONLY:
            raise Exception("Documents are read-only.")

        self.state = Document.DocumentState.IN_QUEUE
        self.save()
        try:
            process_document.delay(self.id)
        except Exception as e:
            self.state = Document.DocumentState.READY_TO_QUEUE
            self.save()
            raise e

    def get_absolute_url(self) -> str:
        return reverse("document_show", args=(self.id,))

    def write_perm(self, user, moderated_courses) -> bool:
        if user.id == self.user_id:
            return True

        if self.course_id in moderated_courses:
            return True

        return False

    def tag_from_name(self) -> None:
        tags = logic.tags_from_name(self.name)
        self.tags.add(*tags)


class Vote(models.Model):
    class VoteType(models.TextChoices):
        UPVOTE = "up"
        DOWNVOTE = "down"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    when = models.DateTimeField(auto_now=True)
    vote_type = models.CharField(max_length=10, choices=VoteType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "document"], name="unique_user_document_vote"
            ),
        ]


class DocumentReport(models.Model):
    class ProblemType(models.TextChoices):
        WRONG_MODULE = "wrong_module", "Ce document est dans le mauvais cours"
        WRONG_TITLE = "wrong_title", "Le titre ou la description est erroné"
        LOW_QUALITY = "low_quality", "Contenu de mauvaise qualité ou inutile"
        READABILITY = "readability", "Problème de lisibilité"
        OTHER = "other", "Autre raison"

        @classmethod
        def get_description(cls, value: str) -> str:
            """Get the detailed description for a problem type."""
            descriptions = {
                cls.WRONG_MODULE: "Ce document appartient à un autre cours",
                cls.WRONG_TITLE: "Le contenu du document n'est pas correctement décrit",
                cls.LOW_QUALITY: "Le contenu peut être non pertinent, contenir uniquement le plan du cours, avoir de nombreuses fautes ou être (presque) vide",
                cls.READABILITY: "Le document est difficile à lire en raison d'une mauvaise écriture ou d'une photo de mauvaise qualité",
                cls.OTHER: "Une autre raison non listée ci-dessus",
            }
            return descriptions.get(value, "")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="Document",
    )
    problem_type = models.CharField(
        max_length=20,
        choices=ProblemType.choices,
        verbose_name="Type de problème",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["document", "created"]),
            models.Index(fields=["created"]),
        ]

    def __str__(self) -> str:
        return f"Report on {self.document.name} by {self.user}"


class DocumentError(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=255)
    exception = models.CharField(max_length=50000)
    traceback = models.TextField()

    def __str__(self):
        return "#" + self.exception


class BulkDocuments(models.Model):
    url = models.URLField()
    course = models.ForeignKey(
        "catalog.Course", null=False, verbose_name="Cours", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Utilisateur", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)


@receiver(pre_delete, sender=Document)
def cleanup_document_files(instance: Document, **kwargs) -> None:
    """
    Deletes all files when the database object is deleted.
    Checks that the name is not empty as that is what is returned when there is
        no file associated with the database object.
    """

    if settings.READ_ONLY:
        raise Exception("Documents are read-only.")

    pdf_file_name = instance.pdf.name
    if pdf_file_name != "" and instance.pdf.storage.exists(pdf_file_name):
        instance.pdf.storage.delete(pdf_file_name)

    original_file_name = instance.original.name
    if original_file_name != "" and instance.original.storage.exists(
        original_file_name
    ):
        instance.original.storage.delete(original_file_name)


from documents import logic  # NOQA

# Import at the end to avoid circular imports
from documents.tasks import process_document, repair  # NOQA
