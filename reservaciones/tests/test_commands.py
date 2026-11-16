from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase


class TestCrearUsuariosPrueba(TestCase):

    def setUp(self):
        self.password = 'Prueba12345!'

    def test_crea_los_dos_usuarios(self):
        call_command('crear_usuarios_prueba')
        for nombre in ('estudiante1', 'estudiante2'):
            self.assertTrue(User.objects.filter(username=nombre).exists())
            self.assertTrue(
                self.client.login(username=nombre, password=self.password))
