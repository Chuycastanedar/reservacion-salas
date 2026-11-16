from django.test import TestCase
from django.contrib.auth.models import User
from reservaciones.models import Reservacion, Sala
import datetime


class TestModels(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.sala = Sala(
            nombre='Sala de prueba',
            ubicacion='Biblioteca, planta baja',
            capacidad=4,
        )
        self.sala.save()
        self.reservacion = Reservacion(
            usuario=self.usuario,
            sala=self.sala,
            fecha=datetime.date(2030, 1, 16),
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(11, 0),
            asistentes=2,
            proposito='Estudio para el examen final',
        )

    def test_reservacion_nueva_es_vigente(self):
        self.reservacion.save()
        guardada = Reservacion.objects.first()
        self.assertEqual(guardada.estado, 'VIGENTE')
        self.assertIsNotNone(guardada.fecha_creacion)
        self.assertIsNone(guardada.fecha_cancelacion)
