from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from reservaciones.tests.utilidades import RelojFijoMixin


class TestCrearUsuariosPrueba(RelojFijoMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.password = 'Prueba12345!'

    def test_crea_los_dos_usuarios(self):
        call_command('crear_usuarios_prueba')
        for nombre in ('estudiante1', 'estudiante2'):
            self.assertTrue(User.objects.filter(username=nombre).exists())
            self.assertTrue(
                self.client.login(username=nombre, password=self.password))

    def test_restablece_password_existente(self):
        User.objects.create_user(
            username='estudiante1', password='otra-clave-9876')
        call_command('crear_usuarios_prueba')
        call_command('crear_usuarios_prueba')
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(
            User.objects.get(username='estudiante1')
            .check_password(self.password))
