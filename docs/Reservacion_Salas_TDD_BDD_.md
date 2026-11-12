**INGENIERÍA DE SOFTWARE**

Pruebas y mantenimiento de software

*Sistema de reservación de salas de estudio*

# Descripción del examen

El estudiante desarrollará una aplicación web completamente funcional para reservar salas de estudio. La implementación deberá construirse de manera incremental mediante Desarrollo Guiado por Pruebas (TDD) y Desarrollo Guiado por Comportamiento (BDD). El producto será evaluado tanto por su comportamiento observable como por su calidad interna, mantenibilidad y desempeño.

Las historias de usuario incluidas en este documento constituyen el alcance obligatorio. No se evaluará únicamente la existencia de pantallas: cada regla de negocio, validación y criterio de aceptación deberá estar automatizado mediante pruebas reproducibles.

> **Alcance controlado:** El sistema puede incluir elementos complementarios de interfaz, pero no deben sustituir ni alterar las reglas obligatorias. La autenticación se considera una precondición técnica: el sistema debe permitir crear usuarios de prueba e iniciar sesión.

# Objetivos

- Traducir historias de usuario y criterios de aceptación en escenarios BDD automatizados.
- Aplicar el ciclo TDD: escribir una prueba que falle, implementar el código mínimo, ejecutar nuevamente y refactorizar.
- Diseñar pruebas unitarias para modelos, formularios, servicios y vistas.
- Aplicar validaciones de entrada y reglas de negocio sin duplicar lógica.
- Verificar estándares de código, cobertura, complejidad ciclomática y rendimiento bajo carga.
- Generar evidencias técnicas reproducibles mediante reportes y scripts de ejecución.

# Descripción general del sistema

El sistema permitirá que usuarios autenticados consulten la disponibilidad de salas de estudio y registren reservaciones. Una reservación tendrá propietario, sala, fecha, hora de inicio, hora de fin, número de asistentes, propósito y estado. Posteriormente, el propietario podrá cancelar una reservación vigente cuando se cumplan las reglas establecidas.

## Modelo conceptual mínimo

| **Entidad** | **Responsabilidad**                          | **Campos mínimos**                                                                                            |
|-------------|----------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Sala        | Representa un espacio reservable.            | nombre, capacidad, ubicación, activa                                                                          |
| Reservación | Registra la asignación temporal de una sala. | usuario, sala, fecha, hora_inicio, hora_fin, asistentes, propósito, estado, fecha_creación, fecha_cancelación |
| Usuario     | Usuario autenticado del sistema.             | Puede utilizar el modelo de usuario proporcionado por Django.                                                 |

> **Estados permitidos:** Una reservación solo puede encontrarse en estado VIGENTE o CANCELADA. No se deben eliminar reservaciones para simular una cancelación.

## Datos iniciales obligatorios

El estudiante deberá incluir una migración de datos, fixture o comando reproducible para disponer al menos de las siguientes salas:

| **Sala**              | **Ubicación**           | **Capacidad** | **Activa** |
|-----------------------|-------------------------|---------------|------------|
| Sala A                | Biblioteca, planta baja | 4             | Sí         |
| Sala B                | Biblioteca, planta baja | 8             | Sí         |
| Sala C                | Biblioteca, planta alta | 12            | Sí         |
| Sala de mantenimiento | Biblioteca, planta alta | 6             | No         |

# Metodología obligatoria de desarrollo

Cada incremento funcional deberá construirse aplicando el ciclo TDD. El repositorio debe mostrar commits pequeños y coherentes que permitan identificar la evolución de las pruebas y de la implementación.

**1.** Escribir una prueba automatizada para un comportamiento todavía no implementado.

**2.** Ejecutar la prueba y conservar evidencia de que falla por la razón esperada.

**3.** Crear el código mínimo necesario para que la prueba pase.

**4.** Ejecutar el conjunto completo de pruebas para comprobar que no existan regresiones.

**5.** Refactorizar código y pruebas para mejorar claridad, cohesión y reutilización.

**6.** Repetir el ciclo hasta completar cada criterio de aceptación y requerimiento técnico.

> **Criterio de evaluación:** No es suficiente escribir las pruebas al finalizar el desarrollo. La bitácora y el historial del repositorio deberán demostrar que las funcionalidades fueron construidas de manera incremental.

# Historia de usuario HU-01: registrar una reservación

