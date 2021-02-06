from django.apps import AppConfig


class TelepathyConfig(AppConfig):
    name = 'telepathy'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Thread'))
        registry.register(self.get_model('Message'))
