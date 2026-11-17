from behave import given
from django.contrib.auth.models import User

from features.paginas import iniciar_sesion

PASSWORD = "Prueba12345!"


@given('el usuario "{username}" ha iniciado sesión')
def paso_usuario_con_sesion(context, username):
    context.usuario = User.objects.create_user(
        username=username, password=PASSWORD)
    iniciar_sesion(context, username, PASSWORD)


@given('el usuario "{username}" ha iniciado sesión en un segundo navegador')
def paso_usuario_con_sesion_en_segundo_navegador(context, username):
    context.usuario2 = User.objects.create_user(
        username=username, password=PASSWORD)
    context.browser2 = context.crear_navegador()
    context.navegadores_extra.append(context.browser2)
    iniciar_sesion(context, username, PASSWORD, browser=context.browser2)
