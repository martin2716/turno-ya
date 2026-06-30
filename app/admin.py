"""Configuración del admin para los modelos principales de la app."""

from django.contrib import admin
from .models import (
    Especialidad,
    Medico,
    FranjaHoraria,
    ObraSocial,
    Paciente,
    Turno,
    Ausencia,
)

admin.site.site_header = "TurnoYa Administración"
admin.site.site_title = "TurnoYa Admin"
admin.site.index_title = "Gestión interna del sistema"


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "matricula", "especialidad", "usuario")
    list_filter = ("especialidad",)
    search_fields = ("apellido", "nombre", "matricula")


@admin.register(FranjaHoraria)
class FranjaHorariaAdmin(admin.ModelAdmin):
    list_display = ("medico", "dia_semana", "hora_inicio", "hora_fin")
    list_filter = ("dia_semana", "medico")
    search_fields = ("medico__apellido", "medico__nombre")


@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ("nombre", "requiere_token", "medicos_disponibles")
    list_filter = ("requiere_token",)
    search_fields = ("nombre", "sitio_web")


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "dni", "email", "obra_social")
    list_filter = ("obra_social",)
    search_fields = ("apellido", "nombre", "dni", "email")


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (
        "fecha_hora",
        "medico",
        "paciente",
        "estado",
        "motivo",
    )
    list_filter = ("estado", "medico")
    search_fields = (
        "paciente__apellido",
        "paciente__nombre",
        "medico__apellido",
        "medico__nombre",
    )
    date_hierarchy = "fecha_hora"


@admin.register(Ausencia)
class AusenciaAdmin(admin.ModelAdmin):
    list_display = ("medico", "motivo", "fecha_inicio", "fecha_fin")
    list_filter = ("medico", "fecha_inicio", "fecha_fin")
    search_fields = ("medico__apellido", "medico__nombre", "motivo")
