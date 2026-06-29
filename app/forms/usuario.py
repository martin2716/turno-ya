import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from app.models import ObraSocial, Paciente


class RegistroPacienteForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(max_length=150, required=True, label="Nombre", widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=150, required=True, label="Apellido", widget=forms.TextInput(attrs={"class": "form-control"}))
    telefono = forms.CharField(max_length=20, label="Teléfono", widget=forms.TextInput(attrs={"class": "form-control"}))
    dni = forms.CharField(max_length=20, label="DNI", widget=forms.TextInput(attrs={"class": "form-control"}))
    obra_social = forms.ModelChoiceField(
        queryset=ObraSocial.objects.order_by("nombre"),
        required=True,
        empty_label="-- Seleccioná una obra social --",
        label="Obra social",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "telefono",
            "dni",
            "obra_social",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Ya existe un usuario registrado con ese email."
            )
        return email

    def clean_first_name(self):
        nombre = self.cleaned_data.get("first_name", "").strip()
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$", nombre):
            raise forms.ValidationError("El nombre solo puede contener letras.")
        return nombre

    def clean_last_name(self):
        apellido = self.cleaned_data.get("last_name", "").strip()
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$", apellido):
            raise forms.ValidationError("El apellido solo puede contener letras.")
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "").strip()
        if not re.match(r"^\d+$", telefono):
            raise forms.ValidationError("El teléfono solo puede contener números.")
        return telefono

    def clean_dni(self):
        dni = self.cleaned_data.get("dni", "").strip()
        if not re.match(r"^\d+$", dni):
            raise forms.ValidationError("El DNI solo puede contener números.")
        return dni

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data
        errors = Paciente.validate(
            cleaned_data.get("first_name", ""),
            cleaned_data.get("last_name", ""),
            cleaned_data.get("dni", ""),
            cleaned_data.get("email", ""),
            cleaned_data.get("telefono", ""),
            cleaned_data.get("obra_social"),
        )
        if errors:
            raise forms.ValidationError(errors)
        return cleaned_data


class PerfilUsuarioForm(forms.Form):
    first_name = forms.CharField(max_length=150, label="Nombre", widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=150, label="Apellido", widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control"}))
    telefono = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control"}))
    dni = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control"}))
    obra_social = forms.ModelChoiceField(
        queryset=ObraSocial.objects.order_by("nombre"),
        required=True,
        empty_label="-- Seleccioná una obra social --",
        widget=forms.Select(attrs={"class": "form-select"}),
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

    def clean_first_name(self):
        nombre = self.cleaned_data.get("first_name", "").strip()
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$", nombre):
            raise forms.ValidationError("El nombre solo puede contener letras.")
        return nombre

    def clean_last_name(self):
        apellido = self.cleaned_data.get("last_name", "").strip()
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$", apellido):
            raise forms.ValidationError("El apellido solo puede contener letras.")
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "").strip()
        if not re.match(r"^\d+$", telefono):
            raise forms.ValidationError("El teléfono solo puede contener números.")
        return telefono

    def clean_dni(self):
        dni = self.cleaned_data.get("dni", "").strip()
        if not re.match(r"^\d+$", dni):
            raise forms.ValidationError("El DNI solo puede contener números.")
        return dni

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
        if self.errors:
            return cleaned_data
        nombre = cleaned_data.get("first_name", "")
        apellido = cleaned_data.get("last_name", "")
        email = cleaned_data.get("email", "")
        telefono = cleaned_data.get("telefono", "")
        dni = cleaned_data.get("dni", "")

        obra_social = cleaned_data.get("obra_social")
        if any([nombre, apellido, email, telefono, dni]):
            errors = Paciente.validate(
                nombre, apellido, dni, email, telefono, obra_social, instance=self.paciente
            )
            if errors:
                raise forms.ValidationError(errors)

        return cleaned_data
