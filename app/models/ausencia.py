from django.db import models
from django.db.models import Q, F
from .medico import Medico


class Ausencia(models.Model):
    motivo = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    medico = models.ForeignKey(
        Medico, on_delete=models.CASCADE, related_name="ausencias"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(fecha_fin__gte=F("fecha_inicio")),
                name="fecha_fin_mayor_igual_inicio",
            )
        ]

    @classmethod
    def validate(cls, motivo, fecha_inicio, fecha_fin, medico=None):
        errors = []
        if not motivo or not motivo.strip():
            errors.append("El motivo es obligatorio.")
        if not fecha_inicio:
            errors.append("La fecha de inicio es obligatoria.")
        if not fecha_fin:
            errors.append("La fecha de fin es obligatoria.")
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            errors.append("La fecha de fin no puede ser anterior a la de inicio.")

        # Verificar que el médico no tenga turnos activos en ese rango
        if medico and fecha_inicio and fecha_fin:
            from .turno import Turno

            turnos_activos = Turno.objects.filter(
                medico=medico,
                fecha_hora__date__gte=fecha_inicio,
                fecha_hora__date__lte=fecha_fin,
                estado__in=[Turno.PENDIENTE, Turno.CONFIRMADO],
            )
            if turnos_activos.exists():
                cantidad = turnos_activos.count()
                errors.append(
                    f"El médico tiene {cantidad} turno{'s' if cantidad > 1 else ''} "
                    f"activo{'s' if cantidad > 1 else ''} en ese período. "
                    f"Cancelalos antes de registrar la ausencia."
                )

        return errors

    @classmethod
    def new(cls, motivo, fecha_inicio, fecha_fin, medico):
        errors = cls.validate(motivo, fecha_inicio, fecha_fin, medico=medico)
        if errors:
            return None, errors
        ausencia = cls.objects.create(
            motivo=motivo.strip(),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            medico=medico,
        )
        return ausencia, []

    def update(self, motivo, fecha_inicio, fecha_fin, medico=None):
        errors = self.__class__.validate(
            motivo, fecha_inicio, fecha_fin, medico=medico or self.medico
        )
        if errors:
            return errors
        self.motivo = motivo.strip()
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.save()
        return []
