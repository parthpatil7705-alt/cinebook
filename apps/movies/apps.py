from django.apps import AppConfig

class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.movies'
    label = 'movies'

    def ready(self):
        import apps.movies.signals
