import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from reservaciones.models import Reservacion, Sala
from reservaciones.services import crear_reservacion


class TestCrearReservacion(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.sala = Sala.objects.create(
            nombre='Sala de prueba', ubicacion='Edificio A', capacidad=4)
        self.datos = {
            'usuario': self.usuario,
            'sala': self.sala,
            'fecha': datetime.date(2030, 1, 16),
            'hora_inicio': datetime.time(10, 0),
            'hora_fin': datetime.time(11, 0),
            'asistentes': 3,
            'proposito': 'Estudio para el examen final',
        }

    def test_crea_reservacion_valida(self):
        crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 1)
        reservacion = Reservacion.objects.first()
        self.assertEqual(reservacion.usuario, self.usuario)
        self.assertEqual(reservacion.sala, self.sala)
        self.assertEqual(reservacion.estado, Reservacion.Estado.VIGENTE)
