from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea los usuarios de prueba del sistema.'

    def handle(self, *args, **options):
        pass
