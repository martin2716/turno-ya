"""formularios personalizados para la aplicacion."""

from django import forms
from django.utils import timezone
from datetime import date
from .models import Turno, Medico, Paciente, Ausencia


class TurnoForm(forms.ModelForm):
    """formulario para crear turnos."""
    
    class Meta:
        model = Turno
        fields = ['medico', 'paciente', 'fecha_hora', 'motivo', 'observaciones']
        widgets = {
            'fecha_hora': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'motivo...'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'observaciones (opcional)'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'paciente': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'medico': 'medico',
            'paciente': 'paciente',
            'fecha_hora': 'fecha y hora',
            'motivo': 'motivo',
            'observaciones': 'observaciones',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_hora'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
        self.fields['medico'].queryset = Medico.objects.all().order_by('apellido', 'nombre')
        self.fields['paciente'].queryset = Paciente.objects.all().order_by('apellido', 'nombre')

    def clean_fecha_hora(self):
        """valida que la fecha no sea pasada."""
        fecha = self.cleaned_data.get('fecha_hora')
        if fecha and fecha < timezone.now():
            raise forms.ValidationError("no se puede agendar un turno en el pasado.")
        return fecha

    def clean(self):
        """valida conflictos de horario."""
        data = super().clean()
        medico = data.get('medico')
        paciente = data.get('paciente')
        fecha = data.get('fecha_hora')
        
        if not all([medico, paciente, fecha]):
            return data
        
        # conflicto de medico
        turno_medico = Turno.objects.filter(medico=medico, fecha_hora=fecha).exclude(estado='cancelado')
        if self.instance and self.instance.pk:
            turno_medico = turno_medico.exclude(pk=self.instance.pk)
        if turno_medico.exists():
            raise forms.ValidationError("el medico ya tiene un turno a esa hora.")
        
        # conflicto de paciente
        turno_paciente = Turno.objects.filter(paciente=paciente, fecha_hora=fecha).exclude(estado='cancelado')
        if self.instance and self.instance.pk:
            turno_paciente = turno_paciente.exclude(pk=self.instance.pk)
        if turno_paciente.exists():
            raise forms.ValidationError("el paciente ya tiene un turno a esa hora.")
        
        return data

    def save(self, commit=True):
        turno = super().save(commit=False)
        if not turno.pk:
            turno.estado = 'pendiente'
        if commit:
            turno.save()
        return turno


class BusquedaTurnosForm(forms.Form):
    """formulario para buscar turnos por fecha o medico."""
    
    fecha = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
        label='fecha'
    )
    
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.all().order_by('apellido', 'nombre'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='medico'
    )
    
    def clean_fecha(self):
        """valida que la fecha no sea pasada."""
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < date.today():
            raise forms.ValidationError("no se puede buscar en fechas pasadas.")
        return fecha