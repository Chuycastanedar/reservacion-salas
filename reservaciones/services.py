from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Reservacion, Sala

MENSAJE_NO_DISPONIBLE = 'La sala no está disponible en el horario solicitado.'
MENSAJE_PERIODO_CONCLUIDO = 'El periodo de cancelación ha concluido.'
MENSAJE_YA_CANCELADA = 'La reservación ya fue cancelada.'
MENSAJE_NO_PROPIETARIO = 'Solo el propietario puede cancelar la reservación.'


def existe_traslape(sala, fecha, hora_inicio, hora_fin):
    """RN-06: inicio_nuevo < fin_existente y fin_nuevo > inicio_existente."""
    return Reservacion.objects.filter(
        sala=sala,
        fecha=fecha,
        estado=Reservacion.Estado.VIGENTE,
        hora_inicio__lt=hora_fin,
        hora_fin__gt=hora_inicio,
    ).exists()


def crear_reservacion(
        usuario, sala, fecha, hora_inicio, hora_fin, asistentes, proposito):
    with transaction.atomic():
        # RN-08: bloquea la fila de la sala; una solicitud concurrente para
        # la misma sala espera aquí hasta que esta transacción termine.
        sala = Sala.objects.select_for_update().get(pk=sala.pk)
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
        if existe_traslape(sala, fecha, hora_inicio, hora_fin):
            raise ValidationError(MENSAJE_NO_DISPONIBLE)
        reservacion.save()
    return reservacion


def cancelar_reservacion(reservacion, usuario, ahora=None):
    if reservacion.usuario_id != usuario.pk:
        raise PermissionDenied(MENSAJE_NO_PROPIETARIO)
    if not reservacion.esta_vigente():
        raise ValidationError(MENSAJE_YA_CANCELADA)
    ahora = ahora or timezone.now()
    if not reservacion.en_periodo_de_cancelacion(ahora):
        raise ValidationError(MENSAJE_PERIODO_CONCLUIDO)
    reservacion.estado = Reservacion.Estado.CANCELADA
    reservacion.fecha_cancelacion = ahora
    reservacion.save()
    return reservacion