| **Elemento**  | **Especificación**                                                  |
|---------------|---------------------------------------------------------------------|
| Identificador | HU-01                                                               |
| Título        | Registrar una reservación de sala                                   |
| Como          | usuario autenticado                                                 |
| Quiero        | seleccionar una sala disponible y registrar una reservación         |
| Para          | asegurar el uso exclusivo de la sala durante un periodo determinado |
| Prioridad     | Alta                                                                |

## Flujo funcional esperado

**1.** El usuario autenticado accede al formulario de nueva reservación.

**2.** El sistema muestra las salas activas y solicita fecha, hora de inicio, hora de fin, número de asistentes y propósito.

**3.** El usuario captura los datos y envía el formulario.

**4.** El sistema valida los datos y las reglas de negocio.

**5.** Cuando la información es válida, el sistema registra la reservación con estado VIGENTE y muestra un mensaje de confirmación.

**6.** Cuando existe un error, el sistema conserva los datos capturados, no registra la reservación y muestra mensajes específicos.

## Criterios de aceptación BDD

Los siguientes escenarios deberán implementarse con Behave y Selenium. La redacción puede adaptarse a la estructura del proyecto, pero no se debe reducir el comportamiento evaluado.

**CA-01. Registrar una reservación válida**

```gherkin
Dado que existe una sala activa con capacidad suficiente
Y el usuario ha iniciado sesión
Y no existe otra reservación vigente que se traslape con el horario solicitado
Cuando captura una fecha válida, una hora de inicio y una hora de fin válidas
Y captura un número de asistentes permitido y un propósito válido
Y envía el formulario
Entonces el sistema registra la reservación con estado "VIGENTE"
Y muestra un mensaje de confirmación
Y la reservación aparece en la lista de reservaciones del usuario.
```

**CA-02. Rechazar una reservación con horario traslapado**

```gherkin
Dado que existe una reservación vigente para una sala entre las 10:00 y las 11:00
Y el usuario ha iniciado sesión
Cuando intenta registrar otra reservación para la misma sala entre las 10:30 y las 11:30
Entonces el sistema no registra la nueva reservación
Y muestra un mensaje indicando que la sala no está disponible en el horario solicitado.
```

**CA-03. Rechazar una reservación que exceda la capacidad**

```gherkin
Dado que una sala activa tiene capacidad para 4 personas
Y el usuario ha iniciado sesión
Cuando intenta registrar una reservación para 5 asistentes
Entonces el sistema no registra la reservación
Y muestra un mensaje indicando que el número de asistentes supera la capacidad de la sala.
```

**CA-04. Rechazar una fecha u horario inválidos**

```gherkin
Dado que el usuario ha iniciado sesión
Cuando intenta reservar una sala con una fecha anterior al día actual
O la hora de fin no es posterior a la hora de inicio
Entonces el sistema no registra la reservación
Y muestra el mensaje de validación correspondiente.
```

**CA-05. Rechazar una sala inactiva**

```gherkin
Dado que existe una sala marcada como inactiva
Y el usuario ha iniciado sesión
Cuando intenta registrar una reservación para esa sala
Entonces el sistema no registra la reservación
Y muestra un mensaje indicando que la sala no se encuentra disponible para reservación.
```

**CA-06. Evitar una doble reservación ante solicitudes concurrentes**

```gherkin
Dado que una sala está disponible para un horario específico
Cuando dos solicitudes intentan registrar simultáneamente una reservación para la misma sala y el mismo horario
Entonces solo una reservación queda registrada como vigente
Y la segunda solicitud recibe una respuesta controlada indicando que la sala ya no está disponible.
```

## Validaciones requeridas

| **Campo o condición** | **Validación**                                                                                            | **Nivel esperado**                        |
|-----------------------|-----------------------------------------------------------------------------------------------------------|-------------------------------------------|
| Sala                  | Obligatoria. Debe existir y encontrarse activa.                                                           | Formulario y regla de negocio.            |
| Fecha                 | Obligatoria. No puede ser anterior a la fecha actual.                                                     | Formulario.                               |
| Hora de inicio        | Obligatoria. Debe encontrarse entre 08:00 y 19:00.                                                        | Formulario.                               |
| Hora de fin           | Obligatoria. Debe ser posterior a la hora de inicio y no exceder las 20:00.                               | Formulario.                               |
| Duración              | La reservación debe durar como mínimo 30 minutos y como máximo 2 horas.                                   | Regla de negocio.                         |
| Asistentes            | Obligatorio. Número entero mayor o igual a 1 y menor o igual a la capacidad de la sala.                   | Formulario y regla de negocio.            |
| Propósito             | Obligatorio. Texto entre 10 y 200 caracteres después de eliminar espacios iniciales y finales.            | Formulario.                               |
| Disponibilidad        | No puede existir una reservación VIGENTE para la misma sala cuyo intervalo se traslape con el solicitado. | Regla de negocio y control transaccional. |

