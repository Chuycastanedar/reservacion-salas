import threading

from django.contrib.auth.models import User
from django.db import connection
from django.test import Client, TransactionTestCase
from django.urls import reverse

from reservaciones.models import Reservacion, Sala
from reservaciones.tests.utilidades import (
    RelojFijoMixin, sincronizar_comprobacion_de_traslape)


class TestConcurrencia(RelojFijoMixin, TransactionTestCase):

    def setUp(self):
        super().setUp()
        self.sala = Sala.objects.create(
            nombre='Sala de prueba', ubicacion='Edificio A', capacidad=4)
        self.usuarios = [
            User.objects.create_user(
                username=username, password='Prueba12345!')
            for username in ('estudiante1', 'estudiante2')
        ]
        self.data = {
            'sala': self.sala.pk,
            'fecha': '2030-01-16',
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
            'asistentes': 3,
            'proposito': 'Estudio para el examen final',
        }
        parche = sincronizar_comprobacion_de_traslape()
        parche.start()
        self.addCleanup(parche.stop)

    def test_dos_solicitudes_concurrentes_dejan_una_vigente(self):
        respuestas = self.enviar_en_paralelo()
        self.assertEqual(
            Reservacion.objects.filter(
                estado=Reservacion.Estado.VIGENTE).count(), 1)
        self.assertEqual(
            sorted(r.status_code for r in respuestas), [200, 302])
        rechazada = next(r for r in respuestas if r.status_code == 200)
        self.assertContains(
            rechazada, 'La sala no está disponible en el horario solicitado.')

    def enviar_en_paralelo(self):
        respuestas = []
        hilos = [
            threading.Thread(target=self.enviar, args=(usuario, respuestas))
            for usuario in self.usuarios
        ]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()
        return respuestas

    def enviar(self, usuario, respuestas):
        try:
            cliente = Client()
            cliente.force_login(usuario)
            respuestas.append(
                cliente.post(reverse('nueva_reservacion'), self.data))
        finally:
            connection.close()
