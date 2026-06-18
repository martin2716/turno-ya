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
