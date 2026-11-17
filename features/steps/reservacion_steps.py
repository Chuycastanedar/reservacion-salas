import threading
from datetime import timedelta

from behave import given, then, when
from django.contrib.auth.models import User
from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from features.paginas import (
    asignar_valor, capturar_formulario, esperar, fecha_relativa,
    llenar_texto, seleccionar_sala, texto_visible)
from reservaciones.models import Reservacion, Sala

PASSWORD = "Prueba12345!"

PROPOSITO_VALIDO = "Estudio para el examen final"


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


@given('existe una reservación vigente de "{username}" para "{nombre}" '
       'mañana de {inicio} a {fin}')
def paso_reservacion_vigente(context, username, nombre, inicio, fin):
    usuario = User.objects.create_user(username=username, password=PASSWORD)
    Reservacion.objects.create(
        usuario=usuario,
        sala=Sala.objects.get(nombre=nombre),
        fecha=manana(),
        hora_inicio=inicio,
        hora_fin=fin,
        asistentes=2,
        proposito=PROPOSITO_VALIDO,
        estado=Reservacion.Estado.VIGENTE,
    )


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
    context.capturado["sala"] = sala
    capturar_formulario(context.browser, context.capturado)
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


@given('ambos tienen capturada la misma reservación para "{sala}" '
       'mañana de {inicio} a {fin}')
def paso_ambos_capturan(context, sala, inicio, fin):
    datos = {
        "sala": sala,
        "fecha": manana().isoformat(),
        "hora_inicio": inicio,
        "hora_fin": fin,
        "asistentes": "3",
        "proposito": PROPOSITO_VALIDO,
    }
    context.navegadores = [context.browser, context.browser2]
    for browser in context.navegadores:
        browser.get(context.get_url("/reservaciones/nueva/"))
        capturar_formulario(browser, datos)


@when('ambos envían el formulario al mismo tiempo')
def paso_ambos_envian(context):
    salida = threading.Barrier(len(context.navegadores))
    errores = []

    def enviar(browser):
        try:
            boton = browser.find_element(By.ID, "btn-guardar")
            salida.wait()
            boton.click()
            esperar(browser, EC.staleness_of(boton))
        except Exception as error:  # se reporta tras unir los hilos
            errores.append(error)

    hilos = [threading.Thread(target=enviar, args=(browser,))
             for browser in context.navegadores]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    assert not errores, f"Falló el envío concurrente: {errores!r}"


@then('solo uno de los dos ve el mensaje "{mensaje}"')
def paso_solo_uno_ve_mensaje(context, mensaje):
    textos = [texto_visible(b) for b in context.navegadores]
    con_mensaje = [i for i, texto in enumerate(textos) if mensaje in texto]
    assert len(con_mensaje) == 1, (
        f"{len(con_mensaje)} navegadores muestran {mensaje!r}:\n"
        + "\n---\n".join(textos))
    context.otro = context.navegadores[1 - con_mensaje[0]]


@then('el otro ve el mensaje "{mensaje}"')
def paso_el_otro_ve_mensaje(context, mensaje):
    visible = texto_visible(context.otro)
    assert mensaje in visible, (
        f"No se encontró el mensaje {mensaje!r} en la página:\n{visible}")


@then('entre las dos listas hay exactamente una reservación '
      'con estado "{estado}"')
def paso_una_reservacion_entre_listas(context, estado):
    total = 0
    for browser in context.navegadores:
        browser.get(context.get_url("/reservaciones/"))
        for tabla in browser.find_elements(By.ID, "tabla-reservaciones"):
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            total += sum(estado in fila.text for fila in filas)
    assert total == 1, (
        f"Se encontraron {total} reservaciones con estado {estado!r}")


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
