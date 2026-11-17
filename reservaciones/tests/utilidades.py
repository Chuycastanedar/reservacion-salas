"""Datos y reloj fijo compartidos por las pruebas unitarias."""
import datetime
import threading
from unittest import mock
from zoneinfo import ZoneInfo

ZONA = ZoneInfo('America/Mexico_City')

# Instante de referencia de todas las pruebas: 2030-01-16 es "mañana".
AHORA = datetime.datetime(2030, 1, 15, 9, 0, tzinfo=ZONA)


class RelojFijoMixin:
    """Parchea django.utils.timezone.now con AHORA durante cada prueba."""

    ahora = AHORA

    def setUp(self):
        parche = mock.patch(
            'django.utils.timezone.now', return_value=self.ahora)
        parche.start()
        self.addCleanup(parche.stop)
        super().setUp()


def sincronizar_comprobacion_de_traslape(partes=2, espera=2):
    """Parche que fuerza la carrera entre solicitudes concurrentes.

    Tras calcular el resultado real de ``existe_traslape``, cada solicitud
    espera en una barrera hasta que ``partes`` solicitudes hayan hecho la
    comprobación. Si la sala está bloqueada, la segunda nunca llega: la
    barrera expira y la primera continúa.
    """
    from reservaciones import services

    original = services.existe_traslape
    barrera = threading.Barrier(partes, timeout=espera)

    def envoltorio(*args, **kwargs):
        resultado = original(*args, **kwargs)
        try:
            barrera.wait()
        except threading.BrokenBarrierError:
            pass
        return resultado

    return mock.patch('reservaciones.services.existe_traslape', envoltorio)
