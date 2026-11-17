import datetime

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from reservaciones.models import Reservacion, Sala
from reservaciones.tests.utilidades import ZONA, RelojFijoMixin


class TestViewsAutenticacion(RelojFijoMixin, TestCase):

    def test_login_response(self):
        response = self.client.get('/cuentas/login/')
        self.assertEqual(response.status_code, 200)

    def test_template_correcto_login(self):
        response = self.client.get('/cuentas/login/')
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_titulo_se_encuentra_en_el_template_login(self):
        response = self.client.get('/cuentas/login/')
        titulo = '<title>Inicio de sesión</title>'
        self.assertInHTML(titulo, response.content.decode())

    def test_nombre_url_login_response(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_redirige_despues_de_iniciar_sesion(self):
        User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        data_login = {
            'username': 'estudiante1',
            'password': 'Prueba12345!',
        }
        response = self.client.post('/cuentas/login/', data=data_login)
        self.assertEqual(response.url, '/reservaciones/')

    def test_boton_cerrar_sesion_en_template_base(self):
        User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.client.login(username='estudiante1', password='Prueba12345!')
        response = self.client.get('/reservaciones/')
        contenido = response.content.decode()
        self.assertIn('action="/cuentas/logout/"', contenido)
        self.assertIn('csrfmiddlewaretoken', contenido)
        self.assertInHTML(
            '<button type="submit" id="btn-cerrar-sesion">'
            'Cerrar sesión</button>', contenido)

    def test_logout_redireccion(self):
        User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.client.login(username='estudiante1', password='Prueba12345!')
        response = self.client.post('/cuentas/logout/')
        self.assertRedirects(
            response, '/cuentas/login/', fetch_redirect_response=False)


class TestViewsLista(RelojFijoMixin, TestCase):

    def test_redirige_si_no_inicio_sesion_lista(self):
        response = self.client.get('/reservaciones/')
        self.assertRedirects(
            response, '/cuentas/login/?next=/reservaciones/',
            fetch_redirect_response=False)

    def test_lista_response(self):
        self.inicia_sesion()
        response = self.client.get('/reservaciones/')
        self.assertEqual(response.status_code, 200)

    def test_nombre_url_lista(self):
        self.inicia_sesion()
        response = self.client.get(reverse('lista_reservaciones'))
        self.assertEqual(response.status_code, 200)

    def test_template_correcto_lista(self):
        self.inicia_sesion()
        response = self.client.get('/reservaciones/')
        self.assertTemplateUsed(
            response, 'reservaciones/lista_reservaciones.html')

    def test_titulo_se_encuentra_en_el_template_lista(self):
        self.inicia_sesion()
        response = self.client.get('/reservaciones/')
        self.assertInHTML(
            '<h1>Mis reservaciones</h1>', response.content.decode())

    def test_lista_vacia_muestra_aviso(self):
        self.inicia_sesion()
        response = self.client.get('/reservaciones/')
        self.assertContains(
            response, 'No tienes reservaciones registradas.')

    def test_raiz_redirige_a_lista(self):
        response = self.client.get('/')
        self.assertRedirects(
            response, '/reservaciones/', fetch_redirect_response=False)

    def test_envio_datos_reservaciones(self):
        usuario = self.inicia_sesion()
        self.crea_reservacion(usuario)
        response = self.client.get('/reservaciones/')
        self.assertIn('reservaciones', response.context)
        self.assertEqual(len(response.context['reservaciones']), 1)

    def test_reservacion_propia_se_encuentra_en_el_template(self):
        usuario = self.inicia_sesion()
        self.crea_reservacion(usuario)
        response = self.client.get('/reservaciones/')
        self.assertContains(response, 'Sala de prueba')
        contenido = response.content.decode()
        inicio = contenido.index('id="tabla-reservaciones"')
        tabla = contenido[inicio:contenido.index('</table>', inicio)]
        self.assertIn('Sala de prueba', tabla)
        self.assertIn('2030-01-16', tabla)
        self.assertIn('10:00 - 11:00', tabla)
        self.assertIn('VIGENTE', tabla)

    def test_no_muestra_reservaciones_ajenas(self):
        self.inicia_sesion()
        otro = User.objects.create_user(
            username='estudiante2', password='Prueba12345!')
        self.crea_reservacion(otro)
        response = self.client.get('/reservaciones/')
        self.assertNotContains(response, 'Sala de prueba')
        self.assertContains(
            response, 'No tienes reservaciones registradas.')

    def test_cancelada_muestra_fecha_de_cancelacion(self):
        usuario = self.inicia_sesion()
        self.crea_reservacion(
            usuario,
            estado=Reservacion.Estado.CANCELADA,
            fecha_cancelacion=datetime.datetime(
                2030, 1, 14, 9, 15, tzinfo=ZONA),
        )
        response = self.client.get('/reservaciones/')
        self.assertContains(response, 'CANCELADA')
        self.assertContains(response, '14/01/2030 09:15')

    def test_vigente_no_muestra_fecha_de_cancelacion(self):
        usuario = self.inicia_sesion()
        self.crea_reservacion(usuario)
        response = self.client.get('/reservaciones/')
        self.assertContains(response, 'VIGENTE')
        self.assertNotRegex(
            response.content.decode(), r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}')

    def test_boton_cancelar_reservacion_en_template(self):
        usuario = self.inicia_sesion()
        reservacion = self.crea_reservacion(usuario)
        response = self.client.get('/reservaciones/')
        self.assertInHTML(
            f'<a href="/reservaciones/{reservacion.pk}/cancelar/" '
            'class="enlace-cancelar">Cancelar</a>',
            response.content.decode())

    def test_no_muestra_boton_cancelar_en_cancelada(self):
        usuario = self.inicia_sesion()
        reservacion = self.crea_reservacion(
            usuario,
            estado=Reservacion.Estado.CANCELADA,
            fecha_cancelacion=datetime.datetime(
                2030, 1, 14, 9, 15, tzinfo=ZONA),
        )
        response = self.client.get('/reservaciones/')
        self.assertNotContains(
            response, f'/reservaciones/{reservacion.pk}/cancelar/')

    def test_no_muestra_boton_cancelar_si_faltan_60_minutos(self):
        usuario = self.inicia_sesion()
        sala = Sala.objects.create(
            nombre='Sala de prueba', ubicacion='Edificio A', capacidad=4)
        reservacion = Reservacion.objects.create(
            usuario=usuario,
            sala=sala,
            fecha=datetime.date(2030, 1, 15),
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(11, 0),
            asistentes=3,
            proposito='Estudio para el examen final',
        )
        response = self.client.get('/reservaciones/')
        self.assertNotContains(
            response, f'/reservaciones/{reservacion.pk}/cancelar/')

    def inicia_sesion(self):
        usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.client.login(username='estudiante1', password='Prueba12345!')
        return usuario

    def crea_reservacion(self, usuario, **campos):
        sala = Sala.objects.create(
            nombre='Sala de prueba', ubicacion='Edificio A', capacidad=4)
        return Reservacion.objects.create(
            usuario=usuario,
            sala=sala,
            fecha=datetime.date(2030, 1, 16),
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(11, 0),
            asistentes=3,
            proposito='Estudio para el examen final',
            **campos,
        )


class TestViewsNuevaReservacion(RelojFijoMixin, TestCase):

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

    def test_redirige_si_no_inicio_sesion_nueva_reservacion(self):
        response = self.client.get('/reservaciones/nueva/')
        self.assertRedirects(
            response, '/cuentas/login/?next=/reservaciones/nueva/',
            fetch_redirect_response=False)

    def test_post_anonimo_redirige_y_no_crea_reservacion(self):
        response = self.client.post('/reservaciones/nueva/', data={})
        self.assertRedirects(
            response, '/cuentas/login/?next=/reservaciones/nueva/',
            fetch_redirect_response=False)
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_nueva_reservacion_response(self):
        self.inicia_sesion()
        response = self.client.get('/reservaciones/nueva/')
        self.assertEqual(response.status_code, 200)

    def test_nombre_url_nueva_reservacion(self):
        self.inicia_sesion()
        response = self.client.get(reverse('nueva_reservacion'))
        self.assertEqual(response.status_code, 200)

    def test_template_correcto_nueva_reservacion(self):
        self.inicia_sesion()
        response = self.client.get('/reservaciones/nueva/')
        self.assertTemplateUsed(
            response, 'reservaciones/reservacion_form.html')

    def test_titulo_se_encuentra_en_el_template_nueva(self):
        self.inicia_sesion()
        response = self.client.get('/reservaciones/nueva/')
        titulo = '<title>Nueva reservación</title>'
        self.assertInHTML(titulo, response.content.decode())

    def test_formulario_en_el_template(self):
        self.inicia_sesion()
        response = self.client.get('/reservaciones/nueva/')
        self.assertIn('form', response.context)
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'novalidate')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'name="proposito"')
        self.assertContains(response, 'id="btn-guardar"')

    def test_agrega_reservacion_form(self):
        self.inicia_sesion()
        self.client.post('/reservaciones/nueva/', data=self.data)
        self.assertEqual(Reservacion.objects.count(), 1)
        reservacion = Reservacion.objects.first()
        self.assertEqual(reservacion.usuario, self.usuario)
        self.assertEqual(reservacion.estado, Reservacion.Estado.VIGENTE)

    def test_redirige_despues_de_agregar_reservacion(self):
        self.inicia_sesion()
        response = self.client.post('/reservaciones/nueva/', data=self.data)
        self.assertRedirects(
            response, '/reservaciones/', fetch_redirect_response=False)

    def test_mensaje_de_exito_al_agregar_reservacion(self):
        self.inicia_sesion()
        response = self.client.post(
            '/reservaciones/nueva/', data=self.data, follow=True)
        self.assertContains(
            response, 'La reservación se registró correctamente.')

    def test_no_agrega_reservacion_traslapada(self):
        self.inicia_sesion()
        self.crea_reservacion_existente()
        self.client.raise_request_exception = False
        self.data['hora_inicio'] = '10:30'
        self.data['hora_fin'] = '11:30'
        response = self.client.post('/reservaciones/nueva/', data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'La sala no está disponible en el horario solicitado.')
        self.assertEqual(Reservacion.objects.count(), 1)
        self.assertEqual(
            response.context['form'].data['proposito'],
            'Estudio para el examen final')

    def inicia_sesion(self):
        self.usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.client.force_login(self.usuario)

    def crea_reservacion_existente(self):
        otro_usuario = User.objects.create_user(
            username='estudiante2', password='Prueba12345!')
        Reservacion.objects.create(
            usuario=otro_usuario,
            sala=self.sala,
            fecha=datetime.date(2030, 1, 16),
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(11, 0),
            asistentes=2,
            proposito='Repaso de cálculo diferencial',
        )


