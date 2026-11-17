"""Auxiliares de página compartidos por los steps de Selenium."""
from datetime import timedelta

from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

ESPERA = 10

DIAS_RELATIVOS = {"ayer": -1, "hoy": 0, "mañana": 1}


def esperar(browser, condicion):
    return WebDriverWait(browser, ESPERA).until(condicion)


def iniciar_sesion(context, username, password, browser=None):
    browser = browser or context.browser
    browser.get(context.get_url("/cuentas/login/"))
    browser.find_element(By.ID, "id_username").send_keys(username)
    browser.find_element(By.ID, "id_password").send_keys(password)
    browser.find_element(By.ID, "btn-iniciar-sesion").click()
    esperar(browser, EC.presence_of_element_located(
        (By.ID, "btn-cerrar-sesion")))


def asignar_valor(browser, campo_id, valor):
    """Asigna el valor ISO a un campo de fecha u hora (type=date/time)."""
    campo = browser.find_element(By.ID, campo_id)
    browser.execute_script(
        "arguments[0].value = arguments[1];", campo, valor)


def llenar_texto(browser, campo_id, valor):
    campo = browser.find_element(By.ID, campo_id)
    campo.clear()
    campo.send_keys(valor)


def seleccionar_sala(browser, nombre):
    Select(browser.find_element(By.ID, "id_sala")).select_by_visible_text(
        nombre)


def texto_visible(browser):
    return browser.find_element(By.TAG_NAME, "body").text


def capturar_formulario(browser, datos):
    seleccionar_sala(browser, datos["sala"])
    for campo in ("fecha", "hora_inicio", "hora_fin"):
        asignar_valor(browser, f"id_{campo}", datos[campo])
    for campo in ("asistentes", "proposito"):
        llenar_texto(browser, f"id_{campo}", datos[campo])


def fecha_relativa(nombre):
    return timezone.localdate() + timedelta(days=DIAS_RELATIVOS[nombre])


def fila_con_textos(browser, *textos):
    """Primera fila de la tabla de reservaciones que contiene los textos."""
    tablas = browser.find_elements(By.ID, "tabla-reservaciones")
    assert tablas, "No se encontró la tabla 'tabla-reservaciones'"
    for fila in tablas[0].find_elements(By.TAG_NAME, "tr"):
        if all(texto in fila.text for texto in textos):
            return fila
    raise AssertionError(
        f"Ninguna fila contiene {textos!r}:\n{tablas[0].text}")
