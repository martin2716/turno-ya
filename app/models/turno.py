from django.db import models
from .medico import Medico


class Turno(models.Model):
    """Representa un turno médico agendado."""

    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    paciente_nombre = models.CharField(max_length=100)
    paciente_apellido = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    observaciones = models.TextField(blank=True)
    disponibilidad = models.BooleanField(default=True)

    class Meta:
        ordering = ["fecha"]

    def __str__(self):
        return f"Turno con {self.medico} el {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def validate(cls, medico, paciente_nombre, paciente_apellido, fecha, disponibilidad, observaciones):
        errors = []
        if not medico:
            errors.append("El médico es obligatorio.")
        if not paciente_nombre:
            errors.append("El nombre del paciente es obligatorio.")
        if not paciente_apellido:
            errors.append("El apellido del paciente es obligatorio.")
        if not fecha:
            errors.append("La fecha es obligatoria.")
        if not observaciones:
            errors.append("Las observaciones son obligatorias.")
        return errors

    @classmethod
    def new(cls, medico, paciente_nombre, paciente_apellido, fecha, disponibilidad, observaciones):
        errors = cls.validate(medico, paciente_nombre, paciente_apellido, fecha, disponibilidad, observaciones)
        if errors:
            return None, errors

        turno = cls.objects.create(
            medico=medico,
            paciente_nombre=paciente_nombre,
            paciente_apellido=paciente_apellido,
            fecha=fecha,
            disponibilidad=disponibilidad,
            observaciones=observaciones
        )
        return turno, []

    def update(self, medico, paciente_nombre, paciente_apellido, fecha, disponibilidad, observaciones):
        errors = self.__class__.validate(medico, paciente_nombre, paciente_apellido, fecha, disponibilidad, observaciones)
        if errors:
            return errors

        self.medico = medico
        self.paciente_nombre = paciente_nombre
        self.paciente_apellido = paciente_apellido
        self.fecha = fecha
        self.disponibilidad = disponibilidad
        self.observaciones = observaciones
        self.save()
        return []

    def cancelar(self):
        self.disponibilidad = False
        self.save()

    def aceptar(self):
        self.disponibilidad = True
        self.save()

    def estadoDisponibilidad(self):
        return self.disponibilidad
