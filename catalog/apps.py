from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = 'catalog'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Course'))
