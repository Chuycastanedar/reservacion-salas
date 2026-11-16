from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

USUARIOS = ('estudiante1', 'estudiante2')
PASSWORD = 'Prueba12345!'


class Command(BaseCommand):
    help = 'Crea los usuarios de prueba del sistema.'

    def handle(self, *args, **options):
        for nombre in USUARIOS:
            usuario, _ = User.objects.get_or_create(username=nombre)
            usuario.set_password(PASSWORD)
            usuario.save()
