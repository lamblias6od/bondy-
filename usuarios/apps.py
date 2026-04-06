from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    # Default field type for auto-generated primary keys.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'