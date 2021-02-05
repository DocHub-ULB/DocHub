from django.core.management.base import BaseCommand

from documents.models import Document


class Command(BaseCommand):

    help = 'Auto-tag documents based on their name'

    def handle(self, *args, **options):
        docs = Document.objects.all()
        self.stdout.write('Auto-tagging %i documents...' % docs.count())

        for doc in docs:
            doc.tag_from_name()

        self.stdout.write('Done.\n')
