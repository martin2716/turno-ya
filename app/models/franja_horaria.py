from django.db import models
from .medico import Medico


class FranjaHoraria(models.Model):
    """Franja de atención de un médico para un día de la semana.

    Reemplaza el parche de `hora_inicio`/`hora_fin` sobre Medico: permite
    múltiples franjas por médico (turnos partidos, horarios distintos por día).
    """

    LUNES, MARTES, MIERCOLES, JUEVES, VIERNES, SABADO, DOMINGO = range(7)
    DIAS_SEMANA = [
        (LUNES, "Lunes"),
        (MARTES, "Martes"),
        (MIERCOLES, "Miércoles"),
        (JUEVES, "Jueves"),
        (VIERNES, "Viernes"),
        (SABADO, "Sábado"),
        (DOMINGO, "Domingo"),
    ]

    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name="franjas",
    )
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        ordering = ["dia_semana", "hora_inicio"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(hora_fin__gt=models.F("hora_inicio")),
                name="franja_hora_fin_mayor_inicio",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_dia_semana_display()} "
            f"{self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M} ({self.medico})"
        )

    @classmethod
    def validate(cls, medico, dia_semana, hora_inicio, hora_fin):
        errors = []

        if not medico:
            errors.append("El médico es obligatorio.")

        if dia_semana is None:
            errors.append("El día de la semana es obligatorio.")
        elif dia_semana not in dict(cls.DIAS_SEMANA):
            errors.append("El día de la semana no es válido.")

        if not hora_inicio:
            errors.append("La hora de inicio es obligatoria.")

        if not hora_fin:
            errors.append("La hora de fin es obligatoria.")

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            errors.append("La hora de fin debe ser posterior a la hora de inicio.")

        return errors

    @classmethod
    def new(cls, medico, dia_semana, hora_inicio, hora_fin):
        errors = cls.validate(medico, dia_semana, hora_inicio, hora_fin)
        if errors:
            return None, errors

        franja = cls.objects.create(
            medico=medico,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )
        return franja, []

    def update(self, medico, dia_semana, hora_inicio, hora_fin):
        errors = self.__class__.validate(medico, dia_semana, hora_inicio, hora_fin)
        if errors:
            return errors

        self.medico = medico
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.save()
        return []
