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

- **Modelos**: Los 6 modelos implementados con el patron validate/new/update
  - Todos en app/models/ como carpeta con __init__.py
- **Paciente**: CheckConstraints agregados para todos los campos obligatorios. Validaciones de formato (solo letras en nombre/apellido, solo numeros en DNI/telefono) en validate() y en el form.
- **Ausencia**: modelo completo con CheckConstraint y los 3 metodos requeridos
- **Admin**: modelos registrados con list_display, search_fields y list_filter
- **Autenticacion**: login, logout y registro funcionando con CBV
- **Navbar dinamica**: cambia segun autenticacion, rol y permisos
- **Permisos**: LoginRequiredMixin y PermissionRequiredMixin aplicados en vistas
- **Forms**: reorganizados en carpeta app/forms/ con __init__.py que exporta todo
  - AusenciaForm, RegistroPacienteForm, PerfilUsuarioForm en sus archivos correspondientes
  - Triple validacion aplicada: form + validate() + CheckConstraint
- **Vistas CBV implementadas**: HomeView, ListaMedicosView, ListaTurnosView, RegistroUsuarioView, ListaPacientesView, PerfilUsuarioView, ListaAusenciasView, NuevaAusenciaView, DetalleMedicoView
- **Registro de paciente**: crea User y Paciente en un unico paso (RegistroPacienteForm)
- **Perfil de paciente**: vista unificada PerfilUsuarioView que edita User y Paciente juntos
- **DetalleMedicoView**: muestra info, obras sociales y ausencias del medico
- **Templates**: login.html, signup.html, perfil_usuario.html, nueva_ausencia.html, detalle_medico.html con Bootstrap aplicado correctamente (form-control, form-select, is-invalid, bloques de error)
- **Filtro reactivo** por especialidad en lista de medicos (submit automatico al cambiar el select)
- **Home y lista de medicos**: accesibles sin login (acuerdo con el profesor)
- **Migraciones**: commiteadas y funcionales

### ⏳ PENDIENTE (mis tareas)

1. Registrar Ausencia en admin.py
2. Agregar tests de formularios y vistas (ausencia, paciente y registro)
3. Definir rol Medico con usuario asociado (pendiente decision del grupo)
4. Actualizar PerfilPacienteRequiredMixin cuando se defina el rol Medico

### ⚠️ PENDIENTE (vistas que faltan del proyecto general, coordinar con el grupo)

- NuevoTurnoView (URL comentada en urls.py)
- CancelarTurnoView (URL comentada en urls.py)
- AceptarTurnoView (no existe ni la URL)
- Templates de turno relacionados con las vistas anteriores
- Modelo de Medico con usuario asociado (OneToOneField a User)
