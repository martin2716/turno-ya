"""Modelos de dominio de TurnoYa."""  # Descripción general del módulo donde se definen los modelos.

from __future__ import annotations  # Habilita anotaciones de tipo retardadas en Python.
from django.db import models  # Importa las herramientas de modelos de Django.
from django.contrib.auth.models import User  # Importa el modelo de usuario incorporado de Django.
from django.db.models import Q, F  # Importa constructores para consultas y referencias a campos.
from django.utils import timezone

class Especialidad(models.Model):  # Define el modelo Especialidad que hereda de models.Model.
    """Representa la especialidad médica de un profesional."""  # Docstring que describe el propósito del modelo.

    nombre = models.CharField(max_length=100, unique=True)  # Campo de texto para el nombre de la especialidad, único.
    descripcion = models.TextField(blank=True)  # Campo de texto opcional para la descripción.

    class Meta:  # Clase interna Meta para opciones de configuración del modelo.
        verbose_name_plural = "Especialidades"  # Nombre plural legible en el admin.
        ordering = ["nombre"]  # Ordena instancias por nombre por defecto.

    def __str__(self):  # Método que define la representación de cadena del objeto.
        return self.nombre  # Devuelve el nombre como representación legible.

    @classmethod
    def validate(cls, nombre, descripcion=""):  # Método de clase para validar datos antes de crear o actualizar.
        errors = []  # Lista para acumular mensajes de error.

        if not nombre or not nombre.strip():  # Valida que el nombre no sea vacío ni solo espacios.
            errors.append("El nombre de la especialidad es obligatorio.")  # Agrega mensaje de error.

        return errors  # Devuelve la lista de errores, vacía si todo está bien.

    @classmethod
    def new(cls, nombre, descripcion=""):  # Método de clase para crear una nueva especialidad.
        errors = cls.validate(nombre, descripcion)  # Valida primero los datos provistos.
        if errors:  # Si hay errores de validación...
            return None, errors  # ...devuelve None y la lista de errores.

        especialidad = cls.objects.create(
            nombre=nombre.strip(), descripcion=descripcion.strip()  # Crea el objeto limpiando espacios.
        )
        return especialidad, []  # Devuelve el objeto creado y lista vacía de errores.

    def update(self, nombre, descripcion=""):  # Método de instancia para actualizar campos.
        errors = self.__class__.validate(nombre, descripcion)  # Valida con el mismo validador de clase.
        if errors:  # Si hay errores...
            return errors  # ...retorna los errores sin guardar.

        self.nombre = nombre.strip()  # Asigna el nombre limpio.
        self.descripcion = descripcion.strip()  # Asigna la descripción limpia.
        self.save()  # Guarda los cambios en la base de datos.
        return []  # Retorna lista vacía indicando éxito.

# Responsabilidad: Este modelo encapsula la definición y validación de una especialidad médica, asegurando que cada especialidad tenga un nombre obligatorio y administrando su creación y actualización.

