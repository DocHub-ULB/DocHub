from django.apps import AppConfig
from actstream import registry


class CatalogConfig(AppConfig):
    name = 'catalog'

    def ready(self):
        registry.register(self.get_model('Course'))
