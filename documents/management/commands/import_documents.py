import glob
import os

from django.core.files import File
from django.core.management.base import BaseCommand

from catalog.models import Course
from documents import logic
from users.models import User

TAGS = {
    "off": "officiel",
    "ref": "référence",
    "sli": "slides",
    "res": "résumé",
    "exa": "examen",
    "tp": "tp",
    "syl": "syllabus",
    "cor": "corrigé",
    "corr": "corrigé",
    "for": "formulaire",
    "sol": "corrigé",
    "lab": "laboratoire",
    "law": "loi",
}


class Command(BaseCommand):

    help = "Import documents in a course"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path", action="store", dest="path", default="", help="Documents path"
        )
        parser.add_argument(
            "--user",
            action="store",
            dest="username",
            default="",
            help="user owning the documents",
        )
        parser.add_argument(
            "--course",
            action="store",
            dest="course_slug",
            default="",
            help="course slug",
        )

    def handle(self, *args, **options):
        netid = options["username"]
        self.stdout.write(f'Looking for user "{netid}"')

        user = User.objects.filter(netid=netid).first()
        if user is None:
            self.stdout.write("Could not find user.")
            return

        slug = options["course_slug"]
        self.stdout.write(f'Looking for course "{slug}"')

        course = Course.objects.filter(slug=slug).first()
        if course is None:
            self.stdout.write("Could not find course.")
            return

        path = options["path"]
        self.stdout.write(f'Gathering documents in "{path}"')
        if not os.path.exists(path):
            self.stdout.write("Path does not exist")
            return

        paths = glob.glob(os.path.join(path, "*.*"))

        for doc_path in paths:
            import_document_from_path(doc_path, course, user)
            self.stdout.write(".", ending="")
            self.stdout.flush()


def import_document_from_path(doc_path, course, user):
    filename = os.path.split(doc_path)[1]
    tags, filename = extract_tags(filename)
    name, extension = os.path.splitext(filename)

    name = logic.clean_filename(name)

    with open(doc_path, "rb") as fd:
        document = logic.add_file_to_course(
            file=File(fd),
            name=name,
            extension=extension,
            course=course,
            tags=tags,
            user=user,
        )

    document.add_to_queue()


def extract_tags(filename):
    if ":" not in filename:
        return [], filename

    tags, name = filename.split(":", 1)
    tags = tags.split(",")
    tags = [TAGS.get(x.lower()) for x in tags]
    tags = [tag for tag in tags if tag]

    return tags, name