## Reglas de negocio

- RN-01. Solo las salas activas pueden reservarse.
- RN-02. La capacidad solicitada nunca puede superar la capacidad configurada para la sala.
- RN-03. Las reservaciones solo pueden registrarse para el día actual o una fecha futura.
- RN-04. El horario institucional para reservaciones inicia a las 08:00 y finaliza a las 20:00.
- RN-05. La duración mínima es de 30 minutos y la duración máxima es de 2 horas.
- RN-06. Dos reservaciones VIGENTES de la misma sala no pueden traslaparse. Se considera traslape cuando inicio_nuevo < fin_existente y fin_nuevo > inicio_existente.
- RN-07. Una reservación CANCELADA no bloquea la disponibilidad de la sala.
- RN-08. El registro debe protegerse ante condiciones de carrera: dos solicitudes concurrentes no pueden producir dos reservaciones vigentes incompatibles.

## Pruebas mínimas asociadas a HU-01

| **ID** | **Nivel**             | **Caso mínimo**                                              | **Resultado esperado**                    |
|--------|-----------------------|--------------------------------------------------------------|-------------------------------------------|
| UT-01  | Modelo o servicio     | Crear reservación válida.                                    | Se registra con estado VIGENTE.           |
| UT-02  | Formulario            | Rechazar propósito menor a 10 caracteres.                    | Formulario inválido y mensaje específico. |
| UT-03  | Formulario            | Rechazar asistentes con cero, negativo o texto.              | Formulario inválido.                      |
| UT-04  | Formulario o servicio | Rechazar asistentes superiores a capacidad.                  | No se registra reservación.               |
| UT-05  | Formulario            | Rechazar fecha pasada.                                       | Formulario inválido.                      |
| UT-06  | Formulario            | Rechazar hora de fin menor o igual a hora de inicio.         | Formulario inválido.                      |
| UT-07  | Servicio              | Rechazar duración menor a 30 minutos o mayor a 2 horas.      | No se registra reservación.               |
| UT-08  | Servicio              | Detectar traslape parcial, contenido y total.                | No se registra la segunda reservación.    |
| UT-09  | Servicio              | Permitir horarios adyacentes: 10:00-11:00 y 11:00-12:00.     | Ambas reservaciones quedan vigentes.      |
| UT-10  | Servicio              | Ignorar reservaciones canceladas al calcular disponibilidad. | Permite registrar una nueva reservación.  |
| UT-11  | Vista                 | Impedir acceso anónimo al formulario.                        | Redirección a inicio de sesión.           |
| UT-12  | Vista                 | Crear reservación mediante POST válido.                      | Redirección y mensaje de éxito.           |
| IT-01  | Integración           | Enviar dos solicitudes concurrentes incompatibles.           | Solo una reservación vigente persiste.    |

# Historia de usuario HU-02: cancelar una reservación

| **Elemento**  | **Especificación**                                           |
|---------------|--------------------------------------------------------------|
| Identificador | HU-02                                                        |
| Título        | Cancelar una reservación vigente                             |
| Como          | usuario autenticado propietario de una reservación           |
| Quiero        | cancelar una reservación que ya no utilizaré                 |
| Para          | liberar la sala y permitir que otro usuario pueda reservarla |
| Prioridad     | Alta                                                         |

## Flujo funcional esperado

**1.** El usuario autenticado consulta la lista de sus reservaciones.

**2.** El sistema muestra la acción de cancelar únicamente cuando la reservación cumple las reglas aplicables.

**3.** El usuario solicita la cancelación y confirma la operación.

**4.** El sistema actualiza el estado a CANCELADA, registra la fecha y hora de cancelación y muestra un mensaje de confirmación.

**5.** La reservación permanece visible en el historial del usuario, pero deja de bloquear la disponibilidad de la sala.

