from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    name = 'documents'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Document'))
