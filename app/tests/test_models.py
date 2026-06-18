"""Pruebas unitarias de los modelos."""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

# Importamos cada modelo de su archivo correspondiente
from app.models.especialidad import Especialidad
from app.models.medico import Medico
from app.models.obra_social import ObraSocial
from app.models.paciente import Paciente
from app.models.turno import Turno
from app.models.ausencia import Ausencia


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
    """Verifica comportamiento básico y validaciones del modelo Medico."""

    def setUp(self):
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

    def test_str_incluye_apellido_y_nombre(self):
        self.assertIn("Romero", str(self.medico))
        self.assertIn("Laura", str(self.medico))

    def test_nombre_completo(self):
        self.assertEqual(self.medico.nombre_completo(), "Laura Romero")

    def test_cantidad_turnos_inicial_es_cero(self):
        self.assertEqual(self.medico.cantidad_turnos(), 0)

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = Medico.validate("Ana", "García", "MP-0001", self.especialidad)
        self.assertEqual(errors, [])

    def test_new_crea_medico_con_datos_validos(self):
        medico, errors = Medico.new("Carlos", "López", "MP-1234", self.especialidad)
        self.assertEqual(errors, [])
        self.assertIsNotNone(medico)
        self.assertEqual(medico.apellido, "López")

    def test_new_con_obras_sociales_asigna_correctamente(self):
        obra = ObraSocial.objects.create(nombre="OSDE")
        medico, errors = Medico.new("Juan", "Perez", "MP-5555", self.especialidad, obras_sociales=[obra])
        self.assertEqual(errors, [])
        self.assertIn(obra, medico.obras_sociales.all())
    
    def test_update_actualiza_obras_sociales(self):
        obra1 = ObraSocial.objects.create(nombre="OSDE")
        obra2 = ObraSocial.objects.create(nombre="Swiss Medical")
        self.medico.update("Laura", "Romero", "MP-9999", self.especialidad, obras_sociales=[obra1])
        self.medico.refresh_from_db()
        self.assertIn(obra1, self.medico.obras_sociales.all())
        
        self.medico.update("Laura", "Romero", "MP-9999", self.especialidad, obras_sociales=[obra2])
        self.medico.refresh_from_db()
        self.assertNotIn(obra1, self.medico.obras_sociales.all())
        self.assertIn(obra2, self.medico.obras_sociales.all())
    
class PacienteModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo Paciente."""

    def setUp(self):
         # Para crear un paciente, necesitamos un usuario y una obra social
         self.user = User.objects.create_user(username='maxi', password='1234')

         self.obra_social = ObraSocial.objects.create(nombre = "IOMA")

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

      def setUp(self):
          self.especialidad = Especialidad.objects.create(nombre="Pediatría")
          self.medico = Medico.objects.create(
              nombre="Laura", apellido="Romero",
              matricula="MP-9999", especialidad=self.especialidad
          )
          self.fecha_valida = timezone.now() + timedelta(days=5)

      # --- validate ---

      def test_validate_datos_correctos_retorna_lista_vacia(self):
          errors = Turno.validate(self.medico, "Misael", "Casagrande", self.fecha_valida, True, "Consulta")
          self.assertEqual(errors, [])

      def test_validate_sin_medico_retorna_error(self):
          errors = Turno.validate(None, "Misael", "Casagrande", self.fecha_valida, True, "Consulta")
          self.assertTrue(len(errors) > 0)

      # --- new ---

      def test_new_crea_turno_con_datos_validos(self):
          turno, errors = Turno.new(self.medico, "Misael", "Casagrande", self.fecha_valida, True, "Consulta")
          self.assertEqual(errors, [])
          self.assertIsNotNone(turno)
          self.assertTrue(Turno.objects.filter(paciente_apellido="Casagrande").exists())

      def test_new_con_datos_invalidos_no_crea(self):
          count_antes = Turno.objects.count()
          turno, errors = Turno.new(None, "", "", None, None, "")
          self.assertIsNone(turno)
          self.assertTrue(len(errors) > 0)
          self.assertEqual(Turno.objects.count(), count_antes)

      # --- update ---

      def test_update_modifica_observaciones_correctamente(self):
          turno, _ = Turno.new(self.medico, "Misael", "Casagrande", self.fecha_valida, True, "Consulta")
          nueva_fecha = timezone.now() + timedelta(days=10)
          errors = turno.update(self.medico, "Misael", "Casagrande", nueva_fecha, True, "Nueva observación")
          self.assertEqual(errors, [])
          turno.refresh_from_db()
          self.assertEqual(turno.observaciones, "Nueva observación")

      # --- cancelar ---

      def test_cancelar_cambia_disponibilidad_a_false(self):
          turno, _ = Turno.new(self.medico, "Misael", "Casagrande", self.fecha_valida, True, "Consulta")
          turno.cancelar()
          turno.refresh_from_db()
          self.assertFalse(turno.disponibilidad)

      # --- aceptar ---

      def test_aceptar_cambia_disponibilidad_a_true(self):
          turno, _ = Turno.new(self.medico, "Misael", "Casagrande", self.fecha_valida, False, "Consulta")
          turno.aceptar()
          turno.refresh_from_db()
          self.assertTrue(turno.disponibilidad)

      # --- estadoDisponibilidad ---

      def test_estado_disponibilidad_refleja_cancelacion(self):
          turno, _ = Turno.new(self.medico, "Misael", "Casagrande", self.fecha_valida, True, "Consulta")
          self.assertTrue(turno.estadoDisponibilidad())
          turno.cancelar()
          turno.refresh_from_db()
          self.assertFalse(turno.estadoDisponibilidad())

class ObraSocialModelTest(TestCase):
    """Verifica comportamiento de ObraSocial."""

    def setUp(self):
        self.obra_social = ObraSocial.objects.create(nombre="IOMA")

    def test_str_retorna_nombre(self):
        self.assertEqual(str(self.obra_social), "IOMA")

    def test_validate_nombre_vacio_retorna_error(self):
        errors = ObraSocial.validate("")
        self.assertTrue(len(errors) > 0)

    def test_validate_nombre_duplicado_retorna_error(self):
        errors = ObraSocial.validate("IOMA")
        self.assertTrue(len(errors) > 0)

    def test_new_crea_obra_social_valida(self):
        obra, errors = ObraSocial.new("OSDE")
        self.assertEqual(errors, [])
        self.assertIsNotNone(obra)

    def test_medicos_disponibles_cuenta_correctamente(self):
        especialidad = Especialidad.objects.create(nombre="Pediatría")
        medico, _ = Medico.new("Juan", "Perez", "MP-111", especialidad, obras_sociales=[self.obra_social])
        self.assertEqual(self.obra_social.medicos_disponibles, 1)