"""Pruebas unitarias del modelo Medico."""

from django.test import TestCase
from app.models import Medico


class MedicoModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo."""

    def setUp(self):
        self.medico = Medico.objects.create(nombre="Carlos", apellido="Lopez", matricula="123", especialidad="Cardio")
    self.fechaValida = timezone.now() + timedelta(days=5)

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
        errors = Medico.validate("Ana", "García", "MP-0001", "Cardiología")
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Medico.validate("", "García", "MP-0001", "Cardiología")
        self.assertTrue(len(errors) > 0)

    def test_validate_matricula_vacia_retorna_error(self):
        errors = Medico.validate("Ana", "García", "", "Cardiología")
        self.assertTrue(len(errors) > 0)

    # --- new ---

    def test_new_crea_medico_con_datos_validos(self):
        medico, errors = Medico.new("Carlos", "López", "MP-1234", "Clínica Médica")
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
        errors = self.medico.update("Laura", "Romero", "MP-9999", "Cardiología")
        self.assertEqual(errors, [])
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.especialidad, "Cardiología")

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.medico.update("", "", "", "")
        self.assertTrue(len(errors) > 0)
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.nombre, "Laura")  # sin cambios

    # TODO: agregar tests para Paciente y Turno cuando los implementen
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    class TurnoModelTest(TestCase):
        #Test de turnos:

        from django.utils import timezone
from datetime import timedelta

class MedicoModelTest(TestCase):
    def setUp(self):
        self.medico =Medico.objects.create(nombre="Laura",
                                            apellido="Romero",
                                            matricula="MP-9999",
                                            especialidad="Pediatría")
        
        #Validate:Cubrir al menos caso valido, fecha invalida y conflicto basico
        def testTurnoValido(self):
            errors = Turno.validate(
            medico=self.medico,
            paciente_nombre="Misael",
            paciente_apellido="Casagrande",
            fecha="2024-12-01 10:00:00",
            disponibilidad=True,
            observaciones="Consulta"
            )
            print(errors)
            self.assertEqual(errors, [])#asser si retorna error.equals([])
            
            
        def  testFechaInvalida(self):
            errors = Turno.validate(
                medico=self.medico,
                paciente_nombre="Misael",
                paciente_apellido="Casagrande",
                fecha="2023-12-01 10:00:00",
                disponibilidad=True,
                observaciones="Consulta"
            )
            self.assertTrue(len(errors) > 0)
            
        def testConflictoTurno(self):
            Turno.objects.create(
            medico=self.medico,
            paciente_nombre="Paciente Y",
            paciente_apellido="Apellido Y",
            fecha=self.fechaValida,
            disponibilidad=True,
            observaciones="Primer turno"
            )
            conflictos = Turno.objects.filter(medico=self.medico, fecha=self.fechaValida)
            self.assertTrue(conflictos.exists())
            
        #new:Verificar creacion correcta y bloqueo por errores
        
        def testNewTurnoValido(self):
            turno, errors = Turno.new(
            medico=self.medico,
            paciente_nombre="Misael",
            paciente_apellido="Casagrande",
            fecha=self.fechaValida,
            disponibilidad=True,
            observaciones="Consulta"
            )
            self.assertIsNotNone(turno)
            self.assertEqual(errors, [])

        def testNewTurnoInvalido(self):
            turno, errors = Turno.new(
                medico=None,
                paciente_nombre="",
                paciente_apellido="",
                fecha=None,
                disponibilidad=None,
                observaciones=""
            )
            self.assertIsNone(turno)
            self.assertTrue(len(errors) > 0)
                
        
    #metodos de negocio:Probar cancelar(), aceptar() u otra logica elegida
        
        def testCancelarTurno(self):
            turno, _ = Turno.new(
            medico=self.medico,
            paciente_nombre="Misael",
            paciente_apellido="Casagrande",
            fecha=self.fechaValida,
            disponibilidad=True,
            observaciones="Consulta"
            )
            turno.cancelar()
            self.assertEqual(turno.disponibilidad, False)

        def testAceptarTurno(self):
            turno, _ = Turno.new(
                medico=self.medico,
                paciente_nombre="Misael",
                paciente_apellido="Casagrande",
                fecha=self.fechaValida,
                disponibilidad=False,
                observaciones="Consulta"
            )
            turno.aceptar()
            self.assertEqual(turno.disponibilidad, True)

        def testEstadoDisponibilidad(self):
            turno, _ = Turno.new(
                medico=self.medico,
                paciente_nombre="Misael",
                paciente_apellido="Casagrande",
                fecha=self.fechaValida,
                disponibilidad=True,
                observaciones="Consulta"
            )
            self.assertEqual(turno.estadoDisponibilidad(), True)
            
            turno.cancelar()
            self.assertEqual(turno.estadoDisponibilidad(), False)
