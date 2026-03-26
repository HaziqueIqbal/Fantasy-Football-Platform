from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fantasyfootball.user"
    label = "user"

    def ready(self):
        import fantasyfootball.user.signals  # noqa: F401
