"""Configuración del admin para los modelos principales de la app."""

from django.contrib import admin
from .models import Especialidad, Medico, ObraSocial, Paciente, Turno, Ausencia


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "matricula", "especialidad")
    list_filter = ("especialidad",)
    search_fields = ("apellido", "nombre", "matricula")


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
        "fecha",
        "medico",
        "paciente_apellido",
        "paciente_nombre",
        "disponibilidad",
    )
    list_filter = ("disponibilidad", "medico")
    search_fields = (
        "paciente_apellido",
        "paciente_nombre",
        "medico__apellido",
        "medico__nombre",
    )
    date_hierarchy = "fecha"


@admin.register(Ausencia)
class AusenciaAdmin(admin.ModelAdmin):
    list_display = ("medico", "motivo", "fecha_inicio", "fecha_fin")
    list_filter = ("medico", "fecha_inicio", "fecha_fin")
    search_fields = ("medico__apellido", "medico__nombre", "motivo")
