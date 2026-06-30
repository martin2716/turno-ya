# Diagnóstico de ramas y plan de unificación — TurnoYa

> Relevado el 2026-06-29. Comparación entre `main` y la rama `mi-cambios-mergeados`.

> **Nota:** este documento debe leerse como un registro técnico e histórico del proceso de unificación de ramas. No reemplaza la verificación funcional final ni implica por sí solo que el estado actual del proyecto coincida exactamente con cada conclusión acá escrita.

> ⚠️ **PENDIENTE IMPORTANTE (directiva no-JS):** `app/templates/clinica/lista_medicos.html`
> usa `onchange="this.form.submit()"` (JS de main, no pactado). Es la única violación
> que queda de la directiva de no usar JavaScript. Decidido dejarlo así por ahora, pero
> hay que resolverlo. Dos soluciones posibles (sin JS propio):
>
> 1. **Botón "Filtrar":** quitar el `onchange` y agregar un `<button type="submit">`.
>    Mantiene el `<select>`. Dos clics. Solo toca el template.
> 2. **Dropdown de Bootstrap (preferida):** reemplazar el `<select>` por un dropdown
>    de Bootstrap donde cada especialidad es un `<a href="?especialidad=X">`. Filtra en
>    un solo clic, usa el bundle de Bootstrap (pactado) para abrir/cerrar — cero JS
>    propio. Toca el template; opcionalmente +2 líneas en `ListaMedicosView` para que
>    el botón muestre la especialidad seleccionada (`especialidad_seleccionada`).
>    Nota: disparar al *seleccionar* en un `<select>` real es imposible sin JS; el
>    dropdown lo logra porque son links, no un `<select>`.

## 1. Contexto

La rama `mi-cambios-mergeados` implementa el **flujo completo de pedir turno**
(seleccionar especialidad → médicos disponibles → horarios → confirmar), que `main`
no tiene. Pero al hacerlo divergió fuerte: reestructuró archivos, cambió el modelo
`Turno` y regresó varias cosas que `main` ya tenía resueltas.

**Un `git merge` directo entre las ramas NO es viable:** los modelos pasaron de
carpeta (`app/models/*.py` en `main`) a archivo único (`app/models.py` en esta rama).
Git no lo ve como el mismo archivo modificado, sino como borrados + altas. El merge
resucitaría los archivos de `main` y dejaría `Turno` definido dos veces, en esquemas
incompatibles. El árbol resultante quedaría roto y habría que desarmarlo a mano igual.

## 2. Qué tiene cada rama

### `main` tiene (y esta rama PERDIÓ)

| Área | Detalle |
|---|---|
| Docs de comportamiento | `consigna.md`, `guia.md`, `usabilidad.md` — definición canónica del proyecto. Borradas en esta rama. |
| Disciplina de permisos | `PerfilPacienteRequiredMixin`, `PermissionRequiredMixin` por vista. Esta rama usa `LoginRequiredMixin` pelado en todo. |
| Registro unificado | `RegistroUsuarioView` (FormView) + `RegistroPacienteForm` → crea User+Paciente en un paso. Esta rama lo regresó a un `UserCreationForm` pelado. |
| Perfil de usuario | `PerfilUsuarioView` + `PerfilUsuarioForm` + template. |
| Ausencias (UI) | `ListaAusenciasView`, `NuevaAusenciaView`, `AusenciaForm` + templates. |
| Detalle de médico | `DetalleMedicoView` + template. |
| Roles/grupos | comando `setup_groups`. |
| Estructura + patrón | modelos en carpeta con `validate/new/update` en todos. `obras_sociales` M2M en Medico. Tests más amplios. |

### Esta rama tiene (y `main` no)

- Flujo de pedir turno (funcionalidad central, verificada end-to-end).
- `Turno` como FK real (`paciente`, `fecha_hora`, `estado`, `motivo`, `creado_por`).
- `hora_inicio` / `hora_fin` en Medico (parche — ver punto 4).
- `BuscarPacientesView` (búsqueda JSON), `CancelarTurnoView`, `AceptarTurnoView`.

