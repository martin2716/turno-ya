from django.db import models
from .especialidad import Especialidad


class Medico(models.Model):
    """Representa a un profesional médico disponible para turnos."""

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name="medicos",
    )

    class Meta:
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"Dr/a. {self.apellido}, {self.nombre}"

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def cantidad_turnos(self):
        if not hasattr(self, "turno_set"):
            return 0
        return self.turno_set.count()

    @classmethod
    def validate(cls, nombre, apellido, matricula, especialidad):
        errors = []

        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")

        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")

        if not matricula or not matricula.strip():
            errors.append("La matrícula es obligatoria.")

        if not especialidad:
            errors.append("La especialidad es obligatoria.")

        return errors

    @classmethod
    def new(cls, nombre, apellido, matricula, especialidad):
        errors = cls.validate(nombre, apellido, matricula, especialidad)
        if errors:
            return None, errors

        medico = cls.objects.create(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            matricula=matricula.strip(),
            especialidad=especialidad,
        )
        return medico, []

    def update(self, nombre, apellido, matricula, especialidad):
        errors = self.__class__.validate(nombre, apellido, matricula, especialidad)
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.matricula = matricula.strip()
        self.especialidad = especialidad
        self.save()
        return []
