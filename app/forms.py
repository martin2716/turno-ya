"""Formularios personalizados para la aplicación."""
#1
from django import forms
from django.utils import timezone
from .models import Turno, Medico, Paciente
from datetime import date

class TurnoForm(forms.ModelForm):
    """Formulario para la creación y edición de turnos."""

    class Meta:#Segun deepseek, declara la metadata del formulario
        model = Turno
        fields = ['medico', 'paciente', 'fecha_hora', 'motivo', 'observaciones']
        widgets = {
            'fecha_hora': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'motivo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describa el motivo de la consulta...'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Observaciones adicionales (opcional)'}),
        }
        labels = {
            'medico': 'Médico',
            'paciente': 'Paciente',
            'fecha_hora': 'Fecha y Hora',
            'motivo': 'Motivo de la consulta',
            'observaciones': 'Observaciones',
        }

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario con configuraciones adicionales."""
        super().__init__(*args, **kwargs)
        
        self.fields['fecha_hora'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['medico'].queryset = Medico.objects.all().order_by('apellido', 'nombre')
        self.fields['paciente'].queryset = Paciente.objects.all().order_by('apellido', 'nombre')

    def clean_fecha_hora(self):
        """Valida que la fecha no sea pasada."""
        fecha_hora = self.cleaned_data.get('fecha_hora')
        
        if fecha_hora and fecha_hora < timezone.now():
            raise forms.ValidationError("No se puede agendar un turno en el pasado.")
        
        return fecha_hora

    def clean(self):
        """Validaciones personalizadas que involucran múltiples campos."""
        cleaned_data = super().clean()
        medico = cleaned_data.get('medico')
        paciente = cleaned_data.get('paciente')
        fecha_hora = cleaned_data.get('fecha_hora')
        
        if not medico or not paciente or not fecha_hora:
            return cleaned_data
        
        # Validar que el médico no tenga otro turno en el mismo horario
        turno_existente_medico = Turno.objects.filter(
            medico=medico,
            fecha_hora=fecha_hora
        ).exclude(estado='cancelado')
        
        if self.instance and self.instance.pk:
            turno_existente_medico = turno_existente_medico.exclude(pk=self.instance.pk)
        
        if turno_existente_medico.exists():
            raise forms.ValidationError(
                f"El médico {medico} ya tiene un turno agendado para esa fecha y hora."
            )
        
        # Validar que el paciente no tenga otro turno en el mismo horario
        turno_existente_paciente = Turno.objects.filter(
            paciente=paciente,
            fecha_hora=fecha_hora
        ).exclude(estado='cancelado')
        
        if self.instance and self.instance.pk:
            turno_existente_paciente = turno_existente_paciente.exclude(pk=self.instance.pk)
        
        if turno_existente_paciente.exists():
            raise forms.ValidationError(
                f"El paciente {paciente} ya tiene un turno agendado para esa fecha y hora."
            )
        
        return cleaned_data

    def save(self, commit=True):
        """Guarda el turno asegurando que se establezca el estado por defecto."""
        turno = super().save(commit=False)
        if not turno.pk:
            turno.estado = 'pendiente'
        if commit:
            turno.save()
        return turno
    
    
    
    
class BusquedaTurnosForm(forms.Form):
    """
    formulario para buscar turnos por fecha o medico.
    """
    fecha = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
        label='Fecha'
    )
    
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.all().order_by('apellido', 'nombre'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Medico'
    )
    
    def clean_fecha(self):
        """valida que la fecha no sea pasada."""
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < date.today():
            raise forms.ValidationError("No se puede buscar en fechas pasadas.")
        return fecha