## 3. Lo que está FALLANDO en el flujo actual

1. **Rol Médico inexistente.** `Medico` no tiene relación con `User`. El médico no
   puede loguearse ni aceptar/rechazar turnos: `AceptarTurnoView` lo permite solo a
   `is_staff` (admin) como parche. → Incumple `usabilidad.md` ("El médico puede aceptar
   o rechazar turnos").
2. **No existe acción "rechazar"** del médico, solo "aceptar" (pasa a `confirmado`).
3. **Horario como parche.** Dos `TimeField` en `Medico` no modelan almuerzo, turnos
   partidos, ni horarios por día. Debería ser un modelo `FranjaHoraria` (FK a Medico).
4. **`ConfirmarTurnoView` parchada.** El `try/except` que retornaba `redirect()` dentro
   de `get_context_data()` (inválido en Django) se movió a `dispatch()`. La causa raíz
   es el registro no unificado (ver punto siguiente).
5. **Registro regresado.** Al volver a `UserCreationForm` pelado, se pueden crear `User`
   sin `Paciente`, que es justo lo que provoca el bug parchado en el punto 4. En `main`
   no pasaría.
6. **Patrón `validate/new/update` abandonado en `Turno`**, rompiendo la consistencia con
   el resto del proyecto (requisito de cátedra según `guia.md`).

## 4. Decisión de base

**`main` es la base.** Se porta el flujo de turnos hacia `main`, no al revés.

Razón: llevar el flujo a `main` es traer **una** feature cohesiva a una base bien
estructurada. Hacer lo inverso obliga a re-portar **muchas** cosas (docs, permisos,
registro unificado, ausencias, perfil, detalle médico, patrón, tests) sobre una base
que regresó.

## 5. Plan de portado (sobre `main`)

### Fase 0 — Preparación
- [ ] `git checkout main && git checkout -b feat/flujo-pedir-turno`
- **Decisiones del grupo (RESUELTAS 2026-06-29):**
  - Se implementa el modelo **`FranjaHoraria`** (no el parche `hora_inicio/fin`).
  - **`Medico` debe poder ser un `User`** (rol médico habilitado).
  - Se **mantienen** `validate/new/update` en `Turno`.

### Fase 1 — Modelo (lo más delicado) — ✅ COMPLETA
- [x] Reescrito `app/models/turno.py`: `paciente` (FK), `fecha_hora`, `estado`
      (choices), `motivo`, `observaciones`, `creado_por` (FK User), `created_at`,
      `updated_at`. Mantiene `validate/new/update` + transiciones
      `aceptar/rechazar/cancelar/finalizar` (rechazar = cancelado).
- [x] `Medico`: agregado `usuario = OneToOneField(User, null=True)` para el rol médico.
- [x] Creado modelo `FranjaHoraria` (FK Medico, `dia_semana`, `hora_inicio`,
      `hora_fin`) con `validate/new/update` y CheckConstraint hora_fin > hora_inicio.
- [x] Migración inicial regenerada (Opción B: se borró el `db.sqlite3` y el
      `0001_initial.py` viejo; el viejo queda en historial de git). `migrate` OK.
      **⚠️ Al mergear: los compañeros deben resetear su DB local y recargar fixtures.**
- [x] Adaptados `turnos.json` (esquema nuevo + 2 turnos pendientes de prueba) y nuevo
      `franjas.json` (médicos 1-7, lunes a viernes 09-17). `loaddata` OK.
- [x] Corregido `admin.py`: `TurnoAdmin` a campos nuevos + registrado `FranjaHoraria`.

### Fase 2 — Vistas (adaptadas a la estructura de `main`) — ✅ COMPLETA
- [x] Portadas `SeleccionarEspecialidadView`, `MedicosDisponiblesView`,
      `TurnosDisponiblesView`, `ConfirmarTurnoView`, `CancelarTurnoView`,
      `AceptarTurnoView`, `RechazarTurnoView`, `BuscarPacientesView`.
- [x] Vistas del flujo usan `PerfilPacienteRequiredMixin` (de main) → el parche del
      `dispatch` de la otra rama ya no hace falta, el chequeo es por diseño.
- [x] `ConfirmarTurnoView` crea el turno con `Turno.new()` (respeta el patrón).
- [x] `AceptarTurnoView`/`RechazarTurnoView`: validan
      `turno.medico.usuario == request.user` (o staff). POST directo, sin página.
- [x] Lógica de slots reescrita: lee de `FranjaHoraria` (`slots_libres_de_medico`).
      Corregido bug de timezone (naive vs aware) con `timezone.make_aware`.
- [x] **Divergencia aprobada:** `ListaTurnosView` pasó de `PermissionRequiredMixin`
      (`view_turno`) a `LoginRequiredMixin` + filtrado por rol, para que paciente y
      médico vean sus turnos. Coherente con `usabilidad.md`.

### Fase 3 — Templates y URLs — ✅ COMPLETA
- [x] Portados `seleccionar_especialidad.html` (limpiada basura final),
      `medicos_disponibles.html` (sacada la columna de horario que usaba campos
      eliminados), `turnos_disponibles.html`, `confirmar_turno.html` (JS adaptado al
      JSON `{id, texto}` y URL con `{% url %}`).
- [x] Creado `confirmar_cancelacion.html` (no existía; cancelar con confirmación).
- [x] Reescrito `lista_turnos.html` a los campos nuevos + botones aceptar/rechazar
      (médico/staff) y cancelar (paciente dueño/staff).
- [x] Agregadas las rutas del flujo a `app/urls.py`.
- [x] Navbar: agregado "Pedir Turno" (staff o paciente) y relajado el link "Turnos"
      a todo autenticado (la vista ahora filtra por rol).
- [x] **Directiva no-JS:** `confirmar_turno.html` se reescribió sin `<script>`/`<style>`
      (el admin elige paciente con un `<select>` server-side). Se eliminó
      `BuscarPacientesView` + URL + imports `JsonResponse`/`Q` (solo servían al `fetch`).
      Bootstrap CDN en `base.html` queda (pactado). **Pendiente grupo:**
      `lista_medicos.html` usa `onchange="this.form.submit()"` (JS de main no pactado).

### Fase 4 — Verificación — 🔄 EN CURSO
- [x] Flujo como **paciente**: sacar turno y cancelar → OK.
- [x] Flujo como **médico**: aceptar/rechazar turnos asignados → OK (requiere
      asociar el `User` a un `Medico` desde el admin).
- [x] Flujo como **admin**: sacar turno a otro + aceptar/rechazar/cancelar.
- [x] Tests de modelo: reescrito `TurnoModelTest` al esquema nuevo (validate, new,
      update, duplicado, transiciones aceptar/rechazar/cancelar/finalizar) + nuevo
      `FranjaHorariaModelTest`. **58 tests en verde.**
- [ ] **PENDIENTE — Tests de vistas/flujo** (recomendado, no hecho aún). Cubren la
      lógica más riesgosa (permisos por rol), que los tests de modelo NO tocan. Casos:
      · Anónimo es redirigido al login en vistas no públicas (ej. `DetalleMedicoView`,
        flujo de turnos); home y lista de médicos siguen públicas.
      · Usuario sin perfil de `Paciente` → `PerfilPacienteRequiredMixin` lo manda a home.
      · Booking end-to-end: paciente saca turno → queda `pendiente` y a su nombre.
      · `ListaTurnosView` filtra por rol: paciente ve solo los suyos, médico solo los
        asignados, admin todos.
      · `AceptarTurnoView`/`RechazarTurnoView`: solo el médico asignado o staff; un
        tercero no puede; solo sobre `pendiente`.
      · `CancelarTurnoView`: solo dueño o staff.
      · Generación de slots desde `FranjaHoraria` (médico sin franjas no aparece).
- [ ] Recién entonces, proponer el merge de `feat/flujo-pedir-turno` a `main`.

**Bugs encontrados y corregidos durante la verificación:**
- `DetalleMedicoView` era pública (sin `LoginRequiredMixin`) → violaba `usabilidad.md`
  (solo home y lista de médicos son públicos). Corregido.
- UX: en `lista_medicos.html` los médicos figuraban como links incluso sin login
  (rebotaban al login). Ahora son link solo si el usuario está autenticado.
- UX: "Cancelar" y "Rechazar" aparecían juntos para el admin en turnos pendientes
  (ambiguo, hacían lo mismo). Se separó por estado/rol en `lista_turnos.html`:
  · `pendiente` → médico/admin: **Aceptar/Rechazar**; paciente dueño: **Cancelar**.
  · `confirmado` → paciente dueño y admin: **Cancelar**.
  (El médico no cancela confirmados — coherente con `CancelarTurnoView`.)

**Aprendizajes / aclaraciones de roles (de la verificación):**
- El médico NO saca turnos (el flujo "Pedir Turno" requiere `Paciente`); el médico
  acepta/rechaza los asignados. Roles según qué perfil tiene el `User`.
- Un `Medico` recién creado no tiene `FranjaHoraria` → no aparece como disponible
  para reservar hasta que se le carguen franjas.

## 6. Mejoras futuras (fuera del alcance del port, a charlar con el grupo)

- **Creación de usuarios por rol en el admin.** Hoy el "rol" es implícito (qué perfil
  tiene el User). Idea: que la creación distinga admin / médico / paciente y pida los
  datos según el rol:
  - Médico → datos del médico **+ franja horaria**.
  - Paciente → datos del paciente.
  - Admin → sin datos de perfil (solo `is_staff`/superuser).
  - Paso intermedio barato: inline de `FranjaHoraria` en `MedicoAdmin` (cargar franjas
    en la misma pantalla del médico). Lo más ambicioso (un asistente único con selector
    de rol que cree User + perfil en un paso) es una feature custom aparte, al estilo
    de `RegistroPacienteForm`.
- **Filtro de `lista_medicos.html` sin JS** (ver aviso al inicio del doc): botón
  "Filtrar" o dropdown de Bootstrap con links.

## 7. Funcionalidad pendiente del rol Médico (según `usabilidad.md`)

El flujo de turnos (aceptar/rechazar) está, pero el rol médico tiene varias
capacidades de `usabilidad.md` **todavía sin implementar**:

**Requeridas (no opcionales):**
- [ ] **Médico edita sus propios datos.** Hoy `PerfilUsuarioView` es solo para
      pacientes; no hay edición de perfil para el médico.
- [ ] **Ver listado de pacientes ya atendidos** (derivado de sus turnos `finalizado`).
- [ ] **Filtrar/ver el historial de un paciente** específico (sus turnos pasados).
- [ ] **Separar turnos futuros vs pasados** en la vista del médico (hoy `ListaTurnosView`
      los muestra todos juntos, sin distinción).

**Opcionales (marcadas como opcionales en `usabilidad.md`):**
- [ ] Médico **ve** su franja horaria disponible.
- [ ] Médico **define** su franja horaria desde el front (hoy solo vía admin/fixtures).

**Otras mejoras de gestión:**
- [ ] **Ausencias desde el front para el médico.** Hoy `NuevaAusenciaView` está detrás
      de `PermissionRequiredMixin('app.add_ausencia')` → solo staff. El médico no puede
      cargar sus ausencias por la UI. (Nota: `usabilidad.md` no lo lista explícito en el
      rol médico, pero es deseable y se conversó.)

> Resumen: la **funcionalidad central de turnos** (sacar / aceptar / rechazar /
> cancelar, con los 3 roles) está terminada y verificada. Lo de arriba son
> capacidades adicionales del rol médico y de gestión, a planificar con el grupo.

## 8. Gap analysis contra `consigna.md` (cumplimiento)

Leyenda de dificultad: 🟢 trivial (URL / ajuste chico) · 🟡 medio (1 vista CBV +
template siguiendo patrones existentes) · 🔴 difícil (modelo nuevo / rediseño / lógica).

### 8.1 Criterios de aceptación obligatorios — TODOS cumplidos
- ✅ Modelos con `validate/new/update` · ✅ Migraciones funcionales · ✅ Solo CBV ·
  ✅ Login/logout/registro · ✅ Permisos por tipo de usuario · ✅ Navbar dinámica ·
  ✅ Admin personalizado (list_display/filter) · ✅ ≥2 forms con validación propia ·
  ✅ Modelos testeados (58 tests OK) · ✅ Bootstrap 5 responsivo · ✅ README existe (135 líneas).
- ✅ Vistas protegidas con login — salvo home y lista de médicos (públicas, pactado).
- 🟢 **"Frontend sin JS para lógica compleja":** la consigna prohíbe *lógica compleja*
  en JS. El `fetch` del buscador ya se quitó; queda solo `onchange="this.form.submit()"`
  en `lista_medicos.html`, que NO es lógica compleja → **cumple la consigna**. (La regla
  más estricta de "cero JS" es del grupo, no de la consigna; ver aviso al inicio.)
- ⚙️ **Mínimo 10 commits por integrante:** proceso/Git, no código. Verificar en GitHub.

### 8.2 Las 13 características obligatorias del TP — TODAS implementadas ✅
1. Login/logout/registro/permisos · 2. Navbar dinámica · 3. Admin · 4. Home con
estadísticas · 5. Tabla de médicos con filtro por especialidad · 6. Detalle de médico
(info + obras sociales + ausencias) · 7. Formulario de creación de turno · 8. Listado de
turnos del médico · 9. Perfil de usuario · 10. Formulario de ausencias · 11. Listado de
pacientes · 12. Cancelación de turnos · 13. Aceptación de turnos por el médico.

> **Conclusión:** para la lista obligatoria del TP, **no falta nada**. Lo que sigue son
> opcionales y refinamientos.

### 8.3 Tareas opcionales del TP
- **Opcional 1 — Recordatorios** (modelo + manejo + visualización): ❌ no hecho → 🔴.
- **Opcional 2 — Franjas horarias** (modelo + complejización de turnos y detalle médico):
  🟡 casi completo. Modelo `FranjaHoraria` ✅ y turnos leen de él ✅. **Falta** mostrar las
  franjas en el **detalle del médico** (`detalle_medico.html` muestra obras sociales y
  ausencias, no franjas) → 🟢 agregar al template (+ pasar `franjas` en `DetalleMedicoView`).
- **Opcional 3 — Reprogramación automática ante ausencia** con confirmación: ❌ → 🔴.
- **Opcional 4 — Historial de pacientes para el médico** (a partir de turnos): ❌ → 🟡.

> ⚠️ **CAVEAT CRÍTICO (consigna línea 169):** *"Grupos de 5 deberán tomar las tareas
> opcionales 1 y 2 como obligatorias."* Si el grupo es de 5 integrantes, **Recordatorios
> (1) pasa a obligatorio y está SIN hacer (🔴)**, y Franjas (2) debe completarse (el
> detalle del médico). **Verificar el tamaño del grupo cuanto antes** — es el mayor riesgo.

### 8.4 Refinamientos del rol médico (de `usabilidad.md`, ver sección 7)
- 🟡 Médico edita sus datos · 🟡 Ver pacientes atendidos (se solapa con opcional 4) ·
  🟡 Médico define franjas desde el front · 🟢/🟡 separar turnos futuros/pasados.
- 🟡 Ausencias desde el front para el médico (hoy solo staff).

### 8.5 Deuda técnica
- 🟢 Reemplazar `onchange` JS en `lista_medicos.html` (regla estricta del grupo).
- 🟡 Tests de vistas/permisos (ver sección Fase 4).
