from django.core.exceptions import ValidationError


def validar_capacidad(sala, asistentes):
    if asistentes > sala.capacidad:
        raise ValidationError(
            'El número de asistentes supera la capacidad de la sala.')
