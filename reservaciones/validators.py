from django.core.exceptions import ValidationError
from django.utils import timezone


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
    if asistentes == 0:
        raise ValidationError(
            'El número de asistentes debe ser mayor o igual a 1.')
