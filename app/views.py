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

    Lee las franjas horarias del médico para el día de la semana de `fecha`,
    descarta si el médico tiene una ausencia que cubra esa fecha
    y resta los turnos ya ocupados (pendientes o confirmados).
    """
    # Si el médico tiene ausencia ese día, no hay slots disponibles
    if medico.ausencias.filter(
        fecha_inicio__lte=fecha,
        fecha_fin__gte=fecha,
    ).exists():
        return []

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
    """Lista de ausencias.

    El staff ve todas; un médico ve únicamente las suyas.
    """

    model = Ausencia
    template_name = "clinica/lista_ausencias.html"
    context_object_name = "ausencias"
    permission_required = "app.view_ausencia"

    def handle_no_permission(self):
        return redirect("app:home")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        medico = Medico.objects.filter(usuario=self.request.user).first()
        if medico is None:
            return qs.none()
        return qs.filter(medico=medico)


class NuevaAusenciaView(PermissionRequiredMixin, CreateView):
    """Permite al personal registrar una ausencia de un médico."""

    model = Ausencia
    form_class = AusenciaForm
    template_name = "clinica/nueva_ausencia.html"
    success_url = reverse_lazy("app:lista_ausencias")
    permission_required = "app.add_ausencia"

    def handle_no_permission(self):
        return redirect("app:home")

    def _medico_actual(self):
        return Medico.objects.filter(usuario=self.request.user).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Para el médico, mostramos su nombre como dato de solo lectura
        # (el selector editable es exclusivo del staff).
        if not self.request.user.is_staff:
            context["medico_actual"] = self._medico_actual()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # El médico no elige: la ausencia es siempre suya. Solo el staff puede
        # registrar la de cualquier médico, así que para el médico ocultamos
        # el selector.
        if not self.request.user.is_staff:
            form.fields.pop("medico", None)
        return form

    def form_valid(self, form):
        if self.request.user.is_staff:
            medico = form.cleaned_data["medico"]
        else:
            medico = self._medico_actual()
            if medico is None:
                form.add_error(None, "Tu usuario no está vinculado a un médico.")
                return self.form_invalid(form)
        ausencia, errors = Ausencia.new(
            motivo=form.cleaned_data["motivo"],
            fecha_inicio=form.cleaned_data["fecha_inicio"],
            fecha_fin=form.cleaned_data["fecha_fin"],
            medico=medico,
        )
        if errors:
            form.add_error(None, errors)
            return self.form_invalid(form)
        messages.success(self.request, "Ausencia registrada correctamente.")
        return redirect(self.success_url)


class EliminarAusenciaView(PermissionRequiredMixin, TemplateView):
    """Elimina una ausencia. GET confirma, POST elimina.

    El médico solo puede eliminar sus propias ausencias; el staff, cualquiera.
    """

    template_name = "clinica/confirmar_eliminacion_ausencia.html"
    permission_required = "app.delete_ausencia"

    def handle_no_permission(self):
        return redirect("app:home")

    def _ausencia_si_permitido(self, request, pk):
        ausencia = get_object_or_404(Ausencia, pk=pk)
        if not (request.user.is_staff or ausencia.medico.usuario_id == request.user.id):
            return None
        return ausencia

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ausencia"] = get_object_or_404(Ausencia, pk=self.kwargs["pk"])
        return context

    def get(self, request, *args, **kwargs):
        ausencia = self._ausencia_si_permitido(request, kwargs["pk"])
        if ausencia is None:
            messages.error(request, "No podés eliminar esta ausencia.")
            return redirect("app:lista_ausencias")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ausencia = self._ausencia_si_permitido(request, kwargs["pk"])
        if ausencia is None:
            messages.error(request, "No podés eliminar esta ausencia.")
            return redirect("app:lista_ausencias")
        ausencia.delete()
        messages.success(request, "Ausencia eliminada correctamente.")
        return redirect("app:lista_ausencias")


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
    """Paso 2: médicos de la especialidad con al menos un turno libre en 15 días."""

    model = Medico
    template_name = "clinica/medicos_disponibles.html"
    context_object_name = "medicos"

    def get_queryset(self):
        especialidad_id = self.kwargs.get("especialidad_id")
        if not especialidad_id:
            return Medico.objects.none()
        hoy = timezone.localdate()
        ahora = timezone.now()
        medicos = Medico.objects.filter(especialidad_id=especialidad_id)
        disponibles = []
        for medico in medicos:
            tiene_disponibilidad = False
            for i in range(DIAS_CALENDARIO + 1):
                fecha = hoy + timedelta(days=i)
                slots = slots_libres_de_medico(medico, fecha)
                if fecha == hoy:
                    slots = [s for s in slots if s > ahora]
                if slots:
                    tiene_disponibilidad = True
                    break
            if tiene_disponibilidad:
                disponibles.append(medico)
        return disponibles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["especialidad"] = get_object_or_404(
            Especialidad, id=self.kwargs.get("especialidad_id")
        )
        context["dias_calendario"] = DIAS_CALENDARIO
        return context


DIAS_CALENDARIO = 15

NOMBRES_DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
NOMBRES_MESES_ES = [
    "",
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
]


class TurnosDisponiblesView(PerfilPacienteRequiredMixin, TemplateView):
    """Paso 3: calendario de 15 días o lista de horarios según si hay fecha seleccionada.

    Sin fecha en GET: muestra el calendario con los días que tienen turnos libres.
    Con fecha en GET: muestra los horarios disponibles de ese día, filtrando pasados.
    """

    template_name = "clinica/turnos_disponibles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico = get_object_or_404(Medico, id=self.kwargs.get("medico_id"))
        hoy = timezone.localdate()
        ahora = timezone.now()

        fecha_str = self.request.GET.get("fecha")
        fecha_elegida = None

        if fecha_str:
            try:
                parsed = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                if hoy <= parsed <= hoy + timedelta(days=DIAS_CALENDARIO):
                    fecha_elegida = parsed
            except ValueError:
                pass

        context["medico"] = medico

        if fecha_elegida:
            # Mostrar horarios del día elegido, filtrando slots pasados
            slots = slots_libres_de_medico(medico, fecha_elegida)
            slots_futuros = [s for s in slots if s > ahora]
            context["modo"] = "horarios"
            context["fecha"] = fecha_elegida
            context["fecha_str"] = fecha_elegida.strftime("%Y-%m-%d")
            context["turnos"] = [
                {"hora": s.strftime("%H:%M"), "datetime": s} for s in slots_futuros
            ]
        else:
            # Mostrar calendario: calcular cuáles días tienen turnos disponibles
            dias = []
            for i in range(DIAS_CALENDARIO + 1):
                dia = hoy + timedelta(days=i)
                slots = slots_libres_de_medico(medico, dia)
                # Para hoy, solo slots futuros
                if dia == hoy:
                    slots = [s for s in slots if s > ahora]
                dias.append(
                    {
                        "fecha": dia,
                        "fecha_str": dia.strftime("%Y-%m-%d"),
                        "nombre_dia": f"{NOMBRES_DIAS_ES[dia.weekday()]} {dia.day:02d}/{dia.month:02d}",
                        "disponible": len(slots) > 0,
                        "cantidad": len(slots),
                    }
                )
            context["modo"] = "calendario"
            context["dias"] = dias
            context["hoy"] = hoy

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