class Medico(models.Model):  # Define el modelo Medico para los profesionales médicos.
    """Representa a un profesional médico disponible para turnos."""  # Docstring del modelo.

    nombre = models.CharField(max_length=100)  # Nombre del médico.
    apellido = models.CharField(max_length=100)  # Apellido del médico.
    matricula = models.CharField(max_length=20, unique=True)  # Matrícula única del médico.
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,  # Protege la especialidad si se borra.
        related_name="medicos",
    )

    class Meta:
        ordering = ["apellido", "nombre"]  # Ordena médicos por apellido y nombre.

    def __str__(self):  # Representación legible para listados y administración.
        """Retorna una etiqueta legible para listados y admin."""
        return f"Dr/a. {self.apellido}, {self.nombre}"

    def nombre_completo(self):  # Método que devuelve nombre y apellido.
        """Retorna nombre y apellido concatenados."""
        return f"{self.nombre} {self.apellido}"

    def cantidad_turnos(self):  # Cuenta turnos asociados al médico.
        """Retorna la cantidad total de turnos asociados a este médico."""
        if not hasattr(self, "turno_set"):  # Comprueba si existen relaciones con Turno.
            return 0  # Si no hay relación cargada, retorna 0.
        return self.turno_set.count()  # Cuenta los turnos relacionados.

    @classmethod
    def validate(cls, nombre, apellido, matricula, especialidad):  # Valida los datos del médico.
        """
        Valida los datos del médico. Retorna una lista de errores.
        Si la lista está vacía, los datos son válidos.
        """
        errors = []  # Inicializa lista de errores.

        if not nombre or not nombre.strip():  # Verifica nombre no vacío.
            errors.append("El nombre es obligatorio.")

        if not apellido or not apellido.strip():  # Verifica apellido no vacío.
            errors.append("El apellido es obligatorio.")

        if not matricula or not matricula.strip():  # Verifica matrícula no vacía.
            errors.append("La matrícula es obligatoria.")

        if not especialidad:  # Verifica presencia de especialidad.
            errors.append("La especialidad es obligatoria.")

        return errors  # Devuelve los errores.

    @classmethod
    def new(cls, nombre, apellido, matricula, especialidad):  # Crea un nuevo médico.
        """
        Crea y persiste un nuevo médico si los datos son válidos.
        Retorna (instancia, errors). Si hay errores, instancia es None.
        """
        errors = cls.validate(nombre, apellido, matricula, especialidad)  # Valida los datos.
        if errors:  # Si hay errores de validación...
            return None, errors  # ...devuelve None y los errores.

        medico = cls.objects.create(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            matricula=matricula.strip(),
            especialidad=especialidad,
        )
        return medico, []  # Retorna el nuevo médico y lista vacía.

    def update(self, nombre, apellido, matricula, especialidad):  # Actualiza datos del médico.
        """
        Actualiza los datos del médico si los datos son válidos.
        Retorna una lista de errores. Si está vacía, la actualización fue exitosa.
        """
        errors = self.__class__.validate(nombre, apellido, matricula, especialidad)  # Valida antes de guardar.
        if errors:  # Si hay errores...
            return errors  # ...retorna errores.

        self.nombre = nombre.strip()  # Asigna nuevo nombre.
        self.apellido = apellido.strip()  # Asigna nuevo apellido.
        self.matricula = matricula.strip()  # Asigna nueva matrícula.
        self.especialidad = especialidad  # Cambia la especialidad si es necesario.
        self.save()  # Guarda los cambios.
        return []  # Indica éxito.

# Responsabilidad: Este modelo administra la información de los médicos y su vínculo con una especialidad, valida sus datos obligatorios y ofrece métodos para creación, actualización y cálculo de turnos.

