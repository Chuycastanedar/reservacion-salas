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

    def test_hora_fin_vacia_omite_reglas_de_horario(self):
        self.data['hora_fin'] = ''
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['hora_fin'], [
                         'Este campo es obligatorio.'])

    def test_sala_inactiva_mensaje(self):
        inactiva = Sala.objects.create(
            nombre='Sala inactiva', ubicacion='Edificio B', capacidad=4,
            activa=False)
        self.data['sala'] = inactiva.pk
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['sala'], [
                         'La sala no se encuentra disponible para '
                         'reservación.'])

    def test_sala_inexistente_mensaje(self):
        self.data['sala'] = 9999
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['sala'], [
                         'La sala no se encuentra disponible para '
                         'reservación.'])

    def test_proposito_min_caracteres(self):
        self.data['proposito'] = 'a' * 9
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_proposito_min_caracteres_mensaje(self):
        self.data['proposito'] = 'a' * 9
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['proposito'], [
                         'El propósito debe tener al menos 10 caracteres.'])

    def test_proposito_con_10_caracteres_valido(self):
        self.data['proposito'] = 'a' * 10
        form = ReservacionForm(self.data)
        self.assertTrue(form.is_valid())

    def test_proposito_max_caracteres(self):
        self.data['proposito'] = 'a' * 201
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_proposito_max_caracteres_mensaje(self):
        self.data['proposito'] = 'a' * 201
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['proposito'], [
                         'El propósito no puede exceder los 200 '
                         'caracteres.'])

    def test_proposito_con_200_caracteres_valido(self):
        self.data['proposito'] = 'a' * 200
        form = ReservacionForm(self.data)
        self.assertTrue(form.is_valid())

    def test_asistentes_cero(self):
        self.data['asistentes'] = 0
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_asistentes_cero_mensaje(self):
        self.data['asistentes'] = 0
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['asistentes'], [
                         'El número de asistentes debe ser mayor o igual '
                         'a 1.'])

    def test_asistentes_negativo(self):
        self.data['asistentes'] = -1
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_un_asistente_valido(self):
        self.data['asistentes'] = 1
        form = ReservacionForm(self.data)
        self.assertTrue(form.is_valid())

    def test_asistentes_texto(self):
        self.data['asistentes'] = 'cinco'
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_asistentes_texto_mensaje(self):
        self.data['asistentes'] = 'cinco'
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['asistentes'], [
                         'El número de asistentes debe ser un número '
                         'entero.'])

    def test_duracion_minima_mensaje(self):
        self.data['hora_fin'] = '10:29'
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['hora_fin'], [
                         'La reservación debe durar al menos 30 minutos.'])

    def test_duracion_maxima_mensaje(self):
        self.data['hora_fin'] = '12:01'
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['hora_fin'], [
                         'La reservación no puede durar más de 2 horas.'])

    def test_hora_inicio_antes_de_apertura(self):
        self.data['hora_inicio'] = '07:59'
        self.data['hora_fin'] = '08:59'
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_hora_inicio_antes_de_apertura_mensaje(self):
        self.data['hora_inicio'] = '07:59'
        self.data['hora_fin'] = '08:59'
        form = ReservacionForm(self.data)
        self.assertEqual(form.errors['hora_inicio'], [
                         'La hora de inicio debe estar entre las 08:00 y '
                         'las 19:00.'])

    def test_hora_inicio_08_00_valida(self):
        self.data['hora_inicio'] = '08:00'
        self.data['hora_fin'] = '09:00'
        form = ReservacionForm(self.data)
        self.assertTrue(form.is_valid())

    def test_hora_inicio_despues_de_las_19(self):
        self.data['hora_inicio'] = '19:01'
        self.data['hora_fin'] = '19:45'
        form = ReservacionForm(self.data)
        self.assertFalse(form.is_valid())

    def test_hora_inicio_19_00_valida(self):
        self.data['hora_inicio'] = '19:00'
        self.data['hora_fin'] = '20:00'
        form = ReservacionForm(self.data)
        self.assertTrue(form.is_valid())
