# Sistema de reservación de salas de estudio

*Proyecto en desarrollo. Este README describe el alcance y la configuración previstos, que se incorporarán progresivamente.*

Aplicación web hecha con Django para consultar salas de estudio y reservarlas. Un usuario autenticado podrá registrar una reservación y cancelarla después si cumple las reglas. El proyecto se desarrollará mediante TDD y BDD, y el historial de commits deberá reflejarlo.

Actividad de la materia de *Pruebas y mantenimiento de software* (Ingeniería de Software).

## Qué hará

**HU-01. Registrar una reservación.** El usuario elegirá una sala activa, fecha, hora de inicio, hora de fin, número de asistentes y propósito. Si algo no cumple las reglas, no se guardará nada, se conservarán los datos capturados y se mostrarán mensajes específicos.

**HU-02. Cancelar una reservación.** Solo el propietario podrá cancelar una reservación vigente, y solo si faltan más de 60 minutos para su inicio. La reservación no se eliminará: quedará como `CANCELADA`, con su fecha de cancelación, y dejará de bloquear la sala.

Reglas principales:

- Solo se reservan salas activas, para hoy o una fecha futura.
- Horario institucional de 08:00 a 20:00 (el inicio no puede ser después de las 19:00).
- Duración de 30 minutos a 2 horas.
- Asistentes entre 1 y la capacidad de la sala.
- Propósito de 10 a 200 caracteres (sin contar espacios al inicio y al final).
- Dos reservaciones vigentes de la misma sala no pueden traslaparse; los horarios adyacentes (10:00-11:00 y 11:00-12:00) sí son válidos.
- Las solicitudes concurrentes no pueden generar dos reservaciones vigentes incompatibles.

Salas iniciales:

| Sala | Ubicación | Capacidad | Activa |
| --- | --- | --- | --- |
| Sala A | Biblioteca, planta baja | 4 | Sí |
| Sala B | Biblioteca, planta baja | 8 | Sí |
| Sala C | Biblioteca, planta alta | 12 | Sí |
| Sala de mantenimiento | Biblioteca, planta alta | 6 | No |

## Tecnologías

Python y Django, PostgreSQL y Docker. Para las pruebas y la calidad: Behave + Selenium (BDD), `django.test.TestCase` (unitarias), coverage.py, flake8, radon y Apache JMeter.

La actividad exige Python y Django; PostgreSQL y Docker son decisiones de arquitectura de este proyecto.

## Requisitos

- Docker y Docker Compose
- Git
- Apache JMeter (solo para las pruebas de rendimiento, se ejecuta desde tu equipo)

## Puesta en marcha

1. Clona el repositorio y entra a la carpeta:

   ```bash
   git clone <url-del-repositorio>
   cd <carpeta-del-repositorio>
   ```

2. Crea tu archivo de variables de entorno y ajusta los valores (al menos la clave secreta y la contraseña de la base de datos):

   ```bash
   cp .env.example .env
   ```

3. Construye y levanta los servicios (aplicación y PostgreSQL). Las dependencias se instalarán durante la construcción de la imagen, a partir de `requirements.txt`:

   ```bash
   docker compose up -d --build
   ```

4. Aplica las migraciones. Esto también cargará las salas iniciales mediante una migración de datos:

   ```bash
   docker compose exec web python manage.py migrate
   ```

5. Crea los usuarios de prueba:

   ```bash
   docker compose exec web python manage.py crear_usuarios_prueba
   ```

6. Abre <http://localhost:8000> e inicia sesión.

### Variables de entorno

| Variable | Para qué sirve |
| --- | --- |
| `DJANGO_SECRET_KEY` | Clave secreta de Django |
| `DJANGO_DEBUG` | Modo depuración (`True` o `False`) |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por comas |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Base de datos y credenciales de PostgreSQL |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Dónde está PostgreSQL (`db` y `5432` dentro de Docker) |

### Credenciales de prueba

Las creará el comando `crear_usuarios_prueba`. Habrá dos usuarios porque CA-08 necesita que una reservación pertenezca a otra persona.

| Usuario | Contraseña |
| --- | --- |
| `estudiante1` | `Prueba12345!` |
| `estudiante2` | `Prueba12345!` |

## Ejecutar las pruebas