class Ausencia(models.Model):  # Define el modelo Ausencia.
    motivo = models.TextField()  # Motivo de la ausencia.
    fecha_inicio = models.DateField()  # Fecha de inicio de la ausencia.
    fecha_fin = models.DateField()  # Fecha de fin de la ausencia.
    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,  # Si el médico se borra, esta ausencia también se borra.
        related_name="ausencias"
    )

    class Meta:
        constraints = [  # Definición de restricciones de base de datos.
            models.CheckConstraint(
                check=Q(fecha_fin__gte=F("fecha_inicio")),  # Verifica que fecha_fin no sea anterior a fecha_inicio.
                name="fecha_fin_mayor_igual_inicio",
            )
        ]
    
    @classmethod
    def validate(cls, motivo, fecha_inicio, fecha_fin):  # Valida datos de ausencia.
        errors = []  # Lista de errores.
        if not motivo or not motivo.strip():  # Verifica motivo no vacío.
            errors.append("El motivo es obligatorio.")
        if not fecha_inicio:  # Verifica fecha de inicio.
            errors.append("La fecha de inicio es obligatoria.")
        if not fecha_fin:  # Verifica fecha de fin.
            errors.append("La fecha de fin es obligatoria.")
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:  # Comprueba orden cronológico.
            errors.append("La fecha de fin no puede ser anterior a la de inicio.")
        return errors  # Devuelve errores.


    @classmethod
    def new(cls, motivo, fecha_inicio, fecha_fin, medico):  # Crea una nueva ausencia.
        errors = cls.validate(motivo, fecha_inicio, fecha_fin)  # Valida los datos.
        if errors:  # Si hay errores...
            return None, errors  # ...retorna None y errores.
        ausencia = cls.objects.create(
            motivo=motivo.strip(),  # Guarda el motivo limpio.
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,  
            medico=medico
        )
        return ausencia, []  # Retorna la ausencia creada.

    def update(self, motivo, fecha_inicio, fecha_fin):  # Actualiza una ausencia existente.
        errors = self.__class__.validate(motivo, fecha_inicio, fecha_fin)  # Valida los nuevos valores.
        if errors:  # Si hay errores...
            return errors  # ...retorna errores.
        self.motivo = motivo.strip()  # Actualiza motivo.
        self.fecha_inicio = fecha_inicio  # Actualiza fecha de inicio.
        self.fecha_fin = fecha_fin  # Actualiza fecha de fin.
        self.save()  # Guarda los cambios.
        return []  # Retorna éxito.

# Responsabilidad: Este modelo gestiona las ausencias de un médico, valida que el período sea coherente y mantiene la integridad de las fechas de inicio y fin.

class ObraSocial(models.Model):  # Define el modelo ObraSocial.

    medico = models.ForeignKey('Medico', on_delete=models.SET_NULL, null=True, related_name='obras_sociales')  # Relaciona obra social con médico opcionalmente.
    nombre = models.CharField(max_length=100)  # Nombre de la obra social.
    sitio_web = models.URLField(blank=True, null=True)  # URL opcional.
    requiere_token = models.BooleanField(default=False)  # Indica si requiere token.

    def __str__(self):  # Representación legible del objeto.
        return self.nombre  # Devuelve el nombre.
    
    # TODO Implementar:
    #def validate() 
    #def new()
    #def update() 

# Responsabilidad: Este modelo representa una obra social asociable a pacientes y médicos, describiendo sus datos básicos y el posible requerimiento de token.

class Paciente(models.Model):  # Define el modelo Paciente.
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación uno a uno con User.
    nombre = models.CharField(max_length=100)  # Nombre del paciente.
    apellido = models.CharField(max_length=100)  # Apellido del paciente.
    email = models.EmailField(max_length=50)  # Email del paciente.
    telefono = models.CharField(max_length=20)  # Teléfono del paciente.
    dni = models.CharField(max_length=20, unique=True)  # DNI único.
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.SET_NULL, null=True)  # Obra social asociada, opcional.
    
    def __str__(self):  # Representación legible para listados y admin.
        return f"{self.apellido}, {self.nombre}"
    
    def puede_solicitar_turno(self):  # Comprueba si el paciente tiene datos mínimos para pedir turno.
        """
        Retorna True si el paciente tiene los datos mínimos para solicitar un turno.
        """
        # Verificamos que tenga teléfono y una obra social asignada
        if self.telefono and self.obra_social:
            return True
        return False
    
    @classmethod
    def validate(cls, nombre, apellido, dni, email, telefono, instance=None):  # Valida datos del paciente, opcionalmente excluyendo la propia instancia.

        """
        Guardián de datos: verifica que todo esté en orden antes de guardar.
        Si instance no es None, es porque estamos editando (update).
        """
        errors = []  # Lista de errores.

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

        return errors  # Devuelve la lista de errores encontrados.

        
    @classmethod
    def new(cls, usuario, nombre, apellido, email, telefono, dni, obra_social):  # Crea un nuevo paciente.
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
        

    
    
    def update(self, nombre, apellido, email, telefono, dni, obra_social):  # Actualiza un paciente existente.
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

