from django.apps import AppConfig
from actstream import registry


class TagsConfig(AppConfig):
    name = 'tags'

    def ready(self):
        registry.register(self.get_model('Tag'))
