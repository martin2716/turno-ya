"""Vistas principales de la aplicación TurnoYa."""

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    TemplateView,
    DetailView,
    UpdateView,
)

from .forms import AusenciaForm, PerfilUsuarioForm, RegistroPacienteForm
from .models import Especialidad, Medico, Paciente, Turno, Ausencia


class PerfilPacienteRequiredMixin(LoginRequiredMixin):
    """Redirige al usuario para completar su perfil antes de usar la app."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        if not Paciente.objects.filter(usuario=request.user).exists():
            return redirect("app:crear_perfil")
        return super().dispatch(request, *args, **kwargs)


class HomeView(TemplateView):
    """Vista de inicio con estadísticas generales."""

    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()
        context["total_medicos"] = Medico.objects.count()
        context["total_especialidades"] = Especialidad.objects.count()
        context["total_usuarios"] = user_model.objects.count()
        return context


class ListaMedicosView(ListView):
    """Lista todos los médicos, con filtro opcional por especialidad."""

    model = Medico
    template_name = "clinica/lista_medicos.html"
    context_object_name = "medicos"

    def get_queryset(self):
        queryset = super().get_queryset()
        especialidad_id = self.request.GET.get("especialidad")

        if especialidad_id:
            queryset = queryset.filter(especialidad_id=especialidad_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["especialidades"] = Especialidad.objects.all()
        return context


class ListaTurnosView(PermissionRequiredMixin, ListView):
    """Lista todos los turnos."""

    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"
    permission_required = "app.view_turno"

    def handle_no_permission(self):
        return redirect("app:home")


class RegistroUsuarioView(FormView):
    """Registro de paciente: crea el User y el Paciente en un único paso."""

    form_class = RegistroPacienteForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        Paciente.new(
            usuario=user,
            nombre=form.cleaned_data["first_name"],
            apellido=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"],
            telefono=form.cleaned_data["telefono"],
            dni=form.cleaned_data["dni"],
            obra_social=form.cleaned_data["obra_social"],
        )
        return super().form_valid(form)


class ListaPacientesView(PermissionRequiredMixin, ListView):
    """Lista todos los pacientes."""

    model = Paciente
    template_name = "clinica/lista_pacientes.html"
    context_object_name = "pacientes"
    permission_required = "app.view_paciente"

    def handle_no_permission(self):
        return redirect("app:home")


class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    model = Paciente
    fields = ["nombre", "apellido", "telefono", "obra_social"]
    template_name = "clinica/perfil_form.html"
    success_url = reverse_lazy("app:home")

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "paciente") and not request.user.is_staff:
            return redirect("app:crear_perfil")

        if request.user.is_staff:
            return redirect("app:home")

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user.paciente


class PerfilCreateView(LoginRequiredMixin, CreateView):
    model = Paciente
    fields = ["nombre", "apellido", "email", "telefono", "dni", "obra_social"]
    template_name = "clinica/perfil_form.html"
    success_url = reverse_lazy("app:home")

    def form_valid(self, form):
        paciente, errors = Paciente.new(
            usuario=self.request.user,
            nombre=form.cleaned_data["nombre"],
            apellido=form.cleaned_data["apellido"],
            email=form.cleaned_data["email"],
            telefono=form.cleaned_data["telefono"],
            dni=form.cleaned_data["dni"],
            obra_social=form.cleaned_data["obra_social"],
        )

        if errors:
            form.add_error(None, errors)
            return self.form_invalid(form)

        return redirect(self.success_url)



class ListaAusenciasView(PermissionRequiredMixin, ListView):
    """Lista todas las ausencias registradas."""

    model = Ausencia
    template_name = "clinica/lista_ausencias.html"
    context_object_name = "ausencias"
    permission_required = "app.view_ausencia"

    def handle_no_permission(self):
        return redirect("app:home")


class NuevaAusenciaView(PermissionRequiredMixin, CreateView):
    """Permite al personal registrar una ausencia de un médico."""

    model = Ausencia
    form_class = AusenciaForm
    template_name = "clinica/nueva_ausencia.html"
    success_url = reverse_lazy("app:lista_ausencias")
    permission_required = "app.add_ausencia"

    def handle_no_permission(self):
        return redirect("app:home")

    def form_valid(self, form):
        ausencia, errors = Ausencia.new(
            motivo=form.cleaned_data["motivo"],
            fecha_inicio=form.cleaned_data["fecha_inicio"],
            fecha_fin=form.cleaned_data["fecha_fin"],
            medico=form.cleaned_data["medico"],
        )
        if errors:
            form.add_error(None, errors)
            return self.form_invalid(form)
        messages.success(self.request, "Ausencia registrada correctamente.")
        return redirect(self.success_url)


class DetalleMedicoView(DetailView):
    """Vista detallada de un médico: info personal, obras sociales y ausencias."""

    model = Medico
    template_name = "clinica/detalle_medico.html"
    context_object_name = "medico"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ausencias"] = self.object.ausencias.order_by("fecha_inicio")
        context["obras_sociales"] = self.object.obras_sociales.all()
        return context

class PerfilUsuarioView(LoginRequiredMixin, FormView):
    """Alta y edición resumida del perfil de paciente."""

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


# TODO: implementar las siguientes vistas:
# class DetalleMedicoView(...): ...
# class NuevoTurnoView(...): ...
# class CancelarTurnoView(...): ...
