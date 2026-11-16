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
