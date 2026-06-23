from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
# Importamos nuestros modelos para asociar los permisos
from app.models import Turno, Paciente, Medico, Especialidad, ObraSocial

class Command(BaseCommand):
    help = 'Crea grupos y asigna permisos predefinidos'

    def handle(self, *args, **options):
        # 1. Definimos los grupos que existirán en el sistema
        grupos_definidos = ['Pacientes', 'Médicos', 'Administrativos']
        
        for nombre in grupos_definidos:
            # get_or_create: Si el grupo existe, lo obtiene; si no, lo crea.
            grupo, created = Group.objects.get_or_create(name=nombre)
            if created:
                self.stdout.write(f'Grupo "{nombre}" creado con éxito.')
            else:
                self.stdout.write(f'Grupo "{nombre}" ya existía.')

        # 2. Función auxiliar para asignar permisos de forma rápida
        def asignar_permiso(grupo_obj, modelo, accion):
            # ContentType identifica el modelo en la base de datos de Django
            ct = ContentType.objects.get_for_model(modelo)
            # Buscamos el permiso específico (ej: 'add_turno')
            permiso = Permission.objects.get(codename=f'{accion}_{modelo._meta.model_name}', content_type=ct)
            grupo_obj.permissions.add(permiso)

        # 3. Asignación de permisos para PACIENTES
        grupo_pac = Group.objects.get(name='Pacientes')
        asignar_permiso(grupo_pac, Turno, 'view')
        asignar_permiso(grupo_pac, Turno, 'add')

        # 4. Asignación de permisos para MÉDICOS
        grupo_med = Group.objects.get(name='Médicos')
        asignar_permiso(grupo_med, Turno, 'view')
        asignar_permiso(grupo_med, Turno, 'change')
        asignar_permiso(grupo_med, Paciente, 'view')

        # 5. Asignación de permisos para ADMINISTRATIVOS
        # Tienen acceso total a los modelos principales
        grupo_adm = Group.objects.get(name='Administrativos')
        for modelo in [Turno, Paciente, Medico, Especialidad, ObraSocial]:
            for accion in ['add', 'change', 'delete', 'view']:
                asignar_permiso(grupo_adm, modelo, accion)

        self.stdout.write(self.style.SUCCESS('¡Configuración de grupos y permisos completada!'))