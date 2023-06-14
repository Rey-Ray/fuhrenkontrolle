from django.apps import AppConfig
from . import custom_tags

class BeetDeliveryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beetdelivery'

    def ready(self):
        import beetdelivery.templatetags.custom_tags