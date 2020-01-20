from django.apps import AppConfig


class StreamsConfig(AppConfig):
    name = 'apps.streams'

    def ready(self):
        import apps.streams.signals