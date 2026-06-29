"""vistas iniciales para navegar medicos y pantalla de inicio."""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView
from .models import Especialidad, Medico, Turno, Paciente

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import TurnoForm, BusquedaTurnosForm
from django.shortcuts import redirect


class HomeView(TemplateView):
    """vista de inicio. por ahora vacia - completar con estadisticas."""

    template_name = "clinica/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()
        context["total_medicos"] = Medico.objects.count()
        context["total_especialidades"] = Especialidad.objects.count()
        context["total_usuarios"] = user_model.objects.count()
        return context


class ListaMedicosView(ListView):
    """lista todos los medicos."""

    model = Medico
    template_name = "clinica/lista_medicos.html"
    context_object_name = "medicos"


class RegistroUsuarioView(CreateView):
    """base comun para registro de usuarios del proyecto."""

    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


class ListaPacientesView(ListView):
    """lista todos los pacientes."""

    model = Paciente
    template_name = "clinica/lista_pacientes.html"
    context_object_name = "pacientes"


class SeleccionarEspecialidadView(LoginRequiredMixin, ListView):
    """vista para mostrar todas las especialidades y elegir una."""
    model = Especialidad
    template_name = 'clinica/seleccionar_especialidad.html'
    context_object_name = 'especialidades'
    ordering = ['nombre']


