from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from reservaciones.models import Reservacion, Sala
from reservaciones.tests.utilidades import RelojFijoMixin
import datetime


class TestModels(RelojFijoMixin, TestCase):

    def setUp(self):
        super().setUp()
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

    def test_estado_no_permitido(self):
        self.reservacion.estado = 'PENDIENTE'
        with self.assertRaises(ValidationError):
            self.reservacion.full_clean()

    def test_estado_cancelada_permitido(self):
        self.reservacion.estado = 'CANCELADA'
        self.reservacion.full_clean()
        self.reservacion.save()
        self.assertEqual(Reservacion.objects.first().estado, 'CANCELADA')

    def test_return_object_sala(self):
        self.assertEqual(str(self.sala), 'Sala de prueba')

    def test_return_object_reservacion(self):
        self.reservacion.save()
        self.assertEqual(
            str(Reservacion.objects.first()),
            'Sala de prueba · 2030-01-16 10:00-11:00 (VIGENTE)')

    def test_proposito_solo_cuenta_texto_sin_espacios(self):
        self.reservacion.proposito = '   corto    '
        with self.assertRaises(ValidationError):
            self.reservacion.full_clean()

    def test_puede_cancelarse_con_mas_de_60_minutos(self):
        self.reservacion.save()
        self.assertTrue(self.reservacion.puede_cancelarse())
