"""Modelos de dominio de TurnoYa."""

from __future__ import annotations
from django.db import models


class Medico(models.Model):
    """Representa a un profesional médico disponible para turnos."""

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)

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

        if not especialidad or not especialidad.strip():
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
            especialidad=especialidad.strip(),
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
        self.especialidad = especialidad.strip()
        self.save()
        return []

    # TODO de intermedia/final:
    # Martin: class Especialidad(models.Model): ...  ← extraer especialidad a FK
    # Maxi: class Paciente(models.Model): ...
    # Misael: class Turno(models.Model): ...
    # Dario: class Ausencia(models.Model): ...
    # Compartido: class ObraSocial(models.Model): ...





















class Turno(models.Model):
    """Representa un turno médico agendado."""
#cls, medico, paciente, fecha, disponibilidad, observaciones
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    paciente_nombre = models.CharField(max_length=100)
    paciente_apellido = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    observaciones = models.TextField(blank=True)
    disponibilidad = models.BooleanField(default=True)

    class Meta:
        ordering = ["fecha"]

    def __str__(self):
        """Retorna una etiqueta legible para listados y admin."""
        return f"Turno con {self.medico} el {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    
#Entendimiento basico del objeto:

#validate() → ¿es seguro? → new() → crear instancia
#                  ↓
#          si hay error → devolver (None, errores)


    @classmethod
    def validate(cls, medico, paciente_nombre, paciente_apellido, fecha, disponibilidad, observaciones ):
        errors = []
        if not medico:
            errors.append("El médico es obligatorio.")
        if not paciente_nombre:
            errors.append("El nombre del paciente es obligatorio.")
        if not paciente_apellido:
            errors.append("El apellido del paciente es obligatorio.")
        if not fecha:
            errors.append("La fecha es obligatoria.")
        if not disponibilidad:
            errors.append("La disponibilidad es obligatoria.")
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
    
    #Update() → validar datos → actualizar instancia
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
        """Marca el turno como indisponible."""
        self.disponibilidad = False
        self.save()
        
    def aceptar(self):
        """Marca el turno como disponible."""
        self.disponibilidad = True
        self.save()
        
    def estadoDisponibilidad(self):#Esta vigente?
        """Retorna el estado del turno como 'Disponible' o 'Indisponible'."""
        return self.disponibilidad;