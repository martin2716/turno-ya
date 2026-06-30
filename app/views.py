"""Vistas principales de la aplicación TurnoYa."""

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
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


# Paso de los turnos en minutos (cada cuánto se ofrece un horario).
PASO_TURNO_MIN = 30


def _slots_de_franja(fecha, hora_inicio, hora_fin, paso_min=PASO_TURNO_MIN):
    """Genera los datetime (aware) de cada turno posible dentro de una franja."""
    slots = []
    actual = datetime.combine(fecha, hora_inicio)
    fin = datetime.combine(fecha, hora_fin)
    while actual < fin:
        slots.append(timezone.make_aware(actual))
        actual += timedelta(minutes=paso_min)
    return slots


def slots_libres_de_medico(medico, fecha):
    """Devuelve los datetime libres de un médico en una fecha dada.

    Lee las franjas horarias del médico para el día de la semana de `fecha`
    y resta los turnos ya ocupados (pendientes o confirmados).
    """
    posibles = []
    for franja in medico.franjas.filter(dia_semana=fecha.weekday()):
        posibles.extend(_slots_de_franja(fecha, franja.hora_inicio, franja.hora_fin))

    if not posibles:
        return []

    ocupados = set(
        Turno.objects.filter(
            medico=medico,
            fecha_hora__date=fecha,
            estado__in=[Turno.PENDIENTE, Turno.CONFIRMADO],
        ).values_list("fecha_hora", flat=True)
    )
    return [slot for slot in posibles if slot not in ocupados]


