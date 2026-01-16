from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    # Include here whatever separate signals file you add to the application and want to utilize.
    def ready(self):
        pass
