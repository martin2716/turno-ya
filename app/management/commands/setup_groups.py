from django.core.management.base import BaseCommand
from app.groups import configurar_grupos_y_permisos


class Command(BaseCommand):
    help = 'Crea grupos y asigna permisos predefinidos'

    def handle(self, *args, **options):
        configurar_grupos_y_permisos(stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS('¡Configuración de grupos y permisos completada!'))