class PerfilPacienteRequiredMixin(LoginRequiredMixin):
    """Redirige al usuario para completar su perfil antes de usar la app."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        if not Paciente.objects.filter(usuario=request.user).exists():
            return redirect("app:home")
        return super().dispatch(request, *args, **kwargs)


class HomeView(TemplateView):
    """Vista de inicio con estadísticas y acceso contextual según el usuario."""

    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()
        context["total_medicos"] = Medico.objects.count()
        context["total_especialidades"] = Especialidad.objects.count()
        context["total_usuarios"] = user_model.objects.count()
        context["medicos_inicio"] = Medico.objects.select_related("especialidad").all()

        if self.request.user.is_authenticated and not self.request.user.is_staff:
            paciente = Paciente.objects.filter(usuario=self.request.user).first()
            context["paciente_inicio"] = paciente
            context["mis_turnos_count"] = (
                Turno.objects.filter(paciente=paciente).count() if paciente else 0
            )
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


class ListaTurnosView(LoginRequiredMixin, ListView):
    """Lista los turnos visibles según el rol del usuario.

    - Admin/staff: ve todos.
    - Paciente: ve los turnos propios.
    - Médico: ve los turnos asignados a él.
    """

    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Turno.objects.all()

        paciente = Paciente.objects.filter(usuario=user).first()
        medico = Medico.objects.filter(usuario=user).first()

        queryset = Turno.objects.none()
        if paciente:
            queryset = queryset | Turno.objects.filter(paciente=paciente)
        if medico:
            queryset = queryset | Turno.objects.filter(medico=medico)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["es_medico"] = Medico.objects.filter(usuario=user).exists()
        context["mi_paciente_id"] = (
            Paciente.objects.filter(usuario=user).values_list("id", flat=True).first()
        )
        return context


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


class DetalleMedicoView(LoginRequiredMixin, DetailView):
    """Vista detallada de un médico: info personal, obras sociales y ausencias.

    Requiere login: según usabilidad.md solo el home y el listado de médicos
    son públicos; el detalle no.
    """

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


# ==================== FLUJO DE PEDIR TURNO ====================


class SeleccionarEspecialidadView(PerfilPacienteRequiredMixin, ListView):
    """Paso 1: el paciente elige una especialidad."""

    model = Especialidad
    template_name = "clinica/seleccionar_especialidad.html"
    context_object_name = "especialidades"
    ordering = ["nombre"]


class MedicosDisponiblesView(PerfilPacienteRequiredMixin, ListView):
    """Paso 2: médicos de la especialidad con horarios libres en una fecha."""

    model = Medico
    template_name = "clinica/medicos_disponibles.html"
    context_object_name = "medicos"

    def _fecha(self):
        fecha_str = self.request.GET.get("fecha")
        if fecha_str:
            try:
                return datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        return timezone.localdate()

    def get_queryset(self):
        especialidad_id = self.kwargs.get("especialidad_id")
        if not especialidad_id:
            return Medico.objects.none()
        fecha = self._fecha()
        medicos = Medico.objects.filter(especialidad_id=especialidad_id)
        return [m for m in medicos if slots_libres_de_medico(m, fecha)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["especialidad"] = get_object_or_404(
            Especialidad, id=self.kwargs.get("especialidad_id")
        )
        context["fecha"] = self._fecha().strftime("%Y-%m-%d")
        return context


class TurnosDisponiblesView(PerfilPacienteRequiredMixin, TemplateView):
    """Paso 3: horarios libres de un médico en una fecha."""

    template_name = "clinica/turnos_disponibles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico = get_object_or_404(Medico, id=self.kwargs.get("medico_id"))

        fecha_str = self.request.GET.get("fecha")
        fecha = timezone.localdate()
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        slots = slots_libres_de_medico(medico, fecha)
        context["medico"] = medico
        context["fecha"] = fecha
        context["fecha_str"] = fecha.strftime("%Y-%m-%d")
        context["turnos"] = [
            {"hora": s.strftime("%H:%M"), "datetime": s} for s in slots
        ]
        return context


class ConfirmarTurnoView(PerfilPacienteRequiredMixin, CreateView):
    """Paso 4: confirma y crea el turno.

    El chequeo de 'usuario sin perfil de paciente' lo hace
    PerfilPacienteRequiredMixin (en main), no este método.
    """

    model = Turno
    template_name = "clinica/confirmar_turno.html"
    fields = ["motivo", "observaciones"]
    success_url = reverse_lazy("app:lista_turnos")

    def _fecha_hora(self):
        naive = datetime.strptime(
            f"{self.kwargs['fecha']} {self.kwargs['hora']}", "%Y-%m-%d %H:%M"
        )
        return timezone.make_aware(naive)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["medico"] = get_object_or_404(Medico, id=self.kwargs.get("medico_id"))
        context["fecha_hora"] = self._fecha_hora()
        context["es_admin"] = self.request.user.is_staff
        if self.request.user.is_staff:
            context["pacientes"] = Paciente.objects.all().order_by("apellido", "nombre")
        else:
            context["paciente"] = Paciente.objects.get(usuario=self.request.user)
        return context

    def form_valid(self, form):
        medico = get_object_or_404(Medico, id=self.kwargs.get("medico_id"))

        if self.request.user.is_staff:
            paciente_id = self.request.POST.get("paciente_id")
            if not paciente_id:
                form.add_error(None, "Debés seleccionar un paciente de la lista.")
                return self.form_invalid(form)
            paciente = get_object_or_404(Paciente, id=paciente_id)
        else:
            paciente = Paciente.objects.get(usuario=self.request.user)

        turno, errors = Turno.new(
            medico=medico,
            paciente=paciente,
            fecha_hora=self._fecha_hora(),
            motivo=form.cleaned_data["motivo"],
            observaciones=form.cleaned_data.get("observaciones", ""),
            creado_por=self.request.user,
        )
        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Turno solicitado con {medico} para el "
            f"{self._fecha_hora():%d/%m/%Y %H:%M}.",
        )
        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class AceptarTurnoView(LoginRequiredMixin, View):
    """El médico asignado (o staff) confirma un turno pendiente. Solo POST."""

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)
        if not (request.user.is_staff or turno.medico.usuario_id == request.user.id):
            messages.error(request, "Solo el médico asignado puede aceptar este turno.")
            return redirect("app:lista_turnos")
        if turno.estado != Turno.PENDIENTE:
            messages.error(request, "Solo se pueden aceptar turnos pendientes.")
            return redirect("app:lista_turnos")
        turno.aceptar()
        messages.success(request, "Turno aceptado.")
        return redirect("app:lista_turnos")


class RechazarTurnoView(LoginRequiredMixin, View):
    """El médico asignado (o staff) rechaza un turno pendiente. Solo POST.

    Reutiliza la transición a 'cancelado' (Turno.rechazar()).
    """

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)
        if not (request.user.is_staff or turno.medico.usuario_id == request.user.id):
            messages.error(
                request, "Solo el médico asignado puede rechazar este turno."
            )
            return redirect("app:lista_turnos")
        if turno.estado != Turno.PENDIENTE:
            messages.error(request, "Solo se pueden rechazar turnos pendientes.")
            return redirect("app:lista_turnos")
        turno.rechazar()
        messages.success(request, "Turno rechazado.")
        return redirect("app:lista_turnos")


class CancelarTurnoView(LoginRequiredMixin, TemplateView):
    """El paciente (o staff) cancela un turno. GET confirma, POST cancela."""

    template_name = "clinica/confirmar_cancelacion.html"

    def _turno_si_permitido(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk)
        es_paciente = Paciente.objects.filter(
            usuario=request.user, pk=turno.paciente_id
        ).exists()
        if not (request.user.is_staff or es_paciente):
            return None
        return turno

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["turno"] = get_object_or_404(Turno, pk=self.kwargs["pk"])
        return context

    def get(self, request, *args, **kwargs):
        turno = self._turno_si_permitido(request, kwargs["pk"])
        if turno is None:
            messages.error(request, "No podés cancelar este turno.")
            return redirect("app:lista_turnos")
        if turno.estado in [Turno.CANCELADO, Turno.FINALIZADO]:
            messages.error(request, "Este turno no se puede cancelar.")
            return redirect("app:lista_turnos")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        turno = self._turno_si_permitido(request, kwargs["pk"])
        if turno is None:
            messages.error(request, "No podés cancelar este turno.")
            return redirect("app:lista_turnos")
        if turno.estado in [Turno.CANCELADO, Turno.FINALIZADO]:
            messages.error(request, "Este turno no se puede cancelar.")
            return redirect("app:lista_turnos")
        turno.cancelar()
        messages.success(request, "Turno cancelado.")
        return redirect("app:lista_turnos")
