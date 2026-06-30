# TurnoYa

TurnoYa es una aplicacion web para la gestion de turnos medicos desarrollada con Django.
El proyecto fue realizado como trabajo integrador de la materia Laboratorio de Programacion y Lenguajes.

## Stack

- Python 3.13+
- Django 5.1+
- SQLite
- Bootstrap 5
- `django.test.TestCase`
- Git y GitHub

## Funcionalidades implementadas

- registro de pacientes que crea el usuario y su perfil en un unico paso
- login y logout con el sistema de autenticacion de Django
- perfil de usuario editable
- pantalla de inicio con estadisticas generales y vista contextual segun el tipo de usuario
- listado de medicos con filtro por especialidad
- detalle de medico con sus obras sociales y ausencias
- flujo de pedido de turno por pasos (especialidad, medico, horario y confirmacion)
- listado de turnos filtrado segun el rol del usuario
- aceptacion, rechazo y cancelacion de turnos
- alta y listado de ausencias de medicos
- listado de pacientes para el personal autorizado
- panel de administracion de Django con los modelos principales configurados
- migraciones funcionales del proyecto
- tests de modelos y de vistas/permisos

## Integrantes

- Dario Cabrera (`ddario-tdf-edu`)
- Misael Casagrande (`BigHouseBH`)
- Maximiliano Rubidarte (`maxirubidarte-boop`)
- Martin Acosta (`martin2716`)

## Estructura general

```text
turno-ya/
├── app/
│   ├── admin.py
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── ausencia.py
│   │   └── usuario.py
│   ├── fixtures/
│   ├── migrations/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ausencia.py
│   │   ├── especialidad.py
│   │   ├── franja_horaria.py
│   │   ├── medico.py
│   │   ├── obra_social.py
│   │   ├── paciente.py
│   │   └── turno.py
│   ├── templates/
│   ├── tests/
│   │   ├── test_models.py
│   │   └── test_views.py
│   ├── urls.py
│   └── views.py
├── static/
├── templates/
├── turnoya/
│   ├── settings.py
│   └── urls.py
├── manage.py
├── README.md
├── SETUP.md
└── requirements.txt
```

## Instalacion

Para levantar el proyecto en desarrollo se pueden seguir los pasos de `SETUP.md`.

Resumen rapido:

```bash
git clone https://github.com/martin2716/turno-ya.git
cd turno-ya
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Migraciones

El proyecto ya cuenta con migraciones versionadas para la app principal. Antes de empezar a trabajar conviene aplicarlas con:

```bash
python manage.py migrate
```

Si se quiere verificar que no haya cambios de modelo pendientes de migrar:

```bash
python manage.py makemigrations --check --dry-run
```

## Tests

Para correr los tests:

```bash
python manage.py test -v 2
```

Si se quiere correr solo un archivo de tests:

```bash
python manage.py test app.tests.test_models -v 2
python manage.py test app.tests.test_views -v 2
```

El proyecto incluye tests de modelos y tests de vistas/permisos, que verifican el acceso publico/privado y la visibilidad de los turnos segun el rol del usuario.

## Decisiones de diseño

Elegimos el dominio de turnos medicos porque permitia trabajar con varias relaciones entre modelos y cubrir varios de los temas pedidos en la materia, como autenticacion, vistas basadas en clases, validaciones y uso del admin.

En los modelos seguimos el patron `validate/new/update` pedido por la consigna para separar la validacion de la persistencia. De esta manera, cada modelo puede validar sus datos antes de crear o actualizar registros y los tests quedan mas claros.

Tambien se decidio usar solo class based views para mantener consistencia con la consigna y aprovechar las vistas genericas de Django para listados, templates y registro. En la parte de autenticacion se reutilizo el sistema incorporado de Django para login y logout, mientras que el registro de pacientes se resolvio con un formulario propio que crea el usuario y su perfil en un mismo paso.

El acceso se controla por tipo de usuario. El home y el listado de medicos son publicos, mientras que el resto de las vistas requieren autenticacion. Los turnos se muestran segun el rol: un paciente ve solo los suyos, un medico ve los que tiene asignados y el personal administrativo accede a la informacion global.

El rol de medico se modela vinculando el modelo `Medico` con un usuario, de modo que un medico pueda autenticarse y gestionar sus turnos. La disponibilidad de turnos se calcula a partir del modelo `FranjaHoraria`, que define los horarios de atencion de cada medico por dia.

Los formularios se organizaron en el paquete `app/forms/` y los modelos en `app/models/`, separando cada responsabilidad en su propio archivo. La capa de administracion se mantuvo apoyada en el admin por defecto de Django, agregando `list_display`, `list_filter`, `search_fields` y `date_hierarchy` donde aportaban valor.

El trabajo se repartio por areas para que cada integrante pudiera avanzar sobre una parte concreta del proyecto, aunque despues se integraron los cambios en una unica base. Eso obligo a prestar atencion a migraciones, pruebas y consistencia entre modelos, vistas y templates.

## Estado del proyecto

El proyecto tiene una base funcional para el manejo de medicos, pacientes y turnos, y fue evolucionando por etapas a partir de la entrega intermedia. Como en todo trabajo practico grupal, algunas partes se fueron ajustando e integrando progresivamente.

En esta etapa el foco esta puesto en consolidar el flujo final, cerrar migraciones y mantener alineados modelos, admin, vistas y tests.

## Problemas comunes

| Problema | Solucion |
|----------|----------|
| `OperationalError: no such table` | Correr `python manage.py migrate` |
| `No module named django` | Activar el entorno virtual |
| Error 500 o pagina en blanco | Revisar la consola donde corre `runserver` |
| Problemas con login o redireccion | Revisar `LOGIN_URL`, `LOGIN_REDIRECT_URL` y `LOGOUT_REDIRECT_URL` en `settings.py` |
