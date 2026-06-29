"""Rutas públicas de la aplicación principal."""

from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("medicos/", views.ListaMedicosView.as_view(), name="lista_medicos"),
    path("accounts/registro/", views.RegistroUsuarioView.as_view(), name="registro"),
    path("pacientes/", views.ListaPacientesView.as_view(), name="lista_pacientes"),
    path("turnos/nuevo/", views.NuevoTurnoView.as_view(), name="nuevo_turno"),
    path("turnos/<int:pk>/aceptar/", views.AceptarTurnoView.as_view(), name="aceptar_turno"),
    # TODO:
    # path("medicos/<int:pk>/", views.DetalleMedicoView.as_view(), name="detalle_medico"),
    path("turnos/", views.ListaTurnosView.as_view(), name="lista_turnos"),
    # path("turnos/nuevo/", views.NuevoTurnoView.as_view(), name="nuevo_turno"),
    path("turnos/<int:pk>/cancelar/", views.CancelarTurnoView.as_view(), name="cancelar_turno"),
        # NUEVO FLUJO DE TURNOS - Selección por especialidad
    path("especialidades/", views.SeleccionarEspecialidadView.as_view(), name="seleccionar_especialidad"),
    path("especialidad/<int:especialidad_id>/medicos/", views.MedicosDisponiblesView.as_view(), name="medicos_disponibles"),
    path("turno/confirmar/<int:medico_id>/<str:fecha>/<str:hora>/", views.ConfirmarTurnoView.as_view(), name="confirmar_turno"),
    path("medico/<int:medico_id>/turnos/", views.TurnosDisponiblesView.as_view(), name="turnos_disponibles"),
    path("buscar-pacientes/", views.BuscarPacientesView.as_view(), name="buscar_pacientes"),
]
"#"  
