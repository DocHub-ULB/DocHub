import random

from coolname import generate

from catalog.models import Course
from documents.models import Document
from tags.models import Tag
from users.models import User

Tag.objects.create(name="officiel")
Tag.objects.create(name="examen")
Tag.objects.create(name="resume")
Tag.objects.create(name="synthese")
Tag.objects.create(name="notes")


for course in Course.objects.all():
    for i in range(16):
        doc = Document.objects.create(
            name=" ".join(generate()),
            course=course,
            user=User.objects.first(),
        )
        for i in range(random.randint(0, 4)):
            doc.tags.add(Tag.objects.order_by("?").first())
