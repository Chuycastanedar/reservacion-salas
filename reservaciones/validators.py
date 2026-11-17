import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone

# Límites de horario (RN-04) y de duración (RN-05).
HORA_APERTURA = datetime.time(8, 0)
HORA_CIERRE = datetime.time(20, 0)
DURACION_MINIMA = datetime.timedelta(minutes=30)
DURACION_MAXIMA = datetime.timedelta(hours=2)


def validar_capacidad(sala, asistentes):
    if asistentes > sala.capacidad:
        raise ValidationError(
            'El número de asistentes supera la capacidad de la sala.')


def validar_fecha_no_pasada(fecha):
    if fecha < timezone.localdate():
        raise ValidationError(
            'La fecha no puede ser anterior al día actual.')


def validar_orden_horas(hora_inicio, hora_fin):
    if hora_fin <= hora_inicio:
        raise ValidationError(
            'La hora de fin debe ser posterior a la hora de inicio.')


def validar_sala_activa(sala):
    if not sala.activa:
        raise ValidationError(
            'La sala no se encuentra disponible para reservación.')


def validar_proposito(proposito):
    if len(proposito.strip()) < 10:
        raise ValidationError(
            'El propósito debe tener al menos 10 caracteres.')


def validar_asistentes(asistentes):
    if asistentes < 1:
        raise ValidationError(
            'El número de asistentes debe ser mayor o igual a 1.')


def _duracion(hora_inicio, hora_fin):
    dia = datetime.date.min
    return (datetime.datetime.combine(dia, hora_fin)
            - datetime.datetime.combine(dia, hora_inicio))


def validar_duracion(hora_inicio, hora_fin):
    duracion = _duracion(hora_inicio, hora_fin)
    if datetime.timedelta(0) < duracion < DURACION_MINIMA:
        raise ValidationError(
            'La reservación debe durar al menos 30 minutos.')
    if duracion > DURACION_MAXIMA:
        raise ValidationError(
            'La reservación no puede durar más de 2 horas.')
