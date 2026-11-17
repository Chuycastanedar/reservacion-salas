from .models import Reservacion


def crear_reservacion(
        usuario, sala, fecha, hora_inicio, hora_fin, asistentes, proposito):
    reservacion = Reservacion(
        usuario=usuario,
        sala=sala,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        asistentes=asistentes,
        proposito=proposito,
    )
    reservacion.full_clean()
    reservacion.save()
    return reservacion
