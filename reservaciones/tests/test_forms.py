from django.test import TestCase

from reservaciones.forms import ReservacionForm
from reservaciones.models import Sala


class TestFormReservacion(TestCase):

    def setUp(self):
        self.sala = Sala.objects.create(
            nombre='Sala de prueba', ubicacion='Edificio A', capacidad=4)
        self.data = {
            'sala': self.sala.pk,
            'fecha': '2030-01-16',
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
            'asistentes': 3,
            'proposito': 'Estudio para el examen final',
        }

    def test_form_valido(self):
        form = ReservacionForm(self.data)
        self.assertTrue(form.is_valid())

    def test_form_vacio_es_invalido(self):
        form = ReservacionForm({})
        self.assertFalse(form.is_valid())
        for campo in ('sala', 'fecha', 'hora_inicio', 'hora_fin',
                      'asistentes', 'proposito'):
            self.assertIn(campo, form.errors)
