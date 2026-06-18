from django.db import models
from django.db.models import Q, F
from .medico import Medico


class Ausencia(models.Model):
    motivo = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name="ausencias"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(fecha_fin__gte=F("fecha_inicio")),
                name="fecha_fin_mayor_igual_inicio",
            )
        ]

    @classmethod
    def validate(cls, motivo, fecha_inicio, fecha_fin):
        errors = []
        if not motivo or not motivo.strip():
            errors.append("El motivo es obligatorio.")
        if not fecha_inicio:
            errors.append("La fecha de inicio es obligatoria.")
        if not fecha_fin:
            errors.append("La fecha de fin es obligatoria.")
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            errors.append("La fecha de fin no puede ser anterior a la de inicio.")
        return errors

    @classmethod
    def new(cls, motivo, fecha_inicio, fecha_fin, medico):
        errors = cls.validate(motivo, fecha_inicio, fecha_fin)
        if errors:
            return None, errors
        ausencia = cls.objects.create(
            motivo=motivo.strip(),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            medico=medico
        )
        return ausencia, []

    def update(self, motivo, fecha_inicio, fecha_fin):
        errors = self.__class__.validate(motivo, fecha_inicio, fecha_fin)
        if errors:
            return errors
        self.motivo = motivo.strip()
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.save()
        return []
