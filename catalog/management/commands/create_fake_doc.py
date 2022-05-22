# type: ignore

import random
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from coolname import generate

from catalog.models import Course
from documents.models import Document, Vote
from tags.models import Tag
from users.models import User

# 7 years
MAX_AGE = 3600 * 24 * 365 * 7


class Command(BaseCommand):
    help = "Loads a new courses tree into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--n",
            help="Max number of documents to generate per course",
            type=int,
            default=5,
        )

        parser.add_argument(
            "--netid",
            help="User that should own the documents (defaults to a random user for each doc)",
        )

        parser.add_argument(
            "--course",
            dest="slug",
            help="Add documents only to this course (defaults to all courses)",
        )

    def handle(self, n, netid, slug, *args, **options):
        if netid:
            user = User.objects.get(netid=netid)
        else:
            user = None

        tags = Tag.objects.all()
        self.stdout.write(f"Generating {n} documents per course...")

        courses = Course.objects.all()
        if slug:
            courses = courses.filter(slug=slug)

        for course in courses:
            for _ in range(random.randint(0, n)):
                doc = Document.objects.create(
                    name=" ".join(generate()),
                    course=course,
                    user=user if user else User.objects.order_by("?").first(),
                    pages=max(1, int(random.gauss(5, 10))),
                    import_source="fake-doc",
                )

                k = random.randint(0, len(tags))
                if choices := random.choices(tags, k=k):
                    doc.tags.set(choices)

                for user in User.objects.order_by("?")[: random.randint(0, 4)]:
                    t = random.choices(Vote.VoteType.values, [1, 5], k=1)[0]
                    Vote.objects.create(user=user, document=doc, vote_type=t)

        self.stdout.write("Done")