Todos los comandos se ejecutarán dentro del contenedor `web`.

**Pruebas unitarias y de integración (UT-01 a UT-20, IT-01):**

```bash
docker compose exec web python manage.py test
```

**Pruebas BDD, CA-01 a CA-11 (Behave + Selenium en modo headless):**

```bash
docker compose exec web python manage.py behave
```

Los escenarios estarán en `features/`, organizados por historia de usuario: `reservaciones.feature` y `cancelaciones.feature`.

**Cobertura (objetivo: 100% en archivos con lógica del equipo):**

```bash
docker compose exec web coverage run manage.py test
docker compose exec web coverage report -m
docker compose exec web coverage html -d evidencias/cobertura
docker compose exec web rm -f evidencias/cobertura/.gitignore
```

El último comando es necesario: coverage.py crea dentro de la carpeta del reporte un `.gitignore` con `*`, lo que haría que Git ignore todo el reporte y no se versionara la evidencia E-05.

**PEP 8:**

```bash
docker compose exec web flake8 .
```
Las exclusiones (migraciones, entornos virtuales, evidencias) están centralizadas en `.flake8`.

**Complejidad ciclomática (cada función o método debe ser ≤ 10):**

```bash
docker compose exec web radon cc . -s -a -e '*/migrations/*'
```

### Exclusiones de cobertura

Se definirán en `.coveragerc` y solo se excluirán archivos sin lógica funcional:

- **Migraciones de esquema:** las genera Django automáticamente.
- **Migración de datos de las salas:** la escribe el equipo, pero solo inserta los registros iniciales y no contiene lógica de negocio.
- **`settings`, `wsgi`, `asgi` y `manage.py`:** archivos de configuración o arranque, siempre que no contengan lógica funcional.
- **`features/`:** código de automatización BDD (steps y `environment.py`) ejecutado por Behave, no por `manage.py test`. Es infraestructura de pruebas, no lógica funcional de la aplicación.

Los archivos con lógica funcional nunca se excluyen: se cubren al 100 %. Las exclusiones se limitan a los archivos sin lógica listados arriba, y cada una se justifica en esta sección.

## Pruebas de rendimiento con JMeter

Archivos en `jmeter/`:

- `reservaciones.jmx`: plan con tres grupos que se ejecutan en orden consecutivo (PERF-01, PERF-02, PERF-03). Cada hilo inicia sesión una sola vez con su propio gestor de cookies. Antes de cada POST se extrae el `csrfmiddlewaretoken`, y el id de la sala se toma por su nombre del `<select>` del formulario.
- `datos_perf02.csv`: datos de PERF-02, con cabecera `sala,dias,hora_inicio,hora_fin,asistentes` y 108 filas únicas (3 salas activas × 6 franjas de 2 h × 6 días). La columna `dias` es un desplazamiento desde hoy y el plan calcula la fecha al ejecutarse, así que el archivo no caduca. PERF-02 consume 90 filas.

PERF-03 envía 5 solicitudes simultáneas (temporizador de sincronización) para "Sala C", 10:00–11:00, en 10 fechas distintas (hoy + 10 a hoy + 19 días). Son 10 conflictos controlados en los que cada respuesta debe ser "registrada" o "no disponible".

Variables configurables con `-J`: `host`, `puerto`, `usuario`, `clave` (por defecto `localhost`, `8000`, `estudiante1`, `Prueba12345!`) y, por grupo, `perf01.hilos`, `perf01.subida`, `perf01.iteraciones` (y lo mismo con `perf02.` y `perf03.`). Sus valores por defecto son los del spec.

### Preparación de datos

1. Aplicación levantada, con `migrate` (salas iniciales) y `crear_usuarios_prueba` aplicados.
2. **Tabla de reservaciones vacía.** PERF-02 y PERF-03 usan salas, fechas y horarios concretos, así que cualquier reservación previa provocaría rechazos por traslape y mezclaría datos en la consulta de PERF-03. El comando siguiente borra **todas** las reservaciones de la base de desarrollo (salas y usuarios se conservan). Ejecútalo solo después de revisar el conteo:

   ```bash
   docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT count(*) FROM reservaciones_reservacion;"'
   docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "TRUNCATE TABLE reservaciones_reservacion RESTART IDENTITY;"'
   ```

