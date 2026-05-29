"""Pruebas unitarias del modelo Medico."""

from django.test import TestCase
from app.models import Especialidad, Medico


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

    # TODO: agregar tests para Paciente y Turno cuando los implementen
