# Guía de Setup - TurnoYa

## 1. Clonar el repositorio
git clone https://github.com/martin2716/turno-ya
cd turno-ya

## 2. Crear y activar el entorno virtual
    #Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

    # macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

## 3. Instalar Dependencias 
 pip install -r requirements.txt

## 4. Aplicar migraciones
python manage.py migrate
 
## 5. Crear superusuario
python manage.py createsuperuser

## 6. Iniciar el servidor
python manage.py runserver

# Problemas comunes

| Problema | Solución rápida |
| :--- | :--- |
| `OperationalError: no such table` | Ejecutá `python manage.py migrate` |
| `No module named django` | Activá el entorno virtual (`.venv`) |
| Error ejecución scripts (Windows) | Ejecutá `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` |
| Versión de `pip` desactualizada | Dentro del entorno: `python -m pip install --upgrade pip` |
| Error 500 / Página en blanco | Revisá la consola donde corre `runserver` |

