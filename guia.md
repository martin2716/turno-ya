Tareas que se me dieron a mi para sumar al proyecto:

Area	Subtarea	Que tiene que hacer exactamente	Entregable concreto	Criterio que cubre	Dependencia	Estado	Notas
- Modelos	Revisar Ausencia	Confirmar que fechas, motivo y relacion con medico sirvan para el flujo final	Modelo Ausencia consolidado	Modelo correcto	Repo actual	✅ COMPLETO	Modelo tiene motivo, fecha_inicio, fecha_fin, FK a Medico, CheckConstraint fecha_fin>=fecha_inicio, y metodos validate/new/update correctos
- Forms	Crear formulario de ausencia	Implementar validacion de fechas y conflictos basicos	Formulario de ausencia	Formulario de creacion de ausencias / validacion personalizada	Modelo Ausencia estable	⏳ PENDIENTE	No existe forms.py ni carpeta forms/. Proximo paso: crear app/forms/ con __init__.py y ausencia.py
- CBV	Implementar DetalleMedicoView	Mostrar datos del medico, especialidad, obras sociales y ausencias	Detalle de medico final	Detalle de medico	Medico y Ausencia estables	⏳ PENDIENTE	URL medicos/<int:pk>/ esta comentada en urls.py. Vista no implementada en views.py
- CBV	Implementar vista de nueva ausencia	Usar formulario de ausencia y proteger accion	Alta de ausencia funcional	Formulario de creacion de ausencias	Form de ausencia listo	⏳ PENDIENTE	Depende de que el form de ausencia este listo primero
- Templates	Crear template de detalle de medico	Mostrar informacion clara y ordenada con Bootstrap	Template detalle medico	Templates Bootstrap 5 responsivos	DetalleMedicoView lista	⏳ PENDIENTE	No existe detalle_medico.html. Debe mostrar obras sociales y ausencias del medico
- Templates	Apoyar templates del flujo de turnos	Revisar lista_turnos, alta de turno y acciones visibles junto a Misael	Templates de turnos coherentes	UX funcional	Vistas de turno listas	⏳ PENDIENTE	lista_turnos.html existe pero NuevoTurnoView y CancelarTurnoView no estan implementadas. Coordinar con Misael
- Templates	Pulir templates actuales	Revisar home, lista_medicos, lista_turnos, lista_pacientes, login y signup	Templates consistentes	UX cuidada y responsive	Vistas finales	⏳ PENDIENTE	Los templates existen (8 en total). Falta revision de calidad y consistencia visual
- Frontend	Probar vistas en mobile y desktop	Detectar tablas rotas, navbar incomoda o formularios desbordados	Lista de ajustes responsive	Templates Bootstrap 5 responsivos	Templates finales	⏳ PENDIENTE	Hacer pruebas reales
- Tests	Revisar y completar tests de Ausencia	Ajustar si cambia la validacion o el flujo	Tests de Ausencia pasando	Todos los modelos testeados y con tests pasando	Modelo/form final	✅ COMPLETO (modelo) / ⏳ PENDIENTE (form y vista)	AusenciaModelTest tiene 6 tests cubriendo validate/new/update. Faltan tests del formulario y de la vista cuando esten listos
- Tests	Agregar tests de vistas y forms de turnos y ausencias	Cubrir formularios, alta, acciones y permisos basicos de esas vistas	Robustez funcional	Evidencia de funcionamiento	Vistas y forms listos	⏳ PENDIENTE	No hay tests de vistas ni de forms todavia. Coordinar con Misael
- Pulido	Agregar mensajes vacios, titulos y textos coherentes	Mejorar usabilidad general sin usar JS complejo	Pulido visual final	Frontend sin JS complejo / UX cuidada	Vistas finales	⏳ PENDIENTE	Suma mucho en evaluacion

---

## Estado general del proyecto (relevado 2026-06-23)

### ✅ COMPLETADO

- **Modelos**: Los 6 modelos estan implementados con el patron validate/new/update
  - Especialidad, Medico, Paciente, ObraSocial, Turno, Ausencia
  - Todos en app/models/ como carpeta con __init__.py
- **Ausencia**: modelo completo con CheckConstraint y los 3 metodos requeridos
- **Admin**: 5 modelos registrados con list_display, search_fields y list_filter (falta Ausencia)
- **Autenticacion**: login, logout y registro funcionando con CBV
- **Navbar dinamica**: cambia segun autenticacion y rol
- **Permisos**: LoginRequiredMixin y PermissionRequiredMixin aplicados en vistas
- **Vistas CBV implementadas**: HomeView, ListaMedicosView, ListaTurnosView, RegistroUsuarioView, ListaPacientesView, PerfilUpdateView, PerfilCreateView (7 vistas)
- **Templates existentes**: base.html, login.html, signup.html, home.html, lista_medicos.html, lista_pacientes.html, lista_turnos.html, perfil_form.html (8 templates)
- **Tests de modelos**: 48+ tests cubriendo todos los modelos (test_models.py)
- **Filtro por especialidad** en lista de medicos implementado
- **Migraciones** commiteadas y funcionales

### ⏳ PENDIENTE (mis tareas)

1. Crear carpeta app/forms/ con __init__.py y AusenciaForm (ausencia.py)
2. Implementar DetalleMedicoView en views.py y descomentar su URL
3. Implementar NuevaAusenciaView en views.py
4. Crear template detalle_medico.html
5. Crear template nueva_ausencia.html
6. Registrar Ausencia en admin.py
7. Agregar tests de formularios y vistas (ausencia y turnos)
8. Pulir templates existentes (UX, mensajes vacios, responsivo mobile)

### ⚠️ PENDIENTE (vistas que faltan del proyecto general, coordinar con el grupo)

- NuevoTurnoView (URL comentada en urls.py)
- CancelarTurnoView (URL comentada en urls.py)
- AceptarTurnoView (no existe ni la URL)
- Templates de turno relacionados con las vistas anteriores
