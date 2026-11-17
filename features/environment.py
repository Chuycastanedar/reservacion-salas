from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from reservaciones.tests.utilidades import (
    sincronizar_comprobacion_de_traslape)

ARGUMENTOS = (
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--window-size=1280,900",
)


def crear_navegador():
    opciones = Options()
    opciones.binary_location = "/usr/bin/chromium"
    for argumento in ARGUMENTOS:
        opciones.add_argument(argumento)
    servicio = Service("/usr/bin/chromedriver")
    navegador = webdriver.Chrome(service=servicio, options=opciones)
    navegador.implicitly_wait(5)
    return navegador


def before_all(context):
    context.crear_navegador = crear_navegador
    context.browser = crear_navegador()


def after_all(context):
    browser = getattr(context, "browser", None)
    if browser is not None:
        browser.quit()


def before_scenario(context, scenario):
    context.browser.delete_all_cookies()
    context.parches = []
    context.navegadores_extra = []
    if "concurrencia" in scenario.effective_tags:
        parche = sincronizar_comprobacion_de_traslape()
        parche.start()
        context.parches.append(parche)


def after_scenario(context, scenario):
    for parche in getattr(context, "parches", []):
        parche.stop()
    for navegador in getattr(context, "navegadores_extra", []):
        navegador.quit()
