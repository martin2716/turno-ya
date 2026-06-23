"""Configuración básica del admin para los modelos de la app."""

from django.contrib import admin
from .models import Especialidad, Medico, Paciente, Turno, ObraSocial


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "matricula", "especialidad")
    list_filter = ("especialidad",)
    search_fields = ("apellido", "nombre", "matricula")

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "dni", "obra_social")
    search_fields = ("apellido", "nombre", "dni")

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ("medico", "paciente_apellido", "fecha", "disponibilidad")
    list_filter = ("fecha", "disponibilidad")

@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)
