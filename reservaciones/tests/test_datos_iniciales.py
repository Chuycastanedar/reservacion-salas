from django.test import TestCase
from reservaciones.models import Sala


class TestSalasIniciales(TestCase):

    def test_salas_iniciales_cargadas(self):
        salas = Sala.objects.order_by('id').values_list(
            'nombre', 'ubicacion', 'capacidad', 'activa')
        self.assertEqual(list(salas), [
            ('Sala A', 'Biblioteca, planta baja', 4, True),
            ('Sala B', 'Biblioteca, planta baja', 8, True),
            ('Sala C', 'Biblioteca, planta alta', 12, True),
            ('Sala de mantenimiento', 'Biblioteca, planta alta', 6, False),
        ])
