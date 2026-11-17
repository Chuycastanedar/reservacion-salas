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
