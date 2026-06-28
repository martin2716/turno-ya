# Directivas de usabilidad — TurnoYa

Este documento define qué debe poder hacer cada tipo de usuario en el sistema.
Sirve como referencia para implementar vistas, permisos y restricciones.

> **Acuerdo con el profesor:** el home con estadísticas generales y el listado de médicos son accesibles sin necesidad de estar logueado. El resto de las vistas requieren autenticación.

---

## Paciente

- Al registrarse debe completar su perfil completo (nombre, apellido, DNI, teléfono, email, obra social).
- Puede modificar su perfil en cualquier momento.
- Puede ver el listado de médicos disponibles.
- Puede ver los turnos disponibles y sacar uno para sí mismo.
- Puede ver sus turnos pasados.
- Puede cancelar un turno propio.
- *(Opcional)* Puede ver un recordatorio de su próximo turno.

---

## Médico

> El perfil de médico siempre es creado por un administrador. No existe registro propio desde la interfaz de usuario.

- Puede ver sus propios datos (nombre, matrícula, especialidad, obras sociales).
- Puede modificar sus propios datos.
- Puede ver sus turnos futuros.
- Puede ver sus turnos pasados.
- Puede ver el listado de pacientes ya atendidos.
- Puede filtrar y ver el historial de un paciente específico (reconstruido a partir de los turnos).
- Puede aceptar o rechazar turnos (solo futuros).
- *(Opcional)* Puede ver su franja horaria disponible.
- *(Opcional)* Puede definir su franja horaria disponible.

---

## Administrador

> Todos los usuarios ingresan por la misma vista de login. El administrador, al autenticarse, es redirigido automáticamente al panel de Django (`/admin`). Puede navegar libremente entre el panel de admin y las vistas de la aplicación sin necesidad de volver a loguearse.

> Nadie puede acceder a `/admin` sin estar previamente autenticado.

- Tiene acceso completo a todas las vistas disponibles para Paciente y Médico.
- Puede gestionar todos los datos del sistema desde el panel de administración de Django (crear, modificar y eliminar cualquier registro).
- Es el único rol que puede crear perfiles de Médico.

---
