from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from .models import Reservacion

MENSAJE_NO_DISPONIBLE = 'La sala no está disponible en el horario solicitado.'


def existe_traslape(sala, fecha, hora_inicio, hora_fin):
    inicio_dentro = Q(hora_inicio__lte=hora_inicio, hora_fin__gt=hora_inicio)
    fin_dentro = Q(hora_inicio__lt=hora_fin, hora_fin__gte=hora_fin)
    # RN-06: inicio_nuevo < fin_existente y fin_nuevo > inicio_existente.
    regla_general = Q(hora_fin__gt=hora_inicio, hora_inicio__lt=hora_fin)
    return Reservacion.objects.filter(
        inicio_dentro | fin_dentro | regla_general,
        sala=sala,
        fecha=fecha,
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