## Criterios de aceptación BDD

**CA-07. Cancelar una reservación vigente con anticipación suficiente**

```gherkin
Dado que el usuario ha iniciado sesión
Y es propietario de una reservación vigente cuyo inicio ocurrirá dentro de más de 60 minutos
Cuando confirma la cancelación
Entonces el sistema cambia el estado de la reservación a "CANCELADA"
Y registra la fecha y hora de cancelación
Y muestra un mensaje de confirmación
Y la sala vuelve a estar disponible para ese horario.
```

**CA-08. Impedir que un usuario cancele una reservación ajena**

```gherkin
Dado que existe una reservación vigente perteneciente a otro usuario
Y el usuario autenticado intenta cancelarla
Entonces el sistema rechaza la operación
Y mantiene la reservación en estado "VIGENTE"
Y responde sin revelar información sensible de la reservación.
```

**CA-09. Impedir cancelación fuera del periodo permitido**

```gherkin
Dado que el usuario es propietario de una reservación vigente
Y faltan 60 minutos o menos para su inicio
Cuando intenta cancelarla
Entonces el sistema rechaza la operación
Y mantiene la reservación en estado "VIGENTE"
Y muestra un mensaje indicando que el periodo de cancelación ha concluido.
```

**CA-10. Impedir cancelar nuevamente una reservación cancelada**

```gherkin
Dado que el usuario es propietario de una reservación cancelada
Cuando intenta cancelarla nuevamente
Entonces el sistema rechaza la operación
Y conserva el estado "CANCELADA"
Y muestra un mensaje indicando que la reservación ya fue cancelada.
```

**CA-11. Mantener la trazabilidad de la cancelación**

```gherkin
Dado que el usuario cancela correctamente una reservación
Cuando consulta su historial
Entonces observa la reservación con estado "CANCELADA"
Y puede identificar la fecha y hora en la que se realizó la cancelación.
```

## Validaciones requeridas

| **Condición**            | **Validación**                                                                        | **Nivel esperado**          |
|--------------------------|---------------------------------------------------------------------------------------|-----------------------------|
| Autenticación            | La operación solo puede ejecutarse por un usuario autenticado.                        | Vista.                      |
| Propiedad                | El usuario autenticado debe ser propietario de la reservación.                        | Vista y servicio.           |
| Estado                   | Solo una reservación VIGENTE puede cancelarse.                                        | Servicio.                   |
| Anticipación             | La cancelación se permite únicamente cuando faltan más de 60 minutos para el inicio.  | Servicio.                   |
| Persistencia             | La cancelación cambia el estado y registra fecha_cancelación; no elimina el registro. | Modelo o servicio.          |
| Disponibilidad posterior | Una reservación CANCELADA deja de bloquear el intervalo de la sala.                   | Servicio de disponibilidad. |

## Reglas de negocio

- RN-09. Solo el propietario puede cancelar una reservación.
- RN-10. Una reservación solo puede cancelarse cuando su estado actual sea VIGENTE.
- RN-11. La cancelación debe solicitarse con más de 60 minutos de anticipación respecto al inicio de la reservación.
- RN-12. Cancelar no significa eliminar: el registro debe conservarse como evidencia histórica.
- RN-13. Toda cancelación exitosa debe registrar fecha y hora.
- RN-14. Las reservaciones canceladas deben mostrarse en el historial, pero no deben contabilizarse como ocupación de la sala.

## Pruebas mínimas asociadas a HU-02

| **ID** | **Nivel**   | **Caso mínimo**                                                 | **Resultado esperado**                           |
|--------|-------------|-----------------------------------------------------------------|--------------------------------------------------|
| UT-13  | Servicio    | Cancelar reservación propia, vigente y con anticipación válida. | Estado CANCELADA y fecha_cancelación registrada. |
| UT-14  | Servicio    | Rechazar cancelación de reservación ajena.                      | Estado permanece VIGENTE.                        |
| UT-15  | Servicio    | Rechazar cancelación con 60 minutos exactos de anticipación.    | Estado permanece VIGENTE.                        |
| UT-16  | Servicio    | Rechazar cancelación con menos de 60 minutos.                   | Estado permanece VIGENTE.                        |
| UT-17  | Servicio    | Rechazar segunda cancelación.                                   | No modifica la fecha inicial de cancelación.     |
| UT-18  | Vista       | Impedir cancelación mediante solicitud anónima.                 | Redirección o respuesta de acceso denegado.      |
| UT-19  | Vista       | Impedir que una petición manipulada cancele registro ajeno.     | Respuesta controlada y sin modificación.         |
| UT-20  | Integración | Reservar un horario, cancelarlo y volver a reservarlo.          | La nueva reservación queda VIGENTE.              |