class NuevoTurnoView(LoginRequiredMixin, CreateView):
    """
    vista para que un usuario autenticado pueda crear un nuevo turno.
    """
    model = Turno
    form_class = TurnoForm
    template_name = 'clinica/form_turno.html'
    success_url = reverse_lazy('app:lista_turnos')

    def form_valid(self, form):
        """asigna el usuario actual como creador y guarda."""
        form.instance.creado_por = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"turno creado exitosamente para {form.instance.paciente} con {form.instance.medico}!"
        )
        return response

    def form_invalid(self, form):
        """muestra mensaje de error si el formulario no es valido."""
        messages.error(
            self.request,
            "error al crear el turno. por favor, corrige los errores del formulario."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'nuevo turno'
        context['boton_texto'] = 'solicitar turno'
        return context


class MedicosDisponiblesView(LoginRequiredMixin, ListView):
    """vista para listar medicos filtrados por especialidad con turnos disponibles."""
    model = Medico
    template_name = 'clinica/medicos_disponibles.html'
    context_object_name = 'medicos'

    def get_queryset(self):
        especialidad_id = self.kwargs.get('especialidad_id')

        if not especialidad_id:
            return Medico.objects.none()

        # obtener fecha (hoy por defecto)
        fecha_str = self.request.GET.get('fecha')
        fecha = None
        if fecha_str:
            from datetime import datetime
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                fecha = None

        if not fecha:
            from django.utils import timezone
            fecha = timezone.now().date()

        # filtrar medicos por especialidad
        medicos = Medico.objects.filter(especialidad_id=especialidad_id)

        # filtrar solo los que tienen turnos disponibles
        medicos_disponibles = []
        for medico in medicos:
            if self._medico_tiene_turnos_disponibles(medico, fecha):
                medicos_disponibles.append(medico)

        return medicos_disponibles

    def _medico_tiene_turnos_disponibles(self, medico, fecha):
        from datetime import datetime, timedelta

        hora_inicio = medico.hora_inicio
        hora_fin = medico.hora_fin

        # generar todos los turnos posibles en la franja horaria (30 min)
        turnos_posibles = []
        hora_actual = datetime.combine(fecha, hora_inicio)
        hora_fin_dt = datetime.combine(fecha, hora_fin)

        while hora_actual < hora_fin_dt:
            turnos_posibles.append(hora_actual)
            hora_actual += timedelta(minutes=30)

        # turnos ocupados
        turnos_ocupados = Turno.objects.filter(
            medico=medico,
            fecha_hora__date=fecha,
            estado__in=['confirmado', 'pendiente']
        ).values_list('fecha_hora', flat=True)

        # si hay al menos un turno disponible
        for turno in turnos_posibles:
            if turno not in turnos_ocupados:
                return True

        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['especialidad_id'] = self.kwargs.get('especialidad_id')
        try:
            context['especialidad'] = Especialidad.objects.get(id=self.kwargs.get('especialidad_id'))
        except Especialidad.DoesNotExist:
            context['especialidad'] = None
        context['fecha'] = self.request.GET.get('fecha')
        return context


class TurnosDisponiblesView(LoginRequiredMixin, TemplateView):
    """vista para mostrar los turnos disponibles de un medico."""
    template_name = 'clinica/turnos_disponibles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id = self.kwargs.get('medico_id')

        medico = Medico.objects.get(id=medico_id)
        context['medico'] = medico

        fecha_str = self.request.GET.get('fecha')
        if fecha_str:
            from datetime import datetime
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        else:
            from django.utils import timezone
            fecha = timezone.now().date()

        context['fecha'] = fecha
        context['fecha_str'] = fecha.strftime('%Y-%m-%d')

        from datetime import datetime, timedelta
        hora_inicio = medico.hora_inicio
        hora_fin = medico.hora_fin

        turnos_posibles = []
        hora_actual = datetime.combine(fecha, hora_inicio)
        hora_fin_dt = datetime.combine(fecha, hora_fin)

        while hora_actual < hora_fin_dt:
            turnos_posibles.append(hora_actual)
            hora_actual += timedelta(minutes=30)

        turnos_ocupados = Turno.objects.filter(
            medico=medico,
            fecha_hora__date=fecha,
            estado__in=['confirmado', 'pendiente']
        ).values_list('fecha_hora', flat=True)

        turnos_libres = [t for t in turnos_posibles if t not in turnos_ocupados]

        turnos_data = []
        for turno in turnos_libres:
            turnos_data.append({
                'hora': turno.strftime('%H:%M'),
                'datetime': turno,
            })

        context['turnos'] = turnos_data
        return context


class ConfirmarTurnoView(LoginRequiredMixin, CreateView):
    """vista para confirmar el turno."""
    model = Turno
    template_name = 'clinica/confirmar_turno.html'
    fields = ['motivo', 'observaciones']
    success_url = reverse_lazy('app:lista_turnos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id = self.kwargs.get('medico_id')
        fecha_str = self.kwargs.get('fecha')
        hora_str = self.kwargs.get('hora')
        from datetime import datetime
        fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", '%Y-%m-%d %H:%M')

        user = self.request.user
        context['medico'] = Medico.objects.get(id=medico_id)
        context['fecha_hora'] = fecha_hora
        context['es_admin'] = user.is_staff

        if user.is_staff:
            context['pacientes'] = Paciente.objects.all().order_by('apellido', 'nombre')
        else:
            try:
                context['paciente'] = Paciente.objects.get(usuario=user)
            except Paciente.DoesNotExist:
                messages.error(self.request, "no tenes un perfil de paciente asociado.")
                return redirect('app:home')

        return context

    def form_valid(self, form):
        medico_id = self.kwargs.get('medico_id')
        fecha_str = self.kwargs.get('fecha')
        hora_str = self.kwargs.get('hora')
        from datetime import datetime
        fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", '%Y-%m-%d %H:%M')

        turno = form.save(commit=False)
        turno.medico = Medico.objects.get(id=medico_id)
        turno.fecha_hora = fecha_hora
        turno.estado = 'pendiente'
        turno.creado_por = self.request.user

        user = self.request.user
        if user.is_staff:
            paciente_id = self.request.POST.get('paciente_id')
            if paciente_id:
                try:
                    turno.paciente = Paciente.objects.get(id=paciente_id)
                except Paciente.DoesNotExist:
                    form.add_error(None, "el paciente seleccionado no existe.")
                    return self.form_invalid(form)
            else:
                form.add_error(None, "debes seleccionar un paciente de la lista.")
                return self.form_invalid(form)
        else:
            try:
                turno.paciente = Paciente.objects.get(usuario=user)
            except Paciente.DoesNotExist:
                form.add_error(None, "no tenes un perfil de paciente asociado.")
                return self.form_invalid(form)

        turno.save()
        messages.success(self.request, f"turno creado exitosamente para {turno.paciente} con {turno.medico}.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """muestra errores del formulario y mantiene los datos del contexto."""
        return self.render_to_response(self.get_context_data(form=form))


class CancelarTurnoView(LoginRequiredMixin, UpdateView):
    """
    vista para cancelar un turno existente.
    solo funciona con post (no se accede por get).
    """
    model = Turno
    fields = []  # no mostramos ningun campo editable
    template_name = 'clinica/confirmar_cancelacion.html'
    success_url = reverse_lazy('app:lista_turnos')

    def get_queryset(self):
        """
        solo permite cancelar turnos que no esten cancelados o finalizados.
        """
        return Turno.objects.exclude(
            estado__in=['cancelado', 'finalizado']
        )

    def form_valid(self, form):
        """
        cambia el estado a cancelado y muestra mensaje.
        """
        turno = form.save(commit=False)
        turno.estado = 'cancelado'
        turno.save()

        messages.success(
            self.request,
            f"turno con {turno.paciente} cancelado correctamente."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        muestra error si no se puede cancelar.
        """
        messages.error(
            self.request,
            "no se puede cancelar este turno."
        )
        return super().form_invalid(form)


class AceptarTurnoView(LoginRequiredMixin, UpdateView):
    """
    vista para que un medico acepte un turno pendiente.
    solo el medico asignado al turno puede aceptarlo.
    """
    model = Turno
    fields = []  # no mostramos campos editables
    template_name = 'clinica/confirmar_aceptacion.html'
    success_url = reverse_lazy('app:lista_turnos')

    def get_queryset(self):
        """
        solo permite aceptar turnos que esten pendientes.
        """
        return Turno.objects.filter(estado='pendiente')

    def dispatch(self, request, *args, **kwargs):
        """
        verifica que el usuario sea el medico del turno.
        """
        turno = self.get_object()

        # medico no tiene campo usuario por ahora
        # permitir solo a staff/administradores
        if not request.user.is_staff:
            messages.error(request, "solo los administradores pueden aceptar turnos.")
            return redirect('app:lista_turnos')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        cambia el estado a confirmado y muestra mensaje.
        """
        turno = form.save(commit=False)
        turno.estado = 'confirmado'
        turno.save()

        messages.success(
            self.request,
            f"turno con {turno.paciente} confirmado correctamente."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        muestra error si no se puede aceptar.
        """
        messages.error(
            self.request,
            "no se puede aceptar este turno."
        )
        return super().form_invalid(form)


class ListaTurnosView(LoginRequiredMixin, ListView):
    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"

    def get_queryset(self):
        user = self.request.user

        # admin/staff ve todo
        if user.is_staff:
            queryset = Turno.objects.all()
        else:
            # buscar paciente del usuario
            try:
                paciente = Paciente.objects.get(usuario=user)
                # turnos donde es paciente o donde lo creo
                queryset = Turno.objects.filter(
                    paciente=paciente
                ) | Turno.objects.filter(
                    creado_por=user
                )
            except Paciente.DoesNotExist:
                # si no es paciente, ve lo que creo
                queryset = Turno.objects.filter(creado_por=user)

        # filtros del formulario (fecha y medico)
        form = BusquedaTurnosForm(self.request.GET or None)
        if form.is_valid():
            fecha = form.cleaned_data.get('fecha')
            medico = form.cleaned_data.get('medico')
            if fecha:
                queryset = queryset.filter(fecha_hora__date=fecha)
            if medico:
                queryset = queryset.filter(medico=medico)

        return queryset.order_by('fecha_hora')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = BusquedaTurnosForm(self.request.GET or None)
        return context


# ==================== VISTA PARA BUSCAR PACIENTES ====================
from django.http import JsonResponse
from django.db import models
from django.views import View

class BuscarPacientesView(LoginRequiredMixin, View):
    """vista para buscar pacientes por dni o nombre (devuelve json)."""
    
    def get(self, request):
        termino = request.GET.get('q', '').strip()
        if len(termino) < 2:
            return JsonResponse([], safe=False)
        
        pacientes = Paciente.objects.filter(
            models.Q(dni__icontains=termino) |
            models.Q(nombre__icontains=termino) |
            models.Q(apellido__icontains=termino)
        )[:20]
        
        data = [{
            'id': p.id,
            'nombre': f"{p.apellido}, {p.nombre}",
            'dni': p.dni
        } for p in pacientes]
        
        return JsonResponse(data, safe=False)"#"  
"#"  
"#"  
"#"  
"#"  
"#"  
