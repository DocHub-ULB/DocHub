from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'users'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('User'))
