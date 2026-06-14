# Setup rapido - TurnoYa

Este archivo resume los pasos minimos para levantar el proyecto en una maquina local.

## 1. Clonar el repositorio

```bash
git clone https://github.com/martin2716/turno-ya
cd turno-ya
```

## 2. Crear y activar el entorno virtual

### Windows

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Aplicar migraciones

```bash
python manage.py migrate
```

## 5. Crear superusuario

```bash
python manage.py createsuperuser
```

## 6. Iniciar el servidor

```bash
python manage.py runserver
```

## Problemas comunes

| Problema | Solucion rapida |
|----------|-----------------|
| `OperationalError: no such table` | Ejecutar `python manage.py migrate` |
| `No module named django` | Activar el entorno virtual |
| Error al ejecutar scripts en Windows | Ejecutar `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` |
| Error 500 o pagina en blanco | Revisar la consola donde corre `runserver` |
