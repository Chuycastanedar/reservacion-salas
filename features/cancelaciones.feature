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

  Escenario: CA-08. Impedir que un usuario cancele una reservación ajena
    Dado que existe una sala activa "Sala BDD" con capacidad para 4 personas
    Y existe una reservación vigente de "estudiante2" para "Sala BDD" dentro de 2 días de 10:00 a 11:00 con propósito "Asesoría confidencial de tesis"
    Y el usuario "estudiante1" ha iniciado sesión
    Cuando intenta cancelarla abriendo la URL de cancelación de esa reservación
    Entonces ve una página de recurso no encontrado
    Y la página no muestra el propósito "Asesoría confidencial de tesis"
    Y al iniciar sesión "estudiante2" su lista muestra la reservación con estado "VIGENTE"

  Escenario: CA-09. Impedir cancelación fuera del periodo permitido
    Dado que existe una sala activa "Sala BDD" con capacidad para 4 personas
    Y el usuario "estudiante1" ha iniciado sesión
    Y es propietario de una reservación vigente para "Sala BDD" que inicia dentro de 30 minutos
    Cuando abre la cancelación de esa reservación y la confirma
    Entonces ve el mensaje "El periodo de cancelación ha concluido."
    Y su lista muestra la reservación de "Sala BDD" con estado "VIGENTE"
