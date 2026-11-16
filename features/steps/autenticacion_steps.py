from behave import given
from django.contrib.auth.models import User

from features.paginas import iniciar_sesion

PASSWORD = "Prueba12345!"


@given('el usuario "{username}" ha iniciado sesión')
def paso_usuario_con_sesion(context, username):
    context.usuario = User.objects.create_user(
        username=username, password=PASSWORD)
    iniciar_sesion(context, username, PASSWORD)
