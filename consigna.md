consignas generales:

Trabajo Integrador
✅ Criterios de aceptación obligatorios
Modelos con relaciones correctas y patrón validate/new/update
Migraciones commiteadas y funcionales
Views únicamente Class Based (CBV)
Login, logout y registro funcionando
Permisos configurables según tipo de usuario
Todas las vistas protegidas con @login_required
Navbar dinámica (cambia según autenticación)
Panel admin, usando el default de Django con los modelos configurados y
personalizados
Al menos 2 formularios con validación personalizada
Todos los modelos testeados y con tests pasando
Templates Bootstrap 5 responsivos
Frontend sin uso de Javascript para lógica compleja
README con documentación del proyecto (sin consigna)
Mínimo 10 commits por integrante en GitHub

📊 Rúbrica de evaluación
Criterio Peso Insuficiente Suficiente Bueno Excelente
Modelos y
ORM

20% Faltan modelos o
sin patrón
validate/new/updat
e

1 modelo por
persona +
métodos de
negocio

Métodos de
negocio
complejos +
manager

Todos los
modelos,
consultas
avanzadas,
constraints

Autenticación 10% Sin login o vistas
desprotegidas

Login/logout
y registro
funcionando

Formularios
complejos con
seguridad para
contraseña, etc

Capas extra de
seguridad como
doble factor de
autenticación

Laboratorio de Programación y

Lenguajes

Criterio Peso Insuficiente Suficiente Bueno Excelente
Admin 15% Sin admin o sin
configurar

1 modelo por
persona
registrado

list_display +
list_filter

Personalización
avanzada

Vistas y lógica 20% < 4 vistas o vistas

FBV

1 vista CBV
por persona
+ formularios

> 1 vista CBV
por persona +
formularios

Lógica de
negocio
avanzada + uso
avanzado de
views default de
Django

Templates 15% Sin Bootstrap,
poco o nulo uso de
DTL

Bootstrap
básico,
navbar y uso
de DTL

Buenas
prácticas, árbol
de templates
con herencia

UX cuidada,
responsivo

Tests 10% < 2 tests por
modelo o tests
fallando

1 test por
función y
todos los
tests
pasando

> 2 tests por
función y todos
los tests
pasando

Edge cases y
todos los tests
pasando

Git y
README

10% < 5 commits por
persona

10 commits
por persona

Ramas + PRs Historial limpio,
mensajes
semánticos,
buenas
prácticas

🔖 Entrega Intermedia
Condiciones:
● Modelo completo: mínimo 1 clase por persona
● Métodos: mínimo 1 método de negocio por modelo
● Tests: mínimo 1 test por cada método de cada modelo
● Vistas y templates: mínimo 2 vistas además de las 2 ya construidas

Laboratorio de Programación y

Lenguajes

🔖 Entrega Final
Condiciones para aprobación:
● Un mínimo del 70% del proyecto completo (tareas obligatorias)*
● Features funcionando
● Cumple con todos los criterios de aceptación
● Cumple con nivel “Suficiente” todos los criterios de la rúbrica
*Grupos de 5 deberán tomar las tareas opcionales 1 y 2 como obligatorias

️ Cronograma
Martes 2/6 Entrega intermedia
Martes 9/6 Evaluación
Martes 30/6 Entrega final
Miércoles 1/7 Evaluación

Modalidad de entrega
A través de un repositorio de github, realizando un fork del proyecto. Guía para hacer un
fork: https://guides.github.com/activities/forking/ .
Al hacer una entrega, se envía el link del proyecto en un mail con asunto: “GRUPO X - [Tipo
de proyecto] - Entrega N° X”. Ejemplo: “GRUPO 2 - Turnos - Entrega N° 1”.


consignas especificas del tp:

🏥 TurnoYa — Sistema de Gestión de Turnos
Médicos
Tipo: Trabajo Práctico Integrador Grupal
Stack: Python 3.13+, Django 5.1+, SQLite, Django ORM, Bootstrap 5, Git/GitHub
Proyecto: https://github.com/Laboratorio-de-Programacion-Y-lenguajes/turno-ya
Entrega: Repositorio grupal en GitHub a través de un fork del repositorio principal

🎯 Objetivo
Desarrollar una aplicación web con Django que permita gestionar turnos médicos en una
clínica, integrando: modelado de datos con ORM, vistas con lógica de negocio, templates
con Bootstrap 5, formularios con validación, autenticación de usuarios y panel de
administración.

🧠 Dominio
Una clínica pequeña necesita digitalizar su sistema de turnos. Los pacientes solicitan turnos
con médicos de distintas especialidades. El sistema requiere que los usuarios estén
registrados para operar. El personal administrativo gestiona médicos y especialidades
desde el panel de admin.

*User: es el modelo de usuario de Django
**Patrón obligatorio en todos los modelos:
- validate → solo valida, nunca toca la BD, retorna list[str]
- new → llama a validate; si hay errores retorna (None, errors); si
no, crea y retorna (instancia, [])
- update → llama a validate; si hay errores retorna la lista sin guardar;
si no, llama self.save() y retorna []

️ Características obligatorias
1. Login, logout, registro y permisos
2. Navbar dinámica (visible solo con usuario logueado)
3. Panel de administración (admin.py)
4. Home con estadísticas generales
5. Tabla de medicos con filtro por especialidad para pacientes
6. Detalle de medico: info, obras sociales que atiende y ausencias
7. Formulario de creación de turno
8. Listado de turnos para el médico
9. Perfil de usuario
10. Formulario de creación de ausencias
11. Listado de pacientes
12. Cancelación de turnos
13. Aceptación de turnos por parte de los médicos

⭐ Tareas opcionales
1. Recordatorios: modelo, manejo y visualización
2. Franjas horarias: modelo FranjaHoraria, manejo y complejización de los turnos y
detalle del médico
3. Reprogramación automática de turnos ante ausencia de médico con pedido de
confirmación al usuario
4. Historial de pacientes para el médico hecho a partir de la clase turno, con
observaciones en cada caso