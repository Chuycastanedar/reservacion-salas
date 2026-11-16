from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

ARGUMENTOS = (
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--window-size=1280,900",
)


def before_all(context):
    opciones = Options()
    opciones.binary_location = "/usr/bin/chromium"
    for argumento in ARGUMENTOS:
        opciones.add_argument(argumento)
    servicio = Service("/usr/bin/chromedriver")
    context.browser = webdriver.Chrome(service=servicio, options=opciones)
    context.browser.implicitly_wait(5)


def after_all(context):
    browser = getattr(context, "browser", None)
    if browser is not None:
        browser.quit()


def before_scenario(context, scenario):
    context.browser.delete_all_cookies()


def after_scenario(context, scenario):
    for parche in getattr(context, "parches", []):
        parche.stop()
    for navegador in getattr(context, "navegadores_extra", []):
        navegador.quit()
