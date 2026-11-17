"""Datos y reloj fijo compartidos por las pruebas unitarias."""
import datetime
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
