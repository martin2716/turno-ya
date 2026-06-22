"""Vistas principales de la aplicación TurnoYa."""

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView, TemplateView

from .forms import PerfilUsuarioForm, RegistroUsuarioForm
from .models import Especialidad, Medico, Paciente, Turno


class PerfilPacienteRequiredMixin(LoginRequiredMixin):
    """Redirige al usuario para completar su perfil antes de usar la app."""

    def dispatch(self, request, *args, **kwargs):
        if not Paciente.objects.filter(usuario=request.user).exists():
            return redirect("app:perfil_usuario")
        return super().dispatch(request, *args, **kwargs)


class HomeView(PerfilPacienteRequiredMixin, TemplateView):
    """Vista de inicio con estadísticas generales."""

    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()
        context["total_medicos"] = Medico.objects.count()
        context["total_especialidades"] = Especialidad.objects.count()
        context["total_usuarios"] = user_model.objects.count()
        return context


class ListaMedicosView(PerfilPacienteRequiredMixin, ListView):
    """Lista todos los médicos."""

    model = Medico
    template_name = "clinica/lista_medicos.html"
    context_object_name = "medicos"


class ListaTurnosView(PerfilPacienteRequiredMixin, ListView):
    """Lista todos los turnos."""

    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"


class RegistroUsuarioView(CreateView):
    """Registro inicial de usuarios."""

    form_class = RegistroUsuarioForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


class ListaPacientesView(PerfilPacienteRequiredMixin, ListView):
    """Lista todos los pacientes."""

    model = Paciente
    template_name = "clinica/lista_pacientes.html"
    context_object_name = "pacientes"


class PerfilUsuarioView(LoginRequiredMixin, FormView):
    """Alta y edición obligatoria del perfil de paciente."""

    form_class = PerfilUsuarioForm
    template_name = "clinica/perfil_usuario.html"
    success_url = reverse_lazy("app:home")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["paciente"] = Paciente.objects.filter(usuario=self.request.user).first()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["perfil_completo"] = Paciente.objects.filter(
            usuario=self.request.user
        ).exists()
        return context

    def form_valid(self, form):
        user = self.request.user
        paciente = Paciente.objects.filter(usuario=user).first()

        user.first_name = form.cleaned_data["first_name"].strip()
        user.last_name = form.cleaned_data["last_name"].strip()
        user.email = form.cleaned_data["email"]
        user.save()

        if paciente is None:
            Paciente.new(
                usuario=user,
                nombre=form.cleaned_data["first_name"],
                apellido=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                telefono=form.cleaned_data["telefono"],
                dni=form.cleaned_data["dni"],
                obra_social=form.cleaned_data["obra_social"],
            )
        else:
            paciente.update(
                nombre=form.cleaned_data["first_name"],
                apellido=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                telefono=form.cleaned_data["telefono"],
                dni=form.cleaned_data["dni"],
                obra_social=form.cleaned_data["obra_social"],
            )

        return super().form_valid(form)


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
