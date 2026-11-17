# Interpretación de resultados de rendimiento (PERF-01 a PERF-03)

Ejecución del 2026-11-17 (16:29:42–16:30:50, America/Mexico_City) con `jmeter/reservaciones.jmx` y JMeter 5.6.3 en modo no gráfico, desde el host contra `http://localhost:8000`. Las cifras salen de `evidencias/jmeter/reporte/statistics.json` y se resumen en `resumen.txt`. El reporte HTML completo está en `evidencias/jmeter/reporte/index.html`.

## Entorno

- Aplicación: Django 5.2 con `manage.py runserver` (servidor de desarrollo con hilos) dentro del contenedor `web`, `DJANGO_DEBUG=True`; PostgreSQL 16 en el contenedor `db`.
- Generador de carga y servidor en el mismo equipo (8 núcleos), así que los tiempos incluyen la contención entre ambos.
- Estado inicial: tabla `reservaciones_reservacion` vacía (`tabla_vacia_antes.txt`); salas de la migración de datos y usuario `estudiante1` del comando `crear_usuarios_prueba`.
- Los tres grupos se ejecutan en orden consecutivo. Cada hilo inicia sesión una sola vez (controlador *Once Only*) con su propio gestor de cookies, y antes de cada POST se extrae el `csrfmiddlewaretoken` de la página.

## Cumplimiento

| ID | Muestra medida | Muestras | Errores | p95 | Umbral | Resultado |
| --- | --- | ---: | ---: | ---: | --- | --- |
| PERF-01 | `PERF-01 GET listado` | 250 | 0 % | 81 ms | errores < 1 %; p95 ≤ 1500 ms | **Cumple** |
| PERF-02 | `PERF-02 POST reservación` | 90 | 0 % | 147 ms | errores < 1 %; p95 ≤ 2000 ms | **Cumple** |
| PERF-03 | 10 conflictos × 5 POST simultáneos | 50 | 0 % | 229 ms | nunca dos vigentes traslapadas | **Cumple** |

- **PERF-01.** 50 usuarios, 30 s de subida y 5 iteraciones dan 250 consultas del listado, todas con código 200 y el texto "Mis reservaciones". Promedio de 72 ms y p95 de 81 ms, muy por debajo del umbral.
- **PERF-02.** 30 usuarios × 3 iteraciones consumen 90 de las 108 filas únicas de `jmeter/datos_perf02.csv`. Las fechas se calculan en tiempo de ejecución (hoy + `dias`), así que el CSV no caduca. Las 90 solicitudes recibieron "La reservación se registró correctamente." tras la redirección al listado, sin ningún rechazo por traslape. El p95 de 147 ms incluye el POST, la redirección y el GET del listado.
- **PERF-03.** En cada iteración, un temporizador de sincronización libera a la vez las 5 solicitudes de los 5 hilos para "Sala C", 10:00–11:00, en la fecha hoy + (10 + iteración) días. Son 10 conflictos controlados en fechas distintas y sin choque con PERF-02. Las 50 respuestas fueron controladas (M-01 o M-02) y ninguna devolvió error 500. En la base (`perf03_consulta_bd.txt`):
  - la consulta de pares vigentes traslapados devuelve **0 filas**;
  - hay **exactamente 1** reservación vigente por cada una de las 10 fechas (10 en total), así que las otras 40 solicitudes se rechazaron con "La sala no está disponible en el horario solicitado.";
  - el total de la tabla es 100 (90 de PERF-02 + 10 de PERF-03), sin filas ajenas a la prueba.

  Esto confirma que el bloqueo `select_for_update()` de la fila de `Sala` dentro de `transaction.atomic()` serializa las altas concurrentes en PostgreSQL.

## Cuellos de botella observados

1. **Inicio de sesión (`POST login`).** Es la operación más lenta: promedio de 1.36–1.74 s y máximo de 2.13 s. La causa es el cifrado de contraseñas: Django 5.2 usa PBKDF2-SHA256 con 1 000 000 iteraciones, que consume CPU de forma deliberada, y varios hilos lo hacen a la vez durante la subida. El riesgo R-05 ya lo preveía, y por eso el inicio de sesión se mide aparte, ocurre una sola vez por hilo y no forma parte de las muestras evaluadas. Por eso el p95 de la fila *Total* (1412 ms) está dominado por el login y no sirve para evaluar los criterios.
2. **Serialización por bloqueo en PERF-03.** El `POST reservación` concurrente tiene un p95 de 229 ms, frente a 147 ms en PERF-02 sin conflicto. La diferencia es la espera de las solicitudes que aguardan el bloqueo de la sala mientras la primera confirma su transacción. Es el costo esperado de la garantía de no duplicar y, a esta escala, no compromete los umbrales.
3. **Servidor de desarrollo.** `runserver` con `DEBUG=True` no es un servidor de producción. Aun así sobró margen en ambos umbrales, así que no fue necesario aplicar las mitigaciones de R-05 (`DJANGO_DEBUG=False` o un servidor WSGI de producción).

## Incidencias durante la preparación

- La primera ejecución completa se descartó. El plan calculaba la fecha de PERF-03 con `${__jm__PERF-03__idx}`, una variable que no existía porque el bucle principal del grupo no tiene nombre en el XML. Las 10 iteraciones usaron la misma fecha (1 vigente en vez de 10). La consulta de traslapes también dio 0 filas en esa corrida, pero no demostraba los 10 conflictos pedidos. Se sustituyó por un contador por hilo (`dias_perf03`, 10..19), se comprobó con una prueba de humo de 3 iteraciones, se vació la tabla y se regeneraron `reporte/`, `resultados.jtl` y `perf03_consulta_bd.txt`.
- Los POST que siguen la redirección descartan sus submuestras (`prev.removeSubResults()`). Así el reporte registra una sola muestra por solicitud, con el tiempo total del POST más la redirección, sin filas duplicadas `-0`/`-1`.
