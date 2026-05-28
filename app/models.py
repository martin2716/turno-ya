"""Modelos de dominio de TurnoYa."""

from __future__ import annotations
from django.db import models
from django.contrib.auth.models import User


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

class Paciente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    telefono = models.CharField(max_length=20)
    dni = models.CharField(max_length=20, unique=True)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre}"
    
    def puede_solicitar_turno(self):
        """
        Retorna True si el paciente tiene los datos mínimos para solicitar un turno.
        """
        # Verificamos que tenga teléfono y una obra social asignada
        if self.telefono and self.obra_social:
            return True
        return False
    
    @classmethod
    def validate(cls, nombre, apellido, dni, email, telefono, instance=None):

        """
        Guardián de datos: verifica que todo esté en orden antes de guardar.
        Si instance no es None, es porque estamos editando (update).
        """
        errors = []

        # 1. Validación de campos obligatorios
        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")
        if not dni or not dni.strip():
            errors.append("El DNI es obligatorio.")

        # 2. Validación de unicidad (DNI)
        # Si instance existe (es un update), excluimos al mismo paciente 
        # de la búsqueda para que no se autodetecte como duplicado.
        query = cls.objects.filter(dni=dni)
        if instance:
            query = query.exclude(pk=instance.pk)

        if query.exists():
            errors.append("Ya existe un paciente registrado con ese DNI.")

        # 3 validacion de formato simple para Email
        if email and "@" not in email:
            errors.append("El email ingresado no es válido.")

        return errors

        
    @classmethod
    def new(cls, usuario, nombre, apellido, email, telefono, dni, obra_social):
        """
        Crea y persiste un nuevo paciente si los datos son válidos.
        Retorna (instancia, errores).
        """

        # 1. Llamamos al validador que ya armamos
        errors = cls.validate(nombre, apellido, dni, email, telefono)

        # 2. Si hay errores, no creamos nada y devolvemos la lista
        if errors:
            return None, errors
        
        # 3. si todo esta bien, creamos el paciente
        paciente = cls.objects.create(
            usuario=usuario,
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.strip(),
            telefono=telefono.strip(),
            dni=dni.strip(),
            obra_social=obra_social
        )

        # Devolvemos la instancia creada y una lista vacía de errores
        return paciente, []
        



    
    def update(self, nombre, apellido, email, telefono, dni, obra_social):
        """
        Actualiza los datos del paciente tras validar que no haya conflictos.
        """

        # Validamos usando instance=self para ignorarnos a nosotros mismos
        errors = self.__class__.validate(nombre, apellido, dni, email, telefono, instance=self)

        if errors:
            return errors
        
        # si no hay errores, actualizamos los campos 

        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()
        self.telefono = telefono.strip()
        self.dni = dni.strip()
        self.obra_social = obra_social

        self.save() # Guardamos los cambios en la BD
        return [] # Retornamos lista vacía indicando éxito
    

    
    

    # TODO de intermedia/final:
    # Martin: class Especialidad(models.Model): ...  ← extraer especialidad a FK
    # Maxi: class Paciente(models.Model): --> Propuesta del modelo,validate,new y update implementados (maxi)
    # Misael: class Turno(models.Model): ...
    # Dario: class Ausencia(models.Model): ...
    # Compartido: class ObraSocial(models.Model): --> Propuesta del modelo implementada (maxi)

