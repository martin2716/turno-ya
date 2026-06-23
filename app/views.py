"""Vistas iniciales para navegar médicos y pantalla de inicio."""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic import ListView, TemplateView
from .models import Especialidad, Medico, Turno, Paciente
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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

    def get_queryset(self):
        queryset = super().get_queryset()
        # Buscamos el parámetro 'especialidad' en el GET de la URL
        especialidad_id = self.request.GET.get('especialidad')
        
        if especialidad_id:
            # Filtramos si el usuario seleccionó una especialidad
            queryset = queryset.filter(especialidad_id=especialidad_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Esto llena la variable 'especialidades' que usas en el for del HTML
        context['especialidades'] = Especialidad.objects.all()
        return context

class ListaTurnosView(PermissionRequiredMixin, ListView):
    """Lista todos los turnos."""

    model = Turno
    template_name = "clinica/lista_turnos.html"
    context_object_name = "turnos"
    permission_required = 'app.view_turno' # O el permiso que necesites

    def handle_no_permission(self):
        return redirect('home')


class RegistroUsuarioView(CreateView):
    """Base comun para registro de usuarios del proyecto."""

    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

class ListaPacientesView(PermissionRequiredMixin, ListView):
    """Lista todos los pacientes."""

    model = Paciente
    template_name = "clinica/lista_pacientes.html"
    context_object_name = "pacientes"

    # agregamos el permiso requerido para acceder a esta vista
    permission_required = 'app.view_paciente' # O el permiso que necesites
    
    def handle_no_permission(self):
        return redirect('home')
        

class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    model = Paciente
    # Campos que el usuario tiene permitido modificar después del alta
    fields = ['nombre', 'apellido', 'telefono', 'obra_social'] 
    template_name = 'clinica/perfil_form.html'
    success_url = reverse_lazy('app:home') 

    def dispatch(self, request, *args, **kwargs):
        """
        El método dispatch es el primero en ejecutarse al llamar a la vista.
        Aquí validamos el estado del usuario antes de procesar nada.
        """
        
        # 1. Si el usuario NO tiene un paciente asociado Y no es staff,
        # lo obligamos a pasar por el formulario de creación.
        if not hasattr(request.user, 'paciente') and not request.user.is_staff:
            return redirect('crear_perfil') 
        
        # 2. Si el usuario es staff (admin), no tiene sentido que edite un perfil de paciente.
        # Lo redirigimos a home.
        if request.user.is_staff:
            return redirect('app:home') 
            
        # 3. Si pasó todas las validaciones (es un paciente con perfil creado),
        # ejecutamos la lógica normal de la vista.
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """
        Este método busca el objeto que se va a editar.
        Como ya validamos en dispatch que el paciente existe, 
        aquí simplemente lo devolvemos de forma segura.
        """
        # Accedemos al paciente a través de la relación OneToOne con el usuario
        return self.request.user.paciente

class PerfilCreateView(LoginRequiredMixin, CreateView):
    model = Paciente
    fields = ['nombre', 'apellido', 'email', 'telefono', 'dni', 'obra_social']
    template_name = 'clinica/perfil_form.html'
    success_url = reverse_lazy('app:home')

    def form_valid(self, form):
    
        paciente, errors = Paciente.new(
            usuario=self.request.user,
            nombre=form.cleaned_data['nombre'],
            apellido=form.cleaned_data['apellido'],
            email=form.cleaned_data['email'],
            telefono=form.cleaned_data['telefono'],
            dni=form.cleaned_data['dni'],
            obra_social=form.cleaned_data['obra_social']
        )
        
        if errors:
            # Si hay errores de validación, volvemos a mostrar el form con errores
            form.add_error(None, errors)
            return self.form_invalid(form)
            
        return redirect(self.success_url)
   


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