# Responsabilidad: Este modelo gestiona la información de los pacientes, sus relaciones con usuarios y obras sociales, valida campos obligatorios y controla la creación y actualización segura.

class Turno(models.Model):  # Define el modelo Turno para citas médicas.
    """Representa un turno médico agendado."""  # Docstring del modelo.
#cls, medico, paciente, fecha, disponibilidad, observaciones
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)  # Médico asociado al turno.
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    observaciones = models.TextField(blank=True)  # Observaciones opcionales.
    
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmado', 'Confirmado'),
            ('cancelado', 'Cancelado'),
            ('finalizado', 'Finalizado'),
        ],
        default='pendiente'
    )
    
    motivo = models.TextField()
    
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='turnos_creados'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["fecha_hora"]  # Ordena turnos por fecha.

    def __str__(self):
        return f"Turno #{self.id} - {self.paciente} con {self.medico} el {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
#Entendimiento basico del objeto:

#validate() → ¿es seguro? → new() → crear instancia
#                  ↓
#          si hay error → devolver (None, errores)


    @classmethod
    def validate(cls, medico, paciente, fecha_hora, motivo, estado=None, creado_por=None, observaciones="", instance=None):
        errors = []
        if not medico:
            errors.append("El médico es obligatorio.")
        if not paciente:
            errors.append("El paciente es obligatorio.")
        if not fecha_hora:
            errors.append("La fecha y hora son obligatorias.")
        if not motivo or not motivo.strip():
            errors.append("El motivo es obligatorio.")
        # observaciones es opcional (blank=True)
        return errors
    
    @classmethod
    def new(cls, medico, paciente, fecha_hora, motivo, estado=None, creado_por=None, observaciones=""):  # Crea un turno nuevo.
        errors = cls.validate(medico, paciente, fecha_hora, motivo, estado, creado_por, observaciones)  # Valida los campos.
        if errors:  # Si hay problemas...
            return None, errors  # ...retorna None y errores.
        
        turno = cls.objects.create(
            medico=medico,
            paciente=paciente,
            fecha_hora=fecha_hora,
            motivo=motivo,
            estado=estado,
            creado_por=creado_por,
            observaciones=observaciones
        )
        return turno, []  # Retorna el turno creado.
    
    #Update() → validar datos → actualizar instancia
    # TU CÓDIGO ACTUAL (LÍNEAS 319-330):
    def update(self, medico, paciente, fecha_hora, motivo, estado=None, creado_por=None, observaciones=""):
        errors = self.__class__.validate(medico, paciente, fecha_hora, motivo, estado, creado_por, observaciones)
        if errors:
            return errors
    
        self.medico = medico
        self.paciente = paciente
        self.fecha_hora = fecha_hora
        self.motivo = motivo
        self.estado = estado
        self.creado_por = creado_por
        self.observaciones = observaciones
        self.save()
        return []
        
    def cancelar(self):
        self.estado = 'cancelado'
        self.save()
        
    def aceptar(self):
        self.estado = 'confirmado'
        self.save()

# Responsabilidad: Este modelo representa una cita médica, valida sus datos esenciales, la crea, la actualiza y gestiona su estado de disponibilidad.
        
    def estadoDisponibilidad(self):#Esta vigente?
        """Retorna el estado del turno como 'Disponible' o 'Indisponible'."""
        return self.estado;

# TODO de intermedia/final:
    # Martin: class Especialidad(models.Model): ...  ← extraer especialidad a FK
    # Maxi: class Paciente(models.Model): --> Propuesta del modelo,validate,new y update implementados (maxi)
    # Misael: class Turno(models.Model): ...
    # Dario: class Ausencia(models.Model): ...
    # Compartido: class ObraSocial(models.Model): ...






#1