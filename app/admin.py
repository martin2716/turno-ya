"""Configuración básica del admin para los modelos de la app."""

from django.contrib import admin
from .models import Especialidad, Medico


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "matricula", "especialidad")
    list_filter = ("especialidad",)
    search_fields = ("apellido", "nombre", "matricula")
