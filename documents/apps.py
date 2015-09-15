from django.apps import AppConfig
from actstream import registry


class DocumentsConfig(AppConfig):
    name = 'documents'

    def ready(self):
        registry.register(self.get_model('Document'))
