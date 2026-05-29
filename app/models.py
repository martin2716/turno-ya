"""Modelos de dominio de TurnoYa."""

from __future__ import annotations
from django.db import models


class Especialidad(models.Model):
    """Representa la especialidad médica de un profesional."""

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Especialidades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @classmethod
    def validate(cls, nombre, descripcion=""):
        errors = []

        if not nombre or not nombre.strip():
            errors.append("El nombre de la especialidad es obligatorio.")

        return errors

    @classmethod
    def new(cls, nombre, descripcion=""):
        errors = cls.validate(nombre, descripcion)
        if errors:
            return None, errors

        especialidad = cls.objects.create(
            nombre=nombre.strip(), descripcion=descripcion.strip()
        )
        return especialidad, []

    def update(self, nombre, descripcion=""):
        errors = self.__class__.validate(nombre, descripcion)
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.save()
        return []


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
        """Retorna una etiqueta legible para listados y admin."""
        return f"Dr/a. {self.apellido}, {self.nombre}"

    def nombre_completo(self):
        """Retorna nombre y apellido concatenados."""
        return f"{self.nombre} {self.apellido}"

    def cantidad_turnos(self):
        """Retorna la cantidad total de turnos asociados a este médico."""
        if not hasattr(self, "turno_set"):
            return 0
        return self.turno_set.count()

    @classmethod
    def validate(cls, nombre, apellido, matricula, especialidad):
        """
        Valida los datos del médico. Retorna una lista de errores.
        Si la lista está vacía, los datos son válidos.
        """
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
        """
        Crea y persiste un nuevo médico si los datos son válidos.
        Retorna (instancia, errors). Si hay errores, instancia es None.
        """
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
        """
        Actualiza los datos del médico si los datos son válidos.
        Retorna una lista de errores. Si está vacía, la actualización fue exitosa.
        """
        errors = self.__class__.validate(nombre, apellido, matricula, especialidad)
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.matricula = matricula.strip()
        self.especialidad = especialidad
        self.save()
        return []

    # TODO de intermedia/final:
    # Martin: class Especialidad(models.Model): ...  ← extraer especialidad a FK
    # Maxi: class Paciente(models.Model): ...
    # Misael: class Turno(models.Model): ...
    # Dario: class Ausencia(models.Model): ...
    # Compartido: class ObraSocial(models.Model): ...
