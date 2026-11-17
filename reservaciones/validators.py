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
