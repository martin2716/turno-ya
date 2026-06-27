from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Ausencia, Especialidad, Medico, ObraSocial, Paciente, Turno


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Ya existe un usuario registrado con ese email."
            )
        return email


class PerfilUsuarioForm(forms.Form):
    first_name = forms.CharField(max_length=150, label="Nombre")
    last_name = forms.CharField(max_length=150, label="Apellido")
    email = forms.EmailField(label="Email")
    telefono = forms.CharField(max_length=20)
    dni = forms.CharField(max_length=20)
    obra_social = forms.ModelChoiceField(
        queryset=ObraSocial.objects.order_by("nombre"),
        required=False,
        empty_label="Sin obra social",
    )

    def __init__(self, *args, user=None, paciente=None, **kwargs):
        self.user = user
        self.paciente = paciente
        initial = kwargs.setdefault("initial", {})

        if user is not None:
            initial.setdefault("first_name", user.first_name)
            initial.setdefault("last_name", user.last_name)
            initial.setdefault("email", user.email)

        if paciente is not None:
            initial.setdefault("telefono", paciente.telefono)
            initial.setdefault("dni", paciente.dni)
            initial.setdefault("obra_social", paciente.obra_social)

        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        query = get_user_model().objects.filter(email__iexact=email)
        if self.user is not None:
            query = query.exclude(pk=self.user.pk)
        if query.exists():
            raise forms.ValidationError(
                "Ya existe un usuario registrado con ese email."
            )
        return email

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get("first_name", "")
        apellido = cleaned_data.get("last_name", "")
        email = cleaned_data.get("email", "")
        telefono = cleaned_data.get("telefono", "")
        dni = cleaned_data.get("dni", "")

        if any([nombre, apellido, email, telefono, dni]):
            errors = Paciente.validate(
                nombre, apellido, dni, email, telefono, instance=self.paciente
            )
            if errors:
                raise forms.ValidationError(errors)

        return cleaned_data


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ["medico", "fecha", "observaciones"]
        widgets = {
            "fecha": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha <= timezone.now():
            raise forms.ValidationError("La fecha del turno debe ser futura.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        medico = cleaned_data.get("medico")
        fecha = cleaned_data.get("fecha")

        if medico and fecha:
            if Turno.objects.filter(
                medico=medico, fecha=fecha, disponibilidad=True
            ).exists():
                raise forms.ValidationError(
                    "Ese horario ya fue reservado para el médico seleccionado."
                )

            if medico.ausencias.filter(
                fecha_inicio__lte=fecha.date(), fecha_fin__gte=fecha.date()
            ).exists():
                raise forms.ValidationError(
                    "El médico seleccionado tiene una ausencia cargada para esa fecha."
                )

        return cleaned_data


class AusenciaForm(forms.ModelForm):
    class Meta:
        model = Ausencia
        fields = ["medico", "motivo", "fecha_inicio", "fecha_fin"]
        widgets = {
            "motivo": forms.Textarea(attrs={"rows": 3}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        errors = Ausencia.validate(
            cleaned_data.get("motivo"),
            cleaned_data.get("fecha_inicio"),
            cleaned_data.get("fecha_fin"),
        )
        if errors:
            raise forms.ValidationError(errors)
        return cleaned_data


class FiltroMedicoForm(forms.Form):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.order_by("nombre"),
        required=False,
        empty_label="Todas las especialidades",
    )