3. No crear reservaciones a mano mientras dure la carga.

### Ejecución

```bash
rm -rf evidencias/jmeter/reporte evidencias/jmeter/resultados.jtl
jmeter -n -t jmeter/reservaciones.jmx \
  -l evidencias/jmeter/resultados.jtl \
  -e -o evidencias/jmeter/reporte
```

(La carpeta `evidencias/jmeter/reporte` debe no existir o estar vacía antes de ejecutar.) Para una prueba de humo con carga mínima basta cambiar propiedades, por ejemplo `-Jperf01.hilos=1 -Jperf02.hilos=1 -Jperf03.iteraciones=1`. La prueba de humo deja reservaciones, así que hay que vaciar la tabla otra vez antes de la ejecución completa.

El archivo `resultados.jtl` contiene los resultados crudos y no se versiona. Los entregables están en `evidencias/jmeter/`: el reporte HTML (`reporte/`), el resumen por muestra (`resumen.txt`), la interpretación (`interpretacion.md`), el conteo previo (`tabla_vacia_antes.txt`) y la consulta de PERF-03 (`perf03_consulta_bd.txt`).

| ID | Flujo | Carga | Criterio |
| --- | --- | --- | --- |
| PERF-01 | Consulta de reservaciones del usuario | 50 usuarios, 30 s de subida, 5 iteraciones | Errores < 1 %; p95 ≤ 1500 ms |
| PERF-02 | Registro de reservaciones sin conflicto | 30 usuarios, 30 s de subida, 3 iteraciones | Errores < 1 %; p95 ≤ 2000 ms |
| PERF-03 | Control de concurrencia | Al menos 10 repeticiones del mismo conflicto | Nunca dos reservaciones vigentes traslapadas |

Para la evidencia de PERF-03, esta consulta debe devolver **cero filas** después de la prueba (no debe haber pares de reservaciones vigentes traslapadas en la misma sala). Además debe haber exactamente 10 reservaciones vigentes en las fechas de PERF-03, una por conflicto:

```bash
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT a.id, b.id, a.sala_id, a.fecha, a.hora_inicio, a.hora_fin
FROM reservaciones_reservacion a
JOIN reservaciones_reservacion b
  ON a.sala_id = b.sala_id AND a.fecha = b.fecha AND a.id < b.id
WHERE a.estado = '\''VIGENTE'\'' AND b.estado = '\''VIGENTE'\''
  AND a.hora_inicio < b.hora_fin AND a.hora_fin > b.hora_inicio;"'
```

## Evidencias entregables

| Entregable | Ubicación prevista |
| --- | --- |
| E-03, E-04 Pruebas unitarias y BDD | `features/` y las pruebas de cada app; evidencia de ejecución en `evidencias/` |
| E-05 Reporte de cobertura | `evidencias/cobertura/` |
| E-06 Reporte PEP 8 | `evidencias/` |
| E-07 Reporte de complejidad | `evidencias/` |
| E-08 JMeter | `jmeter/` (`.jmx` y CSV) y `evidencias/jmeter/` (reporte HTML e interpretación) |
| E-09 Bitácora TDD | `evidencias/` |

La carpeta `evidencias/` se versionará a propósito. La evidencia de ejecución puede guardarse como `.txt` o `.log`; ambos formatos se versionan dentro de `evidencias/`. Los reportes temporales (`htmlcov/`, `.coverage`, `*.jtl`) están en `.gitignore`.

## Metodología de desarrollo

Cada incremento funcional seguirá el ciclo TDD:

1. Escribir una prueba para un comportamiento que aún no existe.
2. Ejecutarla y conservar evidencia de que falla por la razón esperada.
3. Escribir el código mínimo para que pase.
4. Ejecutar la suite completa para detectar regresiones.
5. Refactorizar código y pruebas.

Los criterios de aceptación se traducirán a escenarios BDD con Behave y Selenium. Para que el historial sea verificable:

- Los commits serán pequeños y coherentes, y la prueba se commiteará antes que el código que la satisface.
- La bitácora TDD (E-09) se irá llenando durante el desarrollo, no al final.
- La evidencia de cada ejecución (pruebas fallidas y exitosas) se guardará en `evidencias/`.
