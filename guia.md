Tareas que se me dieron a mi para sumar al proyecto:


---

## Buenas prácticas: triple validación

Una regla de negocio importante (por ejemplo, que la fecha de fin no puede ser anterior a la de inicio) debe validarse en tres capas:

1. **Frontend / Form (feedback visual):** el formulario Django con `clean()` o `clean_<campo>()` devuelve errores al usuario junto al campo que los causó. Es la primera barrera y la que da mejor UX.

2. **Modelo / `validate()`:** el método `validate()` en el modelo centraliza las reglas de negocio. Se llama desde `new()` y `update()`, por lo que protege cualquier vía de entrada: la vista web, el admin de Django, comandos de management, etc.

3. **Base de datos / `CheckConstraint`:** el constraint a nivel DB es la última barrera. No depende de Python ni de Django — si alguien logra ejecutar un `INSERT` o `UPDATE` directamente, la base de datos lo rechaza igual.

**¿Por qué las tres?**
- El front puede bypassearse (JS deshabilitado, requests directas).
- El form solo protege la vista web.
- El modelo protege todas las entradas de datos.
- La DB protege ante errores del propio código.

Cada capa es independiente. Que existan las tres no es redundancia, es defensa en profundidad.

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
