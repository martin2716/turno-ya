from django.db import models

class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    sitio_web = models.URLField(blank=True, null=True)
    requiere_token = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Obras Sociales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @classmethod
    def validate(cls, nombre, sitio_web=None, instance=None):
        errors = []
        if not nombre or not nombre.strip():
            errors.append("El nombre de la obra social es obligatorio.")
        # Validar unicidad (excluyendo a la instancia actual si es un update)
        query = cls.objects.filter(nombre=nombre.strip() if nombre else "")
        if instance:
            query = query.exclude(pk=instance.pk)
        if query.exists():
            errors.append("Ya existe una obra social con ese nombre.")
        return errors



    @classmethod
    def new(cls, nombre, sitio_web=None, requiere_token=False):
        errors = cls.validate(nombre)
        if errors:
            return None, errors
        obra = cls.objects.create(
            nombre=nombre.strip(),
            sitio_web=sitio_web,
            requiere_token=requiere_token
        )
        return obra, []

    def update(self, nombre, sitio_web=None, requiere_token=False):
        errors = self.__class__.validate(nombre, instance=self)
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.sitio_web = sitio_web
        self.requiere_token = requiere_token
        self.save()
        return []


    @property
    def medicos_disponibles(self):
        """Retorna cuántos médicos aceptan esta obra social."""
        # 'medicos_que_la_aceptan' es el related_name que definiremos en el modelo Medico
        return self.medicos_que_la_aceptan.count()