# Requerimientos técnicos obligatorios

| **ID** | **Área**                        | **Requerimiento**                                                                                                                                                    |
|--------|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| RT-01  | Framework                       | La aplicación debe desarrollarse con Python y Django.                                                                                                                |
| RT-02  | Persistencia                    | Las entidades deben implementarse mediante modelos de Django y migraciones versionadas.                                                                              |
| RT-03  | Separación de responsabilidades | Las reglas de negocio reutilizables deben centralizarse en servicios, métodos de dominio o validadores. No deben duplicarse en plantillas o JavaScript.              |
| RT-04  | Autenticación                   | Las funcionalidades deben exigir inicio de sesión. Deben existir usuarios de prueba reproducibles.                                                                   |
| RT-05  | BDD                             | Todos los criterios de aceptación CA-01 a CA-11 deben automatizarse con Behave y Selenium usando un navegador real o headless.                                       |
| RT-06  | TDD                             | La implementación debe construirse mediante pruebas unitarias previas al código funcional. Utilizar django.test.TestCase o herramientas compatibles.                 |
| RT-07  | Cobertura                       | El reporte de cobertura debe alcanzar 100% en modelos, vistas, formularios, servicios, validadores y demás archivos con lógica funcional desarrollada por el equipo. |
| RT-08  | Estándar de código              | Todos los archivos Python creados por el equipo deben cumplir PEP 8.                                                                                                 |
| RT-09  | Complejidad                     | Todos los métodos y funciones creados por el equipo deben tener complejidad ciclomática menor o igual a 10.                                                          |
| RT-10  | Rendimiento                     | El equipo debe crear y ejecutar pruebas de rendimiento con Apache JMeter para los flujos señalados en la sección 10.                                                 |
| RT-11  | Configuración reproducible      | El repositorio debe incluir instrucciones para instalar dependencias, migrar base de datos, cargar datos iniciales y ejecutar pruebas.                               |
| RT-12  | Seguridad básica                | Las operaciones que modifican datos deben utilizar POST, protección CSRF y controles de autorización del lado servidor.                                              |

# Casos de prueba unitarios mínimos

Los casos UT-01 a UT-20 constituyen el conjunto mínimo obligatorio. El equipo deberá agregar pruebas adicionales cuando sean necesarias para cubrir ramas, excepciones, límites y componentes creados durante el desarrollo. Se recomienda aplicar particiones de equivalencia y análisis de valores límite.

> **Cobertura no equivale a calidad:** Alcanzar 100% de líneas ejecutadas no sustituye la verificación del comportamiento. Las pruebas deben contener aserciones útiles y comprobar resultados observables, persistencia y manejo de errores.

# Automatización BDD con Behave y Selenium

Cada criterio de aceptación deberá representarse mediante al menos un escenario automatizado. Los escenarios deben ejecutar el flujo desde la interfaz web: iniciar sesión cuando corresponda, navegar, llenar formularios, enviar acciones y comprobar mensajes o cambios visibles.

- Organizar los archivos .feature por historia de usuario.
- Implementar pasos reutilizables y evitar duplicación innecesaria.
- Crear y limpiar los datos de prueba de forma determinista.
- Ejecutar Selenium en modo headless para facilitar la revisión automatizada.
- Capturar evidencia del resultado de la ejecución y documentar el comando utilizado.
- No sustituir los escenarios de interfaz por llamadas directas a vistas o a la base de datos.

## Estructura sugerida de escenarios

```text
features/
├── reservaciones.feature
├── cancelaciones.feature
├── environment.py
└── steps/
    ├── autenticacion_steps.py
    ├── reservacion_steps.py
    └── cancelacion_steps.py
```

# Pruebas de rendimiento con Apache JMeter

El alumno deberá entregar un archivo .jmx ejecutable y un reporte HTML generado por JMeter. Las pruebas se ejecutarán sobre una instancia estable de la aplicación con datos iniciales conocidos.

## Escenarios obligatorios

