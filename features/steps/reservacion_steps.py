from datetime import timedelta

from behave import given, then, when
from django.utils import timezone
from selenium.webdriver.common.by import By

from features.paginas import (
    asignar_valor, llenar_texto, seleccionar_sala, texto_visible)
from reservaciones.models import Reservacion, Sala


def manana():
    return timezone.localdate() + timedelta(days=1)


@given('que existe una sala activa "{nombre}" '
       'con capacidad para {capacidad:d} personas')
def paso_sala_activa(context, nombre, capacidad):
    context.sala, _ = Sala.objects.get_or_create(
        nombre=nombre,
        defaults={
            "ubicacion": "Edificio BDD",
            "capacidad": capacidad,
            "activa": True,
        },
    )


@given('no existe otra reservación vigente para "{nombre}" mañana')
def paso_sin_reservaciones(context, nombre):
    Reservacion.objects.filter(
        sala__nombre=nombre,
        fecha=manana(),
        estado=Reservacion.Estado.VIGENTE,
    ).delete()


@when('abre el formulario de nueva reservación')
def paso_abre_formulario(context):
    enlaces = context.browser.find_elements(By.ID, "enlace-nueva")
    assert enlaces, "No se encontró el enlace 'enlace-nueva' en la página"
    enlaces[0].click()


@when('captura la sala "{sala}", la fecha de mañana '
      'y el horario de {inicio} a {fin}')
def paso_captura_sala_y_horario(context, sala, inicio, fin):
    browser = context.browser
    seleccionar_sala(browser, sala)
    asignar_valor(browser, "id_fecha", manana().isoformat())
    asignar_valor(browser, "id_hora_inicio", inicio)
    asignar_valor(browser, "id_hora_fin", fin)


@when('captura {asistentes:d} asistentes y el propósito "{proposito}"')
def paso_captura_asistentes(context, asistentes, proposito):
    llenar_texto(context.browser, "id_asistentes", str(asistentes))
    llenar_texto(context.browser, "id_proposito", proposito)


@when('envía el formulario')
def paso_envia_formulario(context):
    context.browser.find_element(By.ID, "btn-guardar").click()


@then('ve el mensaje "{mensaje}"')
def paso_ve_mensaje(context, mensaje):
    visible = texto_visible(context.browser)
    assert mensaje in visible, (
        f"No se encontró el mensaje {mensaje!r} en la página:\n{visible}")


@then('su lista muestra la reservación de "{sala}" con estado "{estado}"')
def paso_lista_muestra_reservacion(context, sala, estado):
    tablas = context.browser.find_elements(By.ID, "tabla-reservaciones")
    assert tablas, "No se encontró la tabla 'tabla-reservaciones'"
    filas = tablas[0].find_elements(By.TAG_NAME, "tr")
    assert any(sala in f.text and estado in f.text for f in filas), (
        f"Ninguna fila contiene {sala!r} y {estado!r}:\n{tablas[0].text}")
