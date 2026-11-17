import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from reservaciones.models import Reservacion, Sala
from reservaciones.services import crear_reservacion
from reservaciones.tests.utilidades import RelojFijoMixin


class TestCrearReservacion(RelojFijoMixin, TestCase):

    def setUp(self):
        super().setUp()
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

    def test_no_registra_si_supera_capacidad(self):
        self.datos['asistentes'] = 5
        with self.assertRaises(ValidationError):
            crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_no_registra_en_sala_inactiva(self):
        self.sala.activa = False
        self.sala.save()
        with self.assertRaises(ValidationError) as ctx:
            crear_reservacion(**self.datos)
        self.assertEqual(ctx.exception.message_dict['sala'], [
                         'La sala no se encuentra disponible para '
                         'reservación.'])
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_guarda_proposito_sin_espacios_extremos(self):
        self.datos['proposito'] = '  Estudio para el examen final  '
        crear_reservacion(**self.datos)
        self.assertEqual(
            Reservacion.objects.first().proposito,
            'Estudio para el examen final')
