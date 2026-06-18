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

- registro de usuarios
- login y logout con el sistema de autenticacion de Django
- pantalla de inicio con estadisticas generales
- listado de medicos
- listado de turnos
- listado de pacientes
- panel de administracion de Django para modelos del proyecto
- tests unitarios de modelos

## Integrantes

- Dario Cabrera
- Misael Casagrande
- Maximiliano Rubidarte
- Martin Acosta

## Estructura general

```text
turno-ya/
├── app/
│   ├── admin.py
│   ├── fixtures/
│   ├── migrations/
│   ├── models.py
│   ├── templates/
│   ├── tests/
│   ├── urls.py
│   └── views.py
├── static/
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
git clone https://github.com/martin2716/turno-ya
cd turno-ya
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Tests

Para correr los tests:

```bash
python manage.py test -v 2
```

Si se quiere correr solo el archivo actual de tests de modelos:

```bash
python manage.py test app.tests.test_models -v 2
```

## Decisiones de diseño

Elegimos el dominio de turnos medicos porque permitia trabajar con varias relaciones entre modelos y cubrir varios de los temas pedidos en la materia, como autenticacion, vistas basadas en clases, validaciones y uso del admin.

En los modelos seguimos el patron `validate/new/update` pedido por la consigna para separar la validacion de la persistencia. De esta manera, cada modelo puede validar sus datos antes de crear o actualizar registros y los tests quedan mas claros.

Tambien se decidio usar solo class based views para mantener consistencia con la consigna y aprovechar las vistas genericas de Django para listados, templates y registro. En la parte de autenticacion se reutilizo el sistema incorporado de Django para login y logout, mientras que el registro se resolvio con una `CreateView`.

El trabajo se repartio por areas para que cada integrante pudiera avanzar sobre una parte concreta del proyecto, aunque despues se integraron los cambios en una unica base. Eso obligo a prestar atencion a migraciones, pruebas y consistencia entre modelos, vistas y templates.

## Estado del proyecto

El proyecto tiene una base funcional para el manejo de medicos, pacientes y turnos, y fue evolucionando por etapas a partir de la entrega intermedia. Como en todo trabajo practico grupal, algunas partes se fueron ajustando e integrando progresivamente.

## Problemas comunes

| Problema | Solucion |
|----------|----------|
| `OperationalError: no such table` | Correr `python manage.py migrate` |
| `No module named django` | Activar el entorno virtual |
| Error 500 o pagina en blanco | Revisar la consola donde corre `runserver` |
| Problemas con login o redireccion | Revisar `LOGIN_URL`, `LOGIN_REDIRECT_URL` y `LOGOUT_REDIRECT_URL` en `settings.py` |
