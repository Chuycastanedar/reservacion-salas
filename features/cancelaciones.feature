# language: es
Característica: Cancelación de reservaciones
  Como usuario autenticado propietario de una reservación
  Quiero cancelar una reservación que ya no utilizaré
  Para liberar la sala y permitir que otro usuario pueda reservarla

  Escenario: CA-07. Cancelar una reservación vigente con anticipación suficiente
    Dado que existe una sala activa "Sala BDD" con capacidad para 4 personas
    Y el usuario "estudiante1" ha iniciado sesión
    Y es propietario de una reservación vigente para "Sala BDD" dentro de 2 días de 10:00 a 11:00
    Cuando solicita cancelar esa reservación desde su lista
    Y confirma la cancelación
    Entonces ve el mensaje "La reservación se canceló correctamente."
    Y su lista muestra la reservación de "Sala BDD" con estado "CANCELADA"
    Y la reservación muestra su fecha y hora de cancelación
    Y puede registrar una nueva reservación para "Sala BDD" en ese mismo horario

  Escenario: CA-11. Mantener la trazabilidad de la cancelación
    Dado que existe una sala activa "Sala BDD" con capacidad para 4 personas
    Y el usuario "estudiante1" ha iniciado sesión
    Y canceló ayer a las 09:15 una reservación suya para "Sala BDD"
    Cuando consulta su historial
    Entonces observa la reservación de "Sala BDD" con estado "CANCELADA"
    Y puede identificar la fecha y hora de cancelación "ayer 09:15"
