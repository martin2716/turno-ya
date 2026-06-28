from django.db import models
from django.contrib.auth.models import User
from .obra_social import ObraSocial


class Paciente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    telefono = models.CharField(max_length=20)
    dni = models.CharField(max_length=20, unique=True)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.PROTECT, null=False, blank=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(nombre=""),
                name="paciente_nombre_no_vacio",
            ),
            models.CheckConstraint(
                check=~models.Q(apellido=""),
                name="paciente_apellido_no_vacio",
            ),
            models.CheckConstraint(
                check=~models.Q(dni=""),
                name="paciente_dni_no_vacio",
            ),
            models.CheckConstraint(
                check=~models.Q(telefono=""),
                name="paciente_telefono_no_vacio",
            ),
            models.CheckConstraint(
                check=~models.Q(email=""),
                name="paciente_email_no_vacio",
            ),
        ]

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    def puede_solicitar_turno(self):
        obra_social_id = getattr(self, 'obra_social_id', None)
        if self.telefono and obra_social_id:
            return True
        return False
    
    

    @classmethod
    def validate(cls, nombre, apellido, dni, email, telefono,obra_social, instance=None):
        errors = []

        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")
        if not dni or not dni.strip():
            errors.append("El DNI es obligatorio.")
        if not obra_social:
            errors.append("La obra social es obligatoria.")
        else:
            from .obra_social import ObraSocial
            if not ObraSocial.objects.filter(pk=obra_social.pk).exists():
                errors.append("La obra social seleccionada no es válida.")

        query = cls.objects.filter(dni=dni)
        if instance:
            query = query.exclude(pk=instance.pk)

        if query.exists():
            errors.append("Ya existe un paciente registrado con ese DNI.")

        if not email or not email.strip():
            errors.append("El email es obligatorio.")
        elif "@" not in email:
            errors.append("El email ingresado no es válido.")

        return errors

    @classmethod
    def new(cls, usuario, nombre, apellido, email, telefono, dni, obra_social):
        errors = cls.validate(nombre, apellido, dni, email, telefono, obra_social)
        if errors:
            return None, errors

        paciente = cls.objects.create(
            usuario=usuario,
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.strip(),
            telefono=telefono.strip(),
            dni=dni.strip(),
            obra_social=obra_social
        )
        return paciente, []

    def update(self, nombre, apellido, email, telefono, dni, obra_social):
        errors = self.__class__.validate(nombre, apellido, dni, email, telefono, obra_social, instance=self)
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()
        self.telefono = telefono.strip()
        self.dni = dni.strip()
        self.obra_social = obra_social
        self.save()
        return []
    
