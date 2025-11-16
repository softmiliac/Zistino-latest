from django.apps import AppConfig


class PointsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zistino_apps.points'

    def ready(self):
        """Import signals when app is ready."""
        import zistino_apps.points.signals

