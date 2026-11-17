import re
from datetime import datetime, time, timedelta

from behave import given, then, when
from django.contrib.auth.models import User
from django.utils import timezone
from selenium.webdriver.common.by import By

from features.paginas import (
    capturar_formulario, fecha_relativa, fila_con_textos, iniciar_sesion,
    texto_visible)
from reservaciones.models import Reservacion

PASSWORD = "Prueba12345!"

PROPOSITO_VALIDO = "Estudio para el examen final"

TITULO_NO_ENCONTRADO = "Recurso no encontrado"

FORMATO_CANCELACION = re.compile(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}")


@given('es propietario de una reservación vigente para "{sala}" '
       'dentro de {dias:d} días de {inicio} a {fin}')
def paso_reservacion_propia_vigente(context, sala, dias, inicio, fin):
    context.reservacion = Reservacion.objects.create(
        usuario=context.usuario,
        sala=context.sala,
        fecha=timezone.localdate() + timedelta(days=dias),
        hora_inicio=inicio,
        hora_fin=fin,
        asistentes=2,
        proposito=PROPOSITO_VALIDO,
        estado=Reservacion.Estado.VIGENTE,
    )


@when('solicita cancelar esa reservación desde su lista')
def paso_solicita_cancelar(context):
    context.browser.get(context.get_url("/reservaciones/"))
    enlaces = context.browser.find_elements(By.CLASS_NAME, "enlace-cancelar")
    assert enlaces, (
        "La lista no ofrece la acción 'enlace-cancelar':\n"
        + texto_visible(context.browser))
    enlaces[0].click()


@when('confirma la cancelación')
def paso_confirma_cancelacion(context):
    botones = context.browser.find_elements(
        By.ID, "btn-confirmar-cancelacion")
    assert botones, (
        "No se encontró el botón 'btn-confirmar-cancelacion':\n"
        + texto_visible(context.browser))
    botones[0].click()


@then('la reservación muestra su fecha y hora de cancelación')
def paso_muestra_fecha_de_cancelacion(context):
    hoy = timezone.localdate().strftime("%d/%m/%Y")
    fila = fila_con_textos(context.browser, context.sala.nombre, "CANCELADA")
    encontradas = FORMATO_CANCELACION.findall(fila.text)
    assert any(f.startswith(hoy) for f in encontradas), (
        f"La fila no muestra una fecha de cancelación de hoy ({hoy}):\n"
        f"{fila.text}")


@then('puede registrar una nueva reservación para "{sala}" '
      'en ese mismo horario')
def paso_puede_registrar_mismo_horario(context, sala):
    reservacion = context.reservacion
    browser = context.browser
    browser.find_element(By.ID, "enlace-nueva").click()
    capturar_formulario(browser, {
        "sala": sala,
        "fecha": reservacion.fecha.isoformat(),
        "hora_inicio": reservacion.hora_inicio,
        "hora_fin": reservacion.hora_fin,
        "asistentes": "3",
        "proposito": PROPOSITO_VALIDO,
    })
    browser.find_element(By.ID, "btn-guardar").click()
    mensaje = "La reservación se registró correctamente."
    visible = texto_visible(browser)
    assert mensaje in visible, (
        f"No se pudo registrar el mismo horario:\n{visible}")
    fila_con_textos(browser, sala, "VIGENTE")


def instante_relativo(texto):
    """Convierte "ayer 09:15" en un datetime local con zona."""
    dia, hora = texto.split()
    horas, minutos = (int(parte) for parte in hora.split(":"))
    return timezone.make_aware(
        datetime.combine(fecha_relativa(dia), time(horas, minutos)))


