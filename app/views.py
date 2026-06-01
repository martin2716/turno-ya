"""Vistas iniciales para navegar médicos y pantalla de inicio."""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import ListView, TemplateView
from .models import Especialidad, Medico


class HomeView(TemplateView):
    """Vista de inicio. Por ahora vacía — completar con estadísticas."""

    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()
        context["total_medicos"] = Medico.objects.count()
        context["total_especialidades"] = Especialidad.objects.count()
        context["total_usuarios"] = user_model.objects.count()
        return context


class ListaMedicosView(ListView):
    """Lista todos los médicos."""

    model = Medico
    template_name = "clinica/lista_medicos.html"
    context_object_name = "medicos"


class RegistroUsuarioView(CreateView):
    """Base comun para registro de usuarios del proyecto."""

    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


# Etapa intermedia y final: completar estas vistas unicamente como CBV.
# Martin: HomeView y coordinación técnica.
# Maxi: filtro/listado de médicos y parte de auth.
# Misael: turnos.
# Dario: detalle de médico, templates y UX.
#
# TODO: implementar las siguientes vistas:
# class DetalleMedicoView(...): ...
# class ListaTurnosView(...): ...
# class NuevoTurnoView(...): ...
# class CancelarTurnoView(...): ...
# class ListaPacientesView(...): ...
