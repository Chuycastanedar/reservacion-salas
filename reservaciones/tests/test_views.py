from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from reservaciones.models import Reservacion


class TestViewsAutenticacion(TestCase):

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


class TestViewsLista(TestCase):

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

    def inicia_sesion(self):
        User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.client.login(username='estudiante1', password='Prueba12345!')


class TestViewsNuevaReservacion(TestCase):

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

    def inicia_sesion(self):
        self.usuario = User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.client.force_login(self.usuario)
