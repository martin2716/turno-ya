"""Vistas iniciales para navegar médicos y pantalla de inicio."""
#111
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView
from .models import Especialidad, Medico, Turno, Paciente

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import TurnoForm,BusquedaTurnosForm
from django.shortcuts import redirect

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

class ListaPacientesView(ListView):
    """Lista todos los pacientes."""

    model = Paciente
    template_name = "clinica/lista_pacientes.html"
    context_object_name = "pacientes"


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





class NuevoTurnoView(LoginRequiredMixin, CreateView):
    """
    Vista para que un usuario autenticado pueda crear un nuevo turno.
    """
    model = Turno
    form_class = TurnoForm
    template_name = 'clinica/form_turno.html'
    success_url = reverse_lazy('app:lista_turnos')
    
    def form_valid(self, form):
        """Asigna el usuario actual como creador y guarda."""
        form.instance.creado_por = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"✅ ¡Turno creado exitosamente para {form.instance.paciente} con {form.instance.medico}!"
        )
        return response
    
    def form_invalid(self, form):
        """Muestra mensaje de error si el formulario no es válido."""
        messages.error(
            self.request,
            "❌ Error al crear el turno. Por favor, corrige los errores del formulario."
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto."""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo Turno'
        context['boton_texto'] = 'Solicitar Turno'
        return context
    
    
    
    
    
    
    
    
    
    
    
    
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
            f"Turno con {turno.paciente} cancelado correctamente."
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        muestra error si no se puede cancelar.
        """
        messages.error(
            self.request,
            "No se puede cancelar este turno."
        )
        return super().form_invalid(form)
    
    
    








#Aceptar turno
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
        
        # verificar que el usuario es medico
        try:
            medico = Medico.objects.get(usuario=request.user)
        except Medico.DoesNotExist:
            messages.error(request, "Solo los medicos pueden aceptar turnos.")
            return redirect('app:lista_turnos')
        
        # verificar que el medico es el mismo del turno
        if turno.medico != medico:
            messages.error(request, "No podes aceptar un turno que no te corresponde.")
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
            f"Turno con {turno.paciente} confirmado correctamente."
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        muestra error si no se puede aceptar.
        """
        messages.error(
            self.request,
            "No se puede aceptar este turno."
        )
        return super().form_invalid(form)
    
    
    
    
class ListaTurnosView(LoginRequiredMixin, ListView):
    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"
    
    def get_queryset(self):
        user = self.request.user
        
        # base segun rol
        if user.is_staff:
            queryset = Turno.objects.all()
        else:
            try:
                medico = Medico.objects.get(usuario=user)
                queryset = Turno.objects.filter(medico=medico)
            except Medico.DoesNotExist:
                try:
                    paciente = Paciente.objects.get(usuario=user)
                    queryset = Turno.objects.filter(paciente=paciente)
                except Paciente.DoesNotExist:
                    queryset = Turno.objects.filter(creado_por=user)
        
        # filtros del formulario
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