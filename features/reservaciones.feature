# language: es
Característica: Registro de reservaciones de salas
  Como estudiante
  Quiero reservar una sala de estudio
  Para contar con un espacio en el horario que necesito

  Escenario: CA-01. Registrar una reservación válida
    Dado que existe una sala activa "Sala BDD" con capacidad para 4 personas
    Y el usuario "estudiante1" ha iniciado sesión
    Y no existe otra reservación vigente para "Sala BDD" mañana
    Cuando abre el formulario de nueva reservación
    Y captura la sala "Sala BDD", la fecha de mañana y el horario de 10:00 a 11:00
    Y captura 3 asistentes y el propósito "Estudio para el examen final"
    Y envía el formulario
    Entonces ve el mensaje "La reservación se registró correctamente."
    Y su lista muestra la reservación de "Sala BDD" con estado "VIGENTE"

  Escenario: CA-03. Rechazar una reservación que exceda la capacidad
    Dado que existe una sala activa "Sala BDD" con capacidad para 4 personas
    Y el usuario "estudiante1" ha iniciado sesión
    Cuando intenta registrar una reservación válida para "Sala BDD" con 5 asistentes
    Entonces ve el mensaje "El número de asistentes supera la capacidad de la sala."
    Y el formulario conserva los datos capturados
    Y su lista no muestra ninguna reservación

  Esquema del escenario: CA-04. Rechazar una fecha u horario inválidos
    Dado que existe una sala activa "Sala BDD" con capacidad para 4 personas
    Y el usuario "estudiante1" ha iniciado sesión
    Cuando intenta registrar una reservación para "Sala BDD" con fecha "<fecha>" de <inicio> a <fin>
    Entonces ve el mensaje "<mensaje>"
    Y su lista no muestra ninguna reservación

    Ejemplos:
      | fecha  | inicio | fin   | mensaje                                                |
      | ayer   | 10:00  | 11:00 | La fecha no puede ser anterior al día actual.          |
      | mañana | 11:00  | 10:00 | La hora de fin debe ser posterior a la hora de inicio. |

  Escenario: CA-05. Rechazar una sala inactiva
    Dado que existe una sala activa "Sala en revisión" con capacidad para 6 personas
    Y el usuario "estudiante1" ha iniciado sesión
    Y tiene abierto el formulario de nueva reservación
    Y la sala "Sala en revisión" fue marcada como inactiva
    Cuando intenta registrar una reservación válida para "Sala en revisión"
    Entonces ve el mensaje "La sala no se encuentra disponible para reservación."
    Y su lista no muestra ninguna reservación