class TestViewsCancelar(RelojFijoMixin, TestCase):

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
        self.url = f'/reservaciones/{self.reservacion.pk}/cancelar/'

    def test_redirige_si_no_inicio_sesion_cancelar(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response, f'/cuentas/login/?next={self.url}',
            fetch_redirect_response=False)
        self.assertEqual(
            Reservacion.objects.first().estado, Reservacion.Estado.VIGENTE)

    def test_confirmar_cancelacion_response(self):
        self.inicia_sesion()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template_correcto_confirmar_cancelacion(self):
        self.inicia_sesion()
        response = self.client.get(self.url)
        self.assertTemplateUsed(
            response, 'reservaciones/confirmar_cancelacion.html')

    def test_get_no_cancela_la_reservacion(self):
        self.inicia_sesion()
        self.client.get(self.url)
        reservacion = Reservacion.objects.first()
        self.assertEqual(reservacion.estado, Reservacion.Estado.VIGENTE)
        self.assertIsNone(reservacion.fecha_cancelacion)

    def test_formulario_de_confirmacion_en_el_template(self):
        self.inicia_sesion()
        response = self.client.get(self.url)
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'id="btn-confirmar-cancelacion"')

    def test_mensaje_de_exito_al_cancelar(self):
        self.inicia_sesion()
        response = self.client.post(self.url, follow=True)
        self.assertContains(
            response, 'La reservación se canceló correctamente.')

    def test_post_manipulado_no_cancela_reservacion_ajena(self):
        ajena = self.crea_reservacion_ajena()
        self.inicia_sesion()
        response = self.client.post(
            f'/reservaciones/{ajena.pk}/cancelar/')
        self.assertEqual(response.status_code, 404)
        ajena.refresh_from_db()
        self.assertEqual(ajena.estado, Reservacion.Estado.VIGENTE)
        self.assertIsNone(ajena.fecha_cancelacion)

    def test_get_de_reservacion_ajena_responde_404(self):
        ajena = self.crea_reservacion_ajena()
        self.inicia_sesion()
        response = self.client.get(f'/reservaciones/{ajena.pk}/cancelar/')
        self.assertNotContains(
            response, 'Asesoría confidencial de tesis', status_code=404)

    def test_cancelar_reservacion_inexistente_responde_404(self):
        self.inicia_sesion()
        response = self.client.post('/reservaciones/9999/cancelar/')
        self.assertEqual(response.status_code, 404)

    def test_cancelacion_tardia_muestra_mensaje(self):
        tardia = Reservacion.objects.create(
            usuario=self.usuario,
            sala=self.sala,
            fecha=datetime.date(2030, 1, 15),
            hora_inicio=datetime.time(9, 30),
            hora_fin=datetime.time(10, 30),
            asistentes=3,
            proposito='Estudio para el examen final',
        )
        self.inicia_sesion()
        self.client.raise_request_exception = False
        response = self.client.post(
            f'/reservaciones/{tardia.pk}/cancelar/', follow=True)
        self.assertContains(
            response, 'El periodo de cancelación ha concluido.')
        tardia.refresh_from_db()
        self.assertEqual(tardia.estado, Reservacion.Estado.VIGENTE)

    def inicia_sesion(self):
        self.client.force_login(self.usuario)

    def crea_reservacion_ajena(self):
        otro = User.objects.create_user(
            username='estudiante2', password='Prueba12345!')
        return Reservacion.objects.create(
            usuario=otro,
            sala=self.sala,
            fecha=datetime.date(2030, 1, 17),
            hora_inicio=datetime.time(12, 0),
            hora_fin=datetime.time(13, 0),
            asistentes=2,
            proposito='Asesoría confidencial de tesis',
        )


class TestViewsSeguridad(RelojFijoMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client(enforce_csrf_checks=True)
        self.usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
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

    def test_no_agrega_reservacion_sin_token_csrf(self):
        self.inicia_sesion()
        response = self.client.post('/reservaciones/nueva/', data=self.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Reservacion.objects.all().count(), 0)

    def test_no_cancela_reservacion_sin_token_csrf(self):
        reservacion = self.crea_reservacion()
        self.inicia_sesion()
        response = self.client.post(
            f'/reservaciones/{reservacion.pk}/cancelar/')
        self.assertEqual(response.status_code, 403)
        reservacion.refresh_from_db()
        self.assertEqual(reservacion.estado, Reservacion.Estado.VIGENTE)
        self.assertIsNone(reservacion.fecha_cancelacion)

    def inicia_sesion(self):
        self.client.force_login(self.usuario)

    def crea_reservacion(self):
        return Reservacion.objects.create(
            usuario=self.usuario,
            sala=self.sala,
            fecha=datetime.date(2030, 1, 17),
            hora_inicio=datetime.time(10, 0),
            hora_fin=datetime.time(11, 0),
            asistentes=3,
            proposito='Estudio para el examen final',
        )
