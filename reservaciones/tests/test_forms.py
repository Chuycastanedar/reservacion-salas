from django.test import TestCase

from reservaciones.forms import ReservacionForm
from reservaciones.models import Sala
from reservaciones.tests.utilidades import RelojFijoMixin


class TestFormReservacion(RelojFijoMixin, TestCase):

    def setUp(self):
        super().setUp()
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

    def test_form_solo_ofrece_salas_activas(self):
        inactiva = Sala.objects.create(
            nombre='Sala inactiva', ubicacion='Edificio B', capacidad=4,
            activa=False)
        form = ReservacionForm()
        queryset = form.fields['sala'].queryset
        self.assertIn(self.sala, queryset)
        self.assertNotIn(inactiva, queryset)

    def test_asistentes_supera_capacidad(self):
        self.data['asistentes'] = 5
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_asistentes_supera_capacidad_mensaje(self):
        self.data['asistentes'] = 5
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['asistentes'], [
                         'El número de asistentes supera la capacidad '
                         'de la sala.'])

    def test_asistentes_igual_a_capacidad_valido(self):
        self.data['asistentes'] = 4
        form = ReservacionForm(self.data)
        self.assertTrue(form.is_valid())

    def test_fecha_pasada(self):
        self.data['fecha'] = '2030-01-14'
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_fecha_pasada_mensaje(self):
        self.data['fecha'] = '2030-01-14'
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['fecha'], [
                         'La fecha no puede ser anterior al día actual.'])

    def test_fecha_de_hoy_valida(self):
        self.data['fecha'] = '2030-01-15'
        form = ReservacionForm(self.data)
        self.assertTrue(form.is_valid())

    def test_hora_fin_menor_que_inicio(self):
        self.data['hora_inicio'] = '11:00'
        self.data['hora_fin'] = '10:00'
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_hora_fin_menor_que_inicio_mensaje(self):
        self.data['hora_inicio'] = '11:00'
        self.data['hora_fin'] = '10:00'
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['hora_fin'], [
                         'La hora de fin debe ser posterior a la hora '
                         'de inicio.'])

    def test_hora_fin_igual_a_inicio(self):
        self.data['hora_inicio'] = '10:00'
        self.data['hora_fin'] = '10:00'
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())
