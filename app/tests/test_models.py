"""Pruebas unitarias del modelo Medico."""

from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Especialidad, Medico, ObraSocial, Paciente, Turno, Ausencia
from django.utils import timezone
from datetime import timedelta, date


class EspecialidadModelTest(TestCase):
    """Verifica comportamiento basico y validaciones del modelo Especialidad."""

    def setUp(self):
        self.especialidad = Especialidad.objects.create(
            nombre="Pediatría",
            descripcion="Atención médica infantil",
        )

    def test_str_retorna_nombre(self):
        self.assertEqual(str(self.especialidad), "Pediatría")

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = Especialidad.validate("Cardiología", "Especialidad del corazón")
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Especialidad.validate("", "Especialidad sin nombre")
        self.assertTrue(len(errors) > 0)

    def test_new_crea_especialidad_con_datos_validos(self):
        especialidad, errors = Especialidad.new("Clínica Médica", "Atención integral")
        self.assertEqual(errors, [])
        self.assertIsNotNone(especialidad)
        self.assertEqual(especialidad.nombre, "Clínica Médica")
        self.assertTrue(Especialidad.objects.filter(nombre="Clínica Médica").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        count_antes = Especialidad.objects.count()
        especialidad, errors = Especialidad.new("", "")
        self.assertIsNone(especialidad)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Especialidad.objects.count(), count_antes)

    def test_update_modifica_datos_correctamente(self):
        errors = self.especialidad.update("Neurología", "Sistema nervioso")
        self.assertEqual(errors, [])
        self.especialidad.refresh_from_db()
        self.assertEqual(self.especialidad.nombre, "Neurología")
        self.assertEqual(self.especialidad.descripcion, "Sistema nervioso")

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.especialidad.update("", "")
        self.assertTrue(len(errors) > 0)
        self.especialidad.refresh_from_db()
        self.assertEqual(self.especialidad.nombre, "Pediatría")


class MedicoModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo."""

    def setUp(self):
        # --- revisar si esta fecha tiene utilidad ---
        self.fechaValida = timezone.now() + timedelta(days=5)
        self.especialidad = Especialidad.objects.create(
            nombre="Pediatría",
            descripcion="Atención médica infantil",
        )
        self.medico = Medico.objects.create(
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad=self.especialidad,
        )

    # --- __str__ y métodos simples ---

    def test_str_incluye_apellido_y_nombre(self):
        self.assertIn("Romero", str(self.medico))
        self.assertIn("Laura", str(self.medico))

    def test_nombre_completo(self):
        self.assertEqual(self.medico.nombre_completo(), "Laura Romero")

    def test_cantidad_turnos_inicial_es_cero(self):
        self.assertEqual(self.medico.cantidad_turnos(), 0)

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        especialidad = Especialidad.objects.create(nombre="Cardiología")
        errors = Medico.validate("Ana", "García", "MP-0001", especialidad)
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Medico.validate("", "García", "MP-0001", self.especialidad)
        self.assertTrue(len(errors) > 0)

    def test_validate_matricula_vacia_retorna_error(self):
        errors = Medico.validate("Ana", "García", "", self.especialidad)
        self.assertTrue(len(errors) > 0)

    # --- new ---

    def test_new_crea_medico_con_datos_validos(self):
        especialidad = Especialidad.objects.create(nombre="Clínica Médica")
        medico, errors = Medico.new("Carlos", "López", "MP-1234", especialidad)
        self.assertEqual(errors, [])
        self.assertIsNotNone(medico)
        self.assertEqual(medico.apellido, "López")
        self.assertTrue(Medico.objects.filter(matricula="MP-1234").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        count_antes = Medico.objects.count()
        medico, errors = Medico.new("", "", "", "")
        self.assertIsNone(medico)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Medico.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        especialidad = Especialidad.objects.create(nombre="Cardiología")
        errors = self.medico.update("Laura", "Romero", "MP-9999", especialidad)
        self.assertEqual(errors, [])
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.especialidad, especialidad)

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.medico.update("", "", "", "")
        self.assertTrue(len(errors) > 0)
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.nombre, "Laura")  # sin cambios

    # TODO: agregar tests para Turno cuando los implementen
    
class PacienteModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo Paciente."""

    def setUp(self):
        # Para crear un paciente, necesitamos un usuario y una obra social
        self.user = User.objects.create_user(username='maxi', password='1234')

        self.obra_social = ObraSocial.objects.create(nombre="IOMA")

        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Juan",
            apellido="Perez",
            email="juan@perez.com",
            telefono="123456",
            dni="11111111",
            obra_social=self.obra_social)
        
    # --- __str__ y métodos simples ---

    def test_str_formato_correcto(self):
        # Verificamos el formato exacto: "Apellido, Nombre"
        self.assertEqual(str(self.paciente), "Perez, Juan")

    def test_puede_solicitar_turno_true(self):
        # Caso feliz: tiene todo
        self.assertTrue(self.paciente.puede_solicitar_turno())

    def test_puede_solicitar_turno_false_sin_obra_social(self):
        # Caso negativo: le quitamos la obra social
        self.paciente.obra_social = None
        self.assertFalse(self.paciente.puede_solicitar_turno())

    def test_puede_solicitar_turno_false_sin_nada(self):
        # Caso negativo extremo: no tiene nada
        self.paciente.telefono = ""
        self.paciente.obra_social = None
        self.assertFalse(self.paciente.puede_solicitar_turno())

    def test_puede_solicitar_turno_false_sin_telefono(self):
        # Caso borde: le quitamos el teléfono y esperamos que sea False
        self.paciente.telefono = ""
        self.assertFalse(self.paciente.puede_solicitar_turno())

    
    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        # Todos los campos OK
        errors = Paciente.validate("Juan", "Perez", "12345678", "juan@test.com", "123456")
        self.assertEqual(errors, [])

    def test_validate_campos_obligatorios_vacios_retorna_errores(self):
        # Probamos que el portero detecte si faltan nombre, apellido o DNI
        errors = Paciente.validate("", "", "", "juan@test.com", "123456")
        self.assertIn("El nombre es obligatorio.", errors)
        self.assertIn("El apellido es obligatorio.", errors)
        self.assertIn("El DNI es obligatorio.", errors)

    def test_validate_dni_duplicado_retorna_error(self):
        # Para que este test funcione, tiene que existir un paciente con ese DNI
        # Usamos el DNI de el setup: "11111111"
        errors = Paciente.validate("Otro", "Persona", "11111111", "otro@test.com", "999")
        self.assertIn("Ya existe un paciente registrado con ese DNI.", errors)

    def test_validate_email_invalido_retorna_error(self):
        # Probamos que detecte si falta el "@"
        errors = Paciente.validate("Juan", "Perez", "99999999", "email-invalido", "123456")
        self.assertIn("El email ingresado no es válido.", errors)

    # --- new ---

    def test_new_crea_paciente_con_datos_validos(self):
        # 1. Preparar un usuario 
        nuevo_user = User.objects.create_user(username="roberto")
        
        # 2. Llamar a new 
        paciente, errors = Paciente.new(
            nuevo_user, "Roberto", "Rubidarte", "roberto@test.com", "654321", "46087375", self.obra_social
        )
        
        # 3. Verificaciones 
        self.assertEqual(errors, [])             # Que no haya errores
        self.assertIsNotNone(paciente)           # Que el objeto no sea None
        self.assertEqual(paciente.nombre, "Roberto") # Que el nombre sea el que pasamos
        self.assertTrue(Paciente.objects.filter(dni="46087375").exists()) # ¡que esté en la base de datos!


    def test_new_con_datos_invalidos_no_crea_paciente(self):
        # 1. Contamos cuántos pacientes hay antes de intentar crear el inválido
        count_antes = Paciente.objects.count()
        
        nuevo_user = User.objects.create_user(username="roberto2")

        paciente, errors = Paciente.new(
            nuevo_user, "", "", "email-invalido", "", "", None
        )

        # 2. Verificaciones
        self.assertIsNone(paciente)
        self.assertTrue(len(errors) > 0) 
        
        # 3. Verificación definitiva: la cantidad en la BD no cambió
        self.assertEqual(Paciente.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        # 1. Usamos self.paciente (el que ya existe gracias al setUp)
        # 2. Llamamos a su método .update() con datos nuevos
        errors = self.paciente.update(
            "Roberto Actualizado", 
            "Rubidarte", 
            "nuevo_email@test.com", 
            "999999", 
            "46087375", 
            self.obra_social
        )
        
        # 3. Verificaciones
        self.assertEqual(errors, []) # Que no haya errores
        
        # 4. Refrescamos para ver los cambios en la base de datos
        self.paciente.refresh_from_db()
        
        # 5. Confirmamos que los campos cambiaron
        self.assertEqual(self.paciente.nombre, "Roberto Actualizado")
        self.assertEqual(self.paciente.email, "nuevo_email@test.com")




    def test_update_con_datos_invalidos_no_modifica(self):
        # Guardamos el nombre original para comparar después
        nombre_original = self.paciente.nombre
        
        # Intentamos actualizar con datos vacíos
        errors = self.paciente.update("", "", "email-invalido", "", "", None)

        # 1. Verificamos que el validador detectó errores
        self.assertTrue(len(errors) > 0)
        
        # 2. Refrescamos para ver si algo cambió en la BD
        self.paciente.refresh_from_db()
        
        # 3. Verificamos que el nombre sigue siendo el original
        # Esto prueba que el update no guardó datos inválidos
        self.assertEqual(self.paciente.nombre, nombre_original)


    def test_update_con_dni_de_otro_paciente_retorna_error(self):
        # 1. Preparar un usuario rival
        nuevo_user = User.objects.create_user(username="joaco")
        
        # 2. Crear al paciente rival
        Paciente.new(
            nuevo_user, "joaco", "Rubidarte", "joaco@test.com", "654321", "12345678", self.obra_social
        )

        # 3. Intentar actualizar nuestro paciente con el DNI del rival 
        errors = self.paciente.update(
            "Juan", "Perez", "juan@perez.com", "123456", "12345678", self.obra_social 
        )

        # 4. Verificación 
        self.assertTrue(len(errors) > 0)

class AusenciaModelTest(TestCase):

        def setUp(self):
          self.especialidad = Especialidad.objects.create(nombre="Pediatría")
          self.medico = Medico.objects.create(
              nombre="Laura", apellido="Romero",
              matricula="MP-9999", especialidad=self.especialidad
          ) 

        def test_validate_fecha_fin_menor_a_inicio_retorna_error(self):
          from datetime import date
          errors = Ausencia.validate("Vacaciones", date(2025, 6, 10), date(2025, 6, 1), )
          self.assertTrue(len(errors) > 0)

    # --- new ---

        def test_new_crea_ausencia_con_datos_validos(self):
            ausencia, errors = Ausencia.new("Vacaciones", date(2025, 6, 1), date(2025, 6, 10), self.medico)
            self.assertEqual(errors, [])
            self.assertIsNotNone(ausencia)
            self.assertTrue(Ausencia.objects.filter(motivo="Vacaciones").exists())

        def test_new_con_datos_invalidos_no_crea(self):
            count_antes = Ausencia.objects.count()
            ausencia, errors = Ausencia.new("", None, None, self.medico)
            self.assertIsNone(ausencia)
            self.assertTrue(len(errors) > 0)
            self.assertEqual(Ausencia.objects.count(), count_antes)

        # --- update ---

        def test_update_modifica_motivo_correctamente(self):
            ausencia, _ = Ausencia.new("Vacaciones", date(2025, 6, 1), date(2025, 6, 10), self.medico)
            errors = ausencia.update("Congreso médico", date(2025, 6, 1), date(2025, 6, 10))
            self.assertEqual(errors, [])
            ausencia.refresh_from_db()
            self.assertEqual(ausencia.motivo, "Congreso médico")

        def test_update_con_datos_invalidos_no_modifica(self):
            ausencia, _ = Ausencia.new("Vacaciones", date(2025, 6, 1), date(2025, 6, 10), self.medico)
            errors = ausencia.update("", None, None)
            self.assertTrue(len(errors) > 0)
            ausencia.refresh_from_db()
            self.assertEqual(ausencia.motivo, "Vacaciones")

class TurnoModelTest(TestCase):
    """Pruebas para el modelo Turno."""

    def setUp(self):
        # crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # crear especialidad
        self.especialidad = Especialidad.objects.create(
            nombre='Cardiologia',
            descripcion='Especialidad en corazon'
        )
        
        # crear medico
        self.medico = Medico.objects.create(
            nombre='Juan',
            apellido='Perez',
            matricula='MP12345',
            especialidad=self.especialidad
        )
        
        # crear obra social
        self.obra_social = ObraSocial.objects.create(
            nombre='OSDE',
            sitio_web='www.osde.com.ar',
            requiere_token=False
        )
        
        # crear paciente
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre='Ana',
            apellido='Gomez',
            email='ana@test.com',
            telefono='123456789',
            dni='40123456',
            obra_social=self.obra_social
        )
        
        # fecha para tests (futuro)
        self.fecha_futura = timezone.now() + timedelta(days=2)

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        """valida que con datos correctos no haya errores."""
        errors = Turno.validate(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Dolor de cabeza'
        )
        self.assertEqual(errors, [])

    def test_validate_sin_medico_retorna_error(self):
        """valida que falle si falta medico."""
        errors = Turno.validate(
            medico=None,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Dolor de cabeza'
        )
        self.assertIn('El medico es obligatorio.', errors)

    def test_validate_sin_paciente_retorna_error(self):
        """valida que falle si falta paciente."""
        errors = Turno.validate(
            medico=self.medico,
            paciente=None,
            fecha_hora=self.fecha_futura,
            motivo='Dolor de cabeza'
        )
        self.assertIn('El paciente es obligatorio.', errors)

    def test_validate_sin_fecha_retorna_error(self):
        """valida que falle si falta fecha."""
        errors = Turno.validate(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=None,
            motivo='Dolor de cabeza'
        )
        self.assertIn('La fecha y hora son obligatorias.', errors)

    def test_validate_sin_motivo_retorna_error(self):
        """valida que falle si falta motivo."""
        errors = Turno.validate(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo=''
        )
        self.assertIn('El motivo es obligatorio.', errors)

    # --- new ---

    def test_new_crea_turno_con_datos_validos(self):
        """prueba que new() cree un turno con datos validos."""
        turno, errors = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Consulta general',
            creado_por=self.user,
            observaciones='Paciente con fiebre'
        )
        
        self.assertEqual(errors, [])
        self.assertIsNotNone(turno)
        self.assertEqual(turno.medico, self.medico)
        self.assertEqual(turno.paciente, self.paciente)
        self.assertEqual(turno.motivo, 'Consulta general')
        self.assertEqual(turno.estado, 'pendiente')
        self.assertEqual(turno.creado_por, self.user)
        self.assertTrue(Turno.objects.filter(paciente=self.paciente).exists())

    def test_new_con_datos_invalidos_no_crea(self):
        """prueba que new() no cree turno con datos invalidos."""
        count_antes = Turno.objects.count()
        turno, errors = Turno.new(
            medico=None,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo=''
        )
        
        self.assertIsNone(turno)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Turno.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        """prueba que update() modifique el turno correctamente."""
        turno, _ = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Original',
            creado_por=self.user
        )
        
        nueva_fecha = self.fecha_futura + timedelta(hours=2)
        errors = turno.update(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=nueva_fecha,
            motivo='Modificado'
        )
        
        self.assertEqual(errors, [])
        turno.refresh_from_db()
        self.assertEqual(turno.motivo, 'Modificado')
        self.assertEqual(turno.fecha_hora, nueva_fecha)

    def test_update_con_datos_invalidos_no_modifica(self):
        """prueba que update() no modifique con datos invalidos."""
        turno, _ = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Original',
            creado_por=self.user
        )
        
        motivo_original = turno.motivo
        errors = turno.update(
            medico=None,
            paciente=None,
            fecha_hora=None,
            motivo=''
        )
        
        self.assertTrue(len(errors) > 0)
        turno.refresh_from_db()
        self.assertEqual(turno.motivo, motivo_original)

    # --- cancelar ---

    def test_cancelar_cambia_estado_a_cancelado(self):
        """prueba que cancelar() cambie estado a cancelado."""
        turno, _ = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Consulta',
            creado_por=self.user
        )
        
        turno.cancelar()
        turno.refresh_from_db()
        self.assertEqual(turno.estado, 'cancelado')

    # --- aceptar ---

    def test_aceptar_cambia_estado_a_confirmado(self):
        """prueba que aceptar() cambie estado a confirmado."""
        turno, _ = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Consulta',
            creado_por=self.user
        )
        
        turno.aceptar()
        turno.refresh_from_db()
        self.assertEqual(turno.estado, 'confirmado')

    # --- estadoDisponibilidad ---

    def test_estado_disponibilidad_retorna_estado_actual(self):
        """prueba que estadoDisponibilidad() retorne el estado actual."""
        turno, _ = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Consulta',
            creado_por=self.user
        )
        
        self.assertEqual(turno.estadoDisponibilidad(), 'pendiente')
        
        turno.aceptar()
        self.assertEqual(turno.estadoDisponibilidad(), 'confirmado')
        
        turno.cancelar()
        self.assertEqual(turno.estadoDisponibilidad(), 'cancelado')

    # --- metodos de estado ---

    def test_esta_pendiente(self):
        """prueba que esta_pendiente() funcione correctamente."""
        turno, _ = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Consulta',
            creado_por=self.user
        )
        
        self.assertTrue(turno.esta_pendiente())
        turno.aceptar()
        self.assertFalse(turno.esta_pendiente())

    def test_esta_confirmado(self):
        """prueba que esta_confirmado() funcione correctamente."""
        turno, _ = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Consulta',
            creado_por=self.user
        )
        
        self.assertFalse(turno.esta_confirmado())
        turno.aceptar()
        self.assertTrue(turno.esta_confirmado())

    def test_esta_cancelado(self):
        """prueba que esta_cancelado() funcione correctamente."""
        turno, _ = Turno.new(
            medico=self.medico,
            paciente=self.paciente,
            fecha_hora=self.fecha_futura,
            motivo='Consulta',
            creado_por=self.user
        )
        
        self.assertFalse(turno.esta_cancelado())
        turno.cancelar()
        self.assertTrue(turno.esta_cancelado())

class ObraSocialModelTest(TestCase):

    def setUp(self):
        self.obra_social = ObraSocial.objects.create(nombre="IOMA")

    def test_str_retorna_nombre(self):
        self.assertEqual(str(self.obra_social), "IOMA")