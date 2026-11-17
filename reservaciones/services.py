from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Reservacion

MENSAJE_NO_DISPONIBLE = 'La sala no está disponible en el horario solicitado.'


def existe_traslape(sala, fecha, hora_inicio, hora_fin):
    return Reservacion.objects.filter(
        sala=sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
    ).exists()


def crear_reservacion(
        usuario, sala, fecha, hora_inicio, hora_fin, asistentes, proposito):
    reservacion = Reservacion(
        usuario=usuario,
        sala=sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        asistentes=asistentes,
        proposito=proposito.strip(),
    )
    reservacion.full_clean()
    with transaction.atomic():
        if existe_traslape(sala, fecha, hora_inicio, hora_fin):
            raise ValidationError(MENSAJE_NO_DISPONIBLE)
        reservacion.save()
    return reservacion
