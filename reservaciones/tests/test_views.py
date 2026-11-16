from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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

    def inicia_sesion(self):
        User.objects.create_user(
            username='estudiante1', password='Prueba12345!')
        self.client.login(username='estudiante1', password='Prueba12345!')
