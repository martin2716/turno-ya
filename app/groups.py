"""Definición de grupos y permisos del sistema.

Lógica compartida entre el comando `setup_groups` y la señal `post_migrate`
(ver `apps.py`), para que los grupos existan automáticamente al correr `migrate`.
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def configurar_grupos_y_permisos(stdout=None):
    """Crea los grupos y les asigna sus permisos. Idempotente.

    Si se pasa `stdout` (el del comando), informa el progreso por ahí.
    """
    # Import diferido: al correr como señal post_migrate los modelos ya están
    # cargados, pero importarlos a nivel de módulo puede adelantarse al registro.
    from app.models import Turno, Paciente, Medico, Especialidad, ObraSocial, Ausencia

    def log(msg):
        if stdout is not None:
            stdout.write(msg)

    grupos_definidos = ['Pacientes', 'Médicos', 'Administrativos']
    for nombre in grupos_definidos:
        grupo, created = Group.objects.get_or_create(name=nombre)
        log(f'Grupo "{nombre}" {"creado" if created else "ya existía"}.')

    def asignar_permiso(grupo_obj, modelo, accion):
        ct = ContentType.objects.get_for_model(modelo)
        permiso = Permission.objects.get(
            codename=f'{accion}_{modelo._meta.model_name}', content_type=ct
        )
        grupo_obj.permissions.add(permiso)

    # Pacientes
    grupo_pac = Group.objects.get(name='Pacientes')
    asignar_permiso(grupo_pac, Turno, 'view')
    asignar_permiso(grupo_pac, Turno, 'add')

    # Médicos
    grupo_med = Group.objects.get(name='Médicos')
    asignar_permiso(grupo_med, Turno, 'view')
    asignar_permiso(grupo_med, Turno, 'change')
    asignar_permiso(grupo_med, Paciente, 'view')
    asignar_permiso(grupo_med, Ausencia, 'view')
    asignar_permiso(grupo_med, Ausencia, 'add')
    asignar_permiso(grupo_med, Ausencia, 'delete')

    # Administrativos: acceso total a los modelos principales
    grupo_adm = Group.objects.get(name='Administrativos')
    for modelo in [Turno, Paciente, Medico, Especialidad, ObraSocial, Ausencia]:
        for accion in ['add', 'change', 'delete', 'view']:
            asignar_permiso(grupo_adm, modelo, accion)