@given('canceló {instante} una reservación suya para "{sala}"')
def paso_reservacion_cancelada(context, instante, sala):
    dia, _, hora = instante.partition(" a las ")
    # Inicio dentro de 2 días: el estado es la única regla incumplida.
    context.reservacion = Reservacion.objects.create(
        usuario=context.usuario,
        sala=context.sala,
        fecha=timezone.localdate() + timedelta(days=2),
        hora_inicio="10:00",
        hora_fin="11:00",
        asistentes=2,
        proposito=PROPOSITO_VALIDO,
        estado=Reservacion.Estado.CANCELADA,
        fecha_cancelacion=instante_relativo(f"{dia} {hora}"),
    )


@when('consulta su historial')
def paso_consulta_historial(context):
    context.browser.get(context.get_url("/reservaciones/"))


@then('observa la reservación de "{sala}" con estado "{estado}"')
def paso_observa_reservacion(context, sala, estado):
    fila_con_textos(context.browser, sala, estado)


@then('puede identificar la fecha y hora de cancelación "{instante}"')
def paso_identifica_fecha_de_cancelacion(context, instante):
    esperado = instante_relativo(instante).strftime("%d/%m/%Y %H:%M")
    fila = fila_con_textos(context.browser, context.sala.nombre, "CANCELADA")
    assert esperado in fila.text, (
        f"La fila no muestra la cancelación {esperado!r}:\n{fila.text}")


@given('existe una reservación vigente de "{username}" para "{sala}" '
       'dentro de {dias:d} días de {inicio} a {fin} '
       'con propósito "{proposito}"')
def paso_reservacion_ajena_vigente(
        context, username, sala, dias, inicio, fin, proposito):
    propietario = User.objects.create_user(
        username=username, password=PASSWORD)
    context.reservacion = Reservacion.objects.create(
        usuario=propietario,
        sala=context.sala,
        fecha=timezone.localdate() + timedelta(days=dias),
        hora_inicio=inicio,
        hora_fin=fin,
        asistentes=2,
        proposito=proposito,
        estado=Reservacion.Estado.VIGENTE,
    )


@when('intenta cancelarla abriendo la URL de cancelación '
      'de esa reservación')
def paso_abre_url_de_cancelacion(context):
    context.browser.get(context.get_url(
        f"/reservaciones/{context.reservacion.pk}/cancelar/"))


@then('ve una página de recurso no encontrado')
def paso_ve_pagina_no_encontrada(context):
    visible = texto_visible(context.browser)
    assert TITULO_NO_ENCONTRADO in visible, (
        f"Se esperaba la página {TITULO_NO_ENCONTRADO!r}:\n{visible}")


@then('la página no muestra el propósito "{proposito}"')
def paso_no_muestra_proposito(context, proposito):
    visible = texto_visible(context.browser)
    assert proposito not in visible, (
        f"La página revela el propósito {proposito!r}:\n{visible}")


@then('al iniciar sesión "{username}" su lista muestra la reservación '
      'con estado "{estado}"')
def paso_propietario_ve_estado(context, username, estado):
    context.browser.delete_all_cookies()
    iniciar_sesion(context, username, PASSWORD)
    context.browser.get(context.get_url("/reservaciones/"))
    fila_con_textos(context.browser, context.sala.nombre, estado)


@given('es propietario de una reservación vigente para "{sala}" '
       'que inicia dentro de {minutos:d} minutos')
def paso_reservacion_propia_proxima(context, sala, minutos):
    inicio = (timezone.localtime() + timedelta(minutes=minutos)).replace(
        second=0, microsecond=0)
    context.reservacion = Reservacion.objects.create(
        usuario=context.usuario,
        sala=context.sala,
        fecha=inicio.date(),
        hora_inicio=inicio.time(),
        hora_fin=(inicio + timedelta(minutes=30)).time(),
        asistentes=2,
        proposito=PROPOSITO_VALIDO,
        estado=Reservacion.Estado.VIGENTE,
    )


@when('abre la cancelación de esa reservación y la confirma')
def paso_abre_y_confirma_cancelacion(context):
    paso_abre_url_de_cancelacion(context)
    paso_confirma_cancelacion(context)
