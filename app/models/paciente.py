from django.db import models
from django.contrib.auth.models import User
from .obra_social import ObraSocial


class Paciente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    telefono = models.CharField(max_length=20)
    dni = models.CharField(max_length=20, unique=True)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    def puede_solicitar_turno(self):
        if self.telefono and self.obra_social:
            return True
        return False

    @classmethod
    def validate(cls, nombre, apellido, dni, email, telefono, instance=None):
        errors = []

        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")
        if not dni or not dni.strip():
            errors.append("El DNI es obligatorio.")

        query = cls.objects.filter(dni=dni)
        if instance:
            query = query.exclude(pk=instance.pk)

        if query.exists():
            errors.append("Ya existe un paciente registrado con ese DNI.")

        if email and "@" not in email:
            errors.append("El email ingresado no es válido.")

        return errors

    @classmethod
    def new(cls, usuario, nombre, apellido, email, telefono, dni, obra_social):
        errors = cls.validate(nombre, apellido, dni, email, telefono)
        if errors:
            return None, errors

        paciente = cls.objects.create(
            usuario=usuario,
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.strip(),
            telefono=telefono.strip(),
            dni=dni.strip(),
            obra_social=obra_social
        )
        return paciente, []

    def update(self, nombre, apellido, email, telefono, dni, obra_social):
        errors = self.__class__.validate(nombre, apellido, dni, email, telefono, instance=self)
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()
        self.telefono = telefono.strip()
        self.dni = dni.strip()
        self.obra_social = obra_social
        self.save()
        return []
