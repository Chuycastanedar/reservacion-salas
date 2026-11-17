import datetime

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase

from reservaciones.models import Reservacion, Sala
from reservaciones.services import cancelar_reservacion, crear_reservacion
from reservaciones.tests.utilidades import AHORA, RelojFijoMixin


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

    def test_rechaza_traslape_parcial_al_final(self):
        self.datos['hora_inicio'] = datetime.time(10, 30)
        self.datos['hora_fin'] = datetime.time(11, 30)
        with self.assertRaises(ValidationError):
            crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 1)

    def test_rechaza_traslape_parcial_al_inicio(self):
        self.datos['hora_inicio'] = datetime.time(9, 30)
        self.datos['hora_fin'] = datetime.time(10, 30)
        with self.assertRaises(ValidationError):
            crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 1)

    def test_permite_horario_adyacente_posterior(self):
        self.datos['hora_inicio'] = datetime.time(11, 0)
        self.datos['hora_fin'] = datetime.time(12, 0)
        crear_reservacion(**self.datos)
        self.assertEqual(self.cuenta_vigentes(), 2)

    def test_permite_horario_adyacente_anterior(self):
        self.datos['hora_inicio'] = datetime.time(9, 0)
        self.datos['hora_fin'] = datetime.time(10, 0)
        crear_reservacion(**self.datos)
        self.assertEqual(self.cuenta_vigentes(), 2)

    def test_rechaza_traslape_que_contiene_a_la_existente(self):
        self.datos['hora_inicio'] = datetime.time(9, 30)
        self.datos['hora_fin'] = datetime.time(11, 30)
        with self.assertRaises(ValidationError):
            crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 1)

    def test_rechaza_traslape_contenido_en_la_existente(self):
        self.datos['hora_inicio'] = datetime.time(10, 15)
        self.datos['hora_fin'] = datetime.time(10, 45)
        with self.assertRaises(ValidationError):
            crear_reservacion(**self.datos)
        self.assertEqual(Reservacion.objects.count(), 1)

    def test_ignora_reservaciones_canceladas(self):
        self.existente.estado = Reservacion.Estado.CANCELADA
        self.existente.save()
        crear_reservacion(**self.datos)
        self.assertEqual(self.cuenta_vigentes(), 1)
        self.assertEqual(
            Reservacion.objects.get(usuario=self.usuario).estado,
            Reservacion.Estado.VIGENTE)

    def cuenta_vigentes(self):
        return Reservacion.objects.filter(
            estado=Reservacion.Estado.VIGENTE).count()


class TestCancelarReservacion(RelojFijoMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.sala = Sala.objects.create(
            nombre='Sala de prueba', ubicacion='Edificio A', capacidad=4)
        self.reservacion = Reservacion.objects.create(
            usuario=self.usuario,
            sala=self.sala,
            fecha=datetime.date(2030, 1, 17),
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(11, 0),
            asistentes=3,
            proposito='Estudio para el examen final',
        )

    def test_cancela_reservacion_propia_vigente(self):
        cancelar_reservacion(self.reservacion, self.usuario, ahora=AHORA)
        self.assertEqual(Reservacion.objects.count(), 1)
        self.assertEqual(
            Reservacion.objects.first().estado,
            Reservacion.Estado.CANCELADA)

    def test_cancelacion_registra_fecha_y_hora(self):
        cancelar_reservacion(self.reservacion, self.usuario, ahora=AHORA)
        self.assertEqual(
            Reservacion.objects.first().fecha_cancelacion, AHORA)

    def test_rechaza_cancelacion_de_reservacion_ajena(self):
        otro = User.objects.create_user(
            username='estudiante2', password='Prueba12345!')
        with self.assertRaises(PermissionDenied):
            cancelar_reservacion(self.reservacion, otro, ahora=AHORA)
        self.reservacion.refresh_from_db()
        self.assertEqual(
            self.reservacion.estado, Reservacion.Estado.VIGENTE)
