# Base Inicial Grupo 6

Este repositorio ya queda preparado como **base común de trabajo** para el grupo.

## Qué ya trae esta base

- Proyecto Django funcionando.
- App principal `app` conectada.
- Modelo `Medico` con patrón `validate/new/update`.
- Tests existentes del modelo `Medico`.
- `HomeView` y `ListaMedicosView` como CBV.
- Navbar base compartida.
- Auth mínima común:
  - `accounts/login/`
  - `accounts/logout/`
  - `accounts/registro/`

## Qué NO está resuelto todavía

- Modelos `Especialidad`, `Paciente`, `Turno`, `Ausencia`, `ObraSocial`.
- Permisos por rol.
- Detalle de médico.
- Turnos y ausencias.
- Tests de los modelos faltantes.
- Admin completo.
- Estadísticas reales del home.

## Convenciones comunes del grupo

- Solo usar CBV.
- Mantener `validate/new/update` en todos los modelos de negocio.
- No trabajar directamente en `main`.
- Abrir PR por tarea o bloque chico.
- No mergear código con tests rotos.

## Ramas sugeridas

- `feature/modelo-medico-especialidad`
- `feature/modelo-paciente`
- `feature/modelo-turno`
- `feature/modelo-ausencia`
- `feature/auth-base`
- `feature/home-y-listado-medicos`

## Orden sugerido para la intermedia

1. Modelos y migraciones.
2. Tests de modelos.
3. Home con estadísticas.
4. Listado de médicos con filtro.
5. Admin básico.
6. Revisión grupal antes de entregar.
