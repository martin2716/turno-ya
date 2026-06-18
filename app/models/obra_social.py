from django.db import models


class ObraSocial(models.Model):

    medico = models.ForeignKey('Medico', on_delete=models.SET_NULL, null=True, related_name='obras_sociales')
    nombre = models.CharField(max_length=100)
    sitio_web = models.URLField(blank=True, null=True)
    requiere_token = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    # TODO Implementar:
    #def validate()
    #def new()
    #def update()
