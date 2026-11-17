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

    def test_no_registra_duracion_menor_a_30_minutos(self):
        self.datos['hora_fin'] = datetime.time(10, 29)
        with self.assertRaises(ValidationError):
            crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_registra_duracion_de_30_minutos(self):
        self.datos['hora_fin'] = datetime.time(10, 30)
        crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 1)

    def test_no_registra_duracion_mayor_a_2_horas(self):
        self.datos['hora_fin'] = datetime.time(12, 1)
        with self.assertRaises(ValidationError):
            crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_registra_duracion_de_2_horas(self):
        self.datos['hora_fin'] = datetime.time(12, 0)
        crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 1)


class TestDisponibilidad(RelojFijoMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.otro_usuario = User.objects.create_user(
            username='estudiante2', password='Prueba12345!')
        self.sala = Sala.objects.create(
            nombre='Sala de prueba', ubicacion='Edificio A', capacidad=4)
        self.existente = Reservacion.objects.create(
            usuario=self.otro_usuario,
            sala=self.sala,
            fecha=datetime.date(2030, 1, 16),
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(11, 0),
            asistentes=2,
            proposito='Repaso de cálculo diferencial',
        )
        self.datos = {
            'usuario': self.usuario,
            'sala': self.sala,
            'fecha': datetime.date(2030, 1, 16),
            'hora_inicio': datetime.time(10, 0),
            'hora_fin': datetime.time(11, 0),
            'asistentes': 3,
            'proposito': 'Estudio para el examen final',
        }

    def test_rechaza_traslape_total(self):
        with self.assertRaises(ValidationError) as ctx:
            crear_reservacion(**self.datos)
        self.assertEqual(ctx.exception.messages, [
                         'La sala no está disponible en el horario '
                         'solicitado.'])
        self.assertEqual(Reservacion.objects.count(), 1)

    def test_permite_mismo_horario_en_otra_sala(self):
        self.datos['sala'] = Sala.objects.create(
            nombre='Otra sala', ubicacion='Edificio B', capacidad=4)
        crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 2)

    def test_permite_mismo_horario_en_otra_fecha(self):
        self.datos['fecha'] = datetime.date(2030, 1, 17)
        crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 2)