| **ID**  | **Flujo**                               | **Descripción**                                                                        | **Carga mínima**                                                          | **Criterio esperado**                                                            |
|---------|-----------------------------------------|----------------------------------------------------------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| PERF-01 | Consulta de reservaciones del usuario   | GET a la vista de listado después de autenticar al usuario.                            | 50 usuarios virtuales, subida gradual de 30 s, 5 iteraciones por usuario. | Tasa de errores < 1%; percentil 95 <= 1500 ms.                                 |
| PERF-02 | Registro de reservaciones sin conflicto | POST de reservación con salas, fechas u horarios parametrizados para evitar traslapes. | 30 usuarios virtuales, subida gradual de 30 s, 3 iteraciones por usuario. | Tasa de errores < 1%; percentil 95 <= 2000 ms.                                 |
| PERF-03 | Control de concurrencia                 | POST simultáneo de dos o más solicitudes para la misma sala y horario.                 | Al menos 10 repeticiones controladas del conflicto.                       | Nunca deben persistir dos reservaciones vigentes traslapadas para la misma sala. |

## Evidencias requeridas de JMeter

- Archivo de plan de pruebas .jmx.
- Archivo CSV con los datos parametrizados utilizados durante las pruebas, cuando aplique.
- Reporte HTML generado por JMeter.
- Captura o exportación del resumen de resultados: muestras, promedio, percentil 90, percentil 95, throughput y porcentaje de errores.
- Breve interpretación de resultados y descripción de cualquier cuello de botella detectado.
- Evidencia de consulta a la base de datos después de PERF-03 para demostrar que no existen reservaciones incompatibles duplicadas.

# Calidad interna del código

## Cumplimiento de PEP 8

Todos los archivos Python creados o modificados por el equipo deberán cumplir PEP 8. El equipo debe ejecutar una herramienta de revisión estática y corregir los hallazgos aplicables antes de entregar.

```bash
# Ejemplo de verificación
flake8 . --exclude=.venv,migrations
# También puede utilizarse pycodestyle con una configuración equivalente.
```

## Cobertura de código

El reporte debe demostrar un mínimo de 100% de cobertura para los archivos con funcionalidad desarrollada por el equipo. Podrán excluirse únicamente archivos generados automáticamente, migraciones y archivos de configuración sin lógica de negocio, siempre que la exclusión se justifique en el README.

```bash
coverage run manage.py test
coverage report -m
coverage html
```

## Complejidad ciclomática

Todas las funciones y métodos deben conservar una complejidad ciclomática menor o igual a 10. Cuando una función exceda este valor, deberá refactorizarse en responsabilidades más pequeñas y volver a evaluarse.

```bash
radon cc . -s -a -x '*/migrations/*'
# Revisar que cada bloque funcional creado por el equipo sea <= 10.
```

# Entregables

| **ID** | **Entregable**               | **Contenido mínimo**                                                                                                                         |
|--------|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| E-01   | Repositorio de código fuente | Proyecto completo, historial de commits y archivo .gitignore apropiado.                                                                      |
| E-02   | README.md                    | Instrucciones reproducibles de instalación, variables de entorno, migraciones, carga de datos iniciales, ejecución y credenciales de prueba. |
| E-03   | Pruebas unitarias            | Código fuente de pruebas y evidencia de ejecución satisfactoria.                                                                             |
| E-04   | Pruebas BDD                  | Archivos .feature, steps de Behave, configuración de Selenium y evidencia de ejecución de CA-01 a CA-11.                                     |
| E-05   | Reporte de cobertura         | Carpeta HTML de coverage.py y captura o archivo de resumen con 100% en archivos funcionales.                                                 |
| E-06   | Reporte de PEP 8             | Salida de flake8 o herramienta equivalente sin incumplimientos pendientes en archivos del equipo.                                            |
| E-07   | Reporte de complejidad       | Salida de radon u otra herramienta equivalente demostrando complejidad <= 10 por método o función.                                          |
| E-08   | Pruebas JMeter               | Archivo .jmx, datos parametrizados, reporte HTML e interpretación de resultados.                                                             |
| E-09   | Bitácora TDD                 | Documento breve que muestre ciclos prueba fallida -> código mínimo -> prueba exitosa -> refactorización, apoyado por commits o capturas.  |
| E-10   | Demostración funcional       | Aplicación ejecutable y preparada para demostrar ambos flujos durante la revisión.                                                           |
