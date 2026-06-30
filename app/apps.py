"""Configuración de Django para la aplicación principal."""

from django.apps import AppConfig as DjangoAppConfig
from django.db.models.signals import post_migrate


def _configurar_grupos(sender, **kwargs):
    """Recibe post_migrate y crea grupos/permisos. Solo para esta app."""
    # `sender` es el AppConfig de la app que terminó de migrar; nos limitamos
    # a la nuestra para no correr la lógica una vez por cada app instalada.
    if sender is None or sender.name != 'app':
        return
    from app.groups import configurar_grupos_y_permisos
    configurar_grupos_y_permisos()


class AppConfig(DjangoAppConfig):
    """Define el nombre interno y el nombre visible de la app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = "Clínica"

    def ready(self):
        # Al correr `migrate`, los permisos por defecto ya fueron creados por
        # django.contrib.auth (su handler de post_migrate corre antes), así que
        # acá los grupos pueden referenciarlos sin problemas.
        post_migrate.connect(_configurar_grupos, sender=self)
