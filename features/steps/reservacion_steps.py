from datetime import timedelta

from behave import given, then, when
from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from features.paginas import (
    asignar_valor, llenar_texto, seleccionar_sala, texto_visible)
from reservaciones.models import Reservacion, Sala

PROPOSITO_VALIDO = "Estudio para el examen final"


DIAS_RELATIVOS = {"ayer": -1, "hoy": 0, "mañana": 1}


def manana():
    return timezone.localdate() + timedelta(days=1)


def fecha_relativa(nombre):
    return timezone.localdate() + timedelta(days=DIAS_RELATIVOS[nombre])


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


@given('la sala "{nombre}" fue marcada como inactiva')
def paso_sala_inactiva(context, nombre):
    Sala.objects.filter(nombre=nombre).update(activa=False)


@given('no existe otra reservación vigente para "{nombre}" mañana')
def paso_sin_reservaciones(context, nombre):
    Reservacion.objects.filter(
        sala__nombre=nombre,
        fecha=manana(),
        estado=Reservacion.Estado.VIGENTE,
    ).delete()


@given('tiene abierto el formulario de nueva reservación')
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


def registrar_reservacion(context, sala, fecha, inicio, fin, asistentes,
                          proposito=PROPOSITO_VALIDO, abrir=True):
    context.capturado = {
        "fecha": fecha.isoformat(),
        "hora_inicio": inicio,
        "hora_fin": fin,
        "asistentes": str(asistentes),
        "proposito": proposito,
    }
    if abrir:
        paso_abre_formulario(context)
    browser = context.browser
    seleccionar_sala(browser, sala)
    context.capturado["sala"] = sala
    for campo in ("fecha", "hora_inicio", "hora_fin"):
        asignar_valor(browser, f"id_{campo}", context.capturado[campo])
    for campo in ("asistentes", "proposito"):
        llenar_texto(browser, f"id_{campo}", context.capturado[campo])
    paso_envia_formulario(context)


@when('intenta registrar una reservación válida para "{sala}" '
      'con {asistentes:d} asistentes')
def paso_intenta_registrar_con_asistentes(context, sala, asistentes):
    registrar_reservacion(
        context, sala, manana(), "10:00", "11:00", asistentes)


@when('intenta registrar una reservación válida para "{sala}"')
def paso_intenta_registrar_en_formulario_abierto(context, sala):
    registrar_reservacion(
        context, sala, manana(), "10:00", "11:00", 3, abrir=False)


@when('intenta registrar una reservación para "{sala}" '
      'con fecha "{fecha}" de {inicio} a {fin}')
def paso_intenta_registrar_con_horario(context, sala, fecha, inicio, fin):
    registrar_reservacion(
        context, sala, fecha_relativa(fecha), inicio, fin, 3)


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


@then('el formulario conserva los datos capturados')
def paso_formulario_conserva_datos(context):
    browser = context.browser
    campos = browser.find_elements(By.ID, "id_sala")
    assert campos, "La página no muestra el formulario de reservación"
    seleccionada = Select(campos[0]).first_selected_option.text
    assert seleccionada == context.capturado["sala"], (
        f"Sala seleccionada {seleccionada!r}, "
        f"se esperaba {context.capturado['sala']!r}")
    for campo, esperado in context.capturado.items():
        if campo == "sala":
            continue
        valor = browser.find_element(
            By.ID, f"id_{campo}").get_attribute("value")
        assert valor == esperado, (
            f"El campo {campo!r} tiene {valor!r}, se esperaba {esperado!r}")


@then('su lista no muestra ninguna reservación')
def paso_lista_sin_reservaciones(context):
    context.browser.get(context.get_url("/reservaciones/"))
    visible = texto_visible(context.browser)
    assert "No tienes reservaciones registradas." in visible, (
        f"La lista muestra reservaciones:\n{visible}")
