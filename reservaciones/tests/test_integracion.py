from django.contrib.auth.models import User
from django.test import TestCase

from reservaciones.models import Reservacion, Sala
from reservaciones.tests.utilidades import RelojFijoMixin


class TestFlujoReservarCancelar(RelojFijoMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.sala = Sala.objects.create(
            nombre='Sala de prueba', ubicacion='Edificio A', capacidad=4)
        self.data = {
            'sala': self.sala.pk,
            'fecha': '2030-01-17',
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
            'asistentes': 3,
            'proposito': 'Estudio para el examen final',
        }
        self.client.force_login(self.usuario)

    def test_reservar_cancelar_y_volver_a_reservar(self):
        self.client.post('/reservaciones/nueva/', data=self.data)
        reservacion = Reservacion.objects.get()
        self.client.post(f'/reservaciones/{reservacion.pk}/cancelar/')
        response = self.client.post('/reservaciones/nueva/', data=self.data)
        self.assertRedirects(
            response, '/reservaciones/', fetch_redirect_response=False)
        self.assertEqual(
            Reservacion.objects.filter(
                estado=Reservacion.Estado.CANCELADA).count(), 1)
        self.assertEqual(
            Reservacion.objects.filter(
                estado=Reservacion.Estado.VIGENTE).count(), 1)
