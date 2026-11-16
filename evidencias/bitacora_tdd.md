# Bitácora TDD

Un registro por ciclo: prueba fallida, código mínimo, prueba exitosa y refactorización.

| # | Fecha | Prueba (ID) | Comportamiento | Rojo (commit y evidencia) | Verde (commit y evidencia) | Refactorización |
|---|-------|-------------|----------------|---------------------------|----------------------------|-----------------|
| 1 | 2026-11-16 | UT-01a_modelo | Una reservación nueva queda en estado VIGENTE | `b76fe84` · `evidencias/tdd/UT-01a_modelo_rojo.txt` | `d2c0bd9` · `evidencias/tdd/UT-01a_modelo_verde.txt` | Sin refactorización |
| 2 | 2026-11-16 | EXTRA-reservacion-estados | Solo se permiten los estados VIGENTE y CANCELADA | `4f3c681` · `evidencias/tdd/EXTRA-reservacion-estados_rojo.txt` | `738169b` · `evidencias/tdd/EXTRA-reservacion-estados_verde.txt` | Sin refactorización |
| 3 | 2026-11-16 | EXTRA-sala-str | str(sala) devuelve su nombre | `d65b492` · `evidencias/tdd/EXTRA-sala-str_rojo.txt` | `ed9fe24` · `evidencias/tdd/EXTRA-sala-str_verde.txt` | Sin refactorización |
| 4 | 2026-11-16 | EXTRA-reservacion-str | str(reservacion) identifica sala, fecha, horario y estado | `c14d307` · `evidencias/tdd/EXTRA-reservacion-str_rojo.txt` | `82e5d1a` · `evidencias/tdd/EXTRA-reservacion-str_verde.txt` | Sin refactorización |
| 5 | 2026-11-16 | EXTRA-salas-iniciales | La migración de datos deja las cuatro salas obligatorias | `f79ed9b` · `evidencias/tdd/EXTRA-salas-iniciales_rojo.txt` | `b927af9` · `evidencias/tdd/EXTRA-salas-iniciales_verde.txt` | Sin refactorización |
| 6 | 2026-11-16 | EXTRA-usuarios-prueba-a_crea | El comando crea estudiante1 y estudiante2 con la contraseña documentada | `c8897d3` · `evidencias/tdd/EXTRA-usuarios-prueba-a_crea_rojo.txt` | `3756bc0` · `evidencias/tdd/EXTRA-usuarios-prueba-a_crea_verde.txt` | Sin refactorización |
| 7 | 2026-11-16 | EXTRA-usuarios-prueba-b_restablece | Reejecutar el comando es seguro y restablece la contraseña | `f7d8514` · `evidencias/tdd/EXTRA-usuarios-prueba-b_restablece_rojo.txt` | `598ddd8` · `evidencias/tdd/EXTRA-usuarios-prueba-b_restablece_verde.txt` | Sin refactorización |
| 8 | 2026-11-16 | EXTRA-login-a_formulario | La página de inicio de sesión responde y usa su plantilla | `02a3a92` · `evidencias/tdd/EXTRA-login-a_formulario_rojo.txt` | `44eabd8` · `evidencias/tdd/EXTRA-login-a_formulario_verde.txt` | Prueba con `reverse` · `evidencias/tdd/EXTRA-login-a_formulario_refactor.txt` |
| 9 | 2026-11-16 | EXTRA-lista-anonimo | La lista de reservaciones exige sesión | `6f965f3` · `evidencias/tdd/EXTRA-lista-anonimo_rojo.txt` | `2988a98` · `evidencias/tdd/EXTRA-lista-anonimo_verde.txt` | Sin refactorización |
| 10 | 2026-11-16 | EXTRA-lista-plantilla | Un usuario autenticado ve su lista (vacía) con la plantilla correcta | `95e57ba` · `evidencias/tdd/EXTRA-lista-plantilla_rojo.txt` | `907651a` · `evidencias/tdd/EXTRA-lista-plantilla_verde.txt` | Sin refactorización |
| 11 | 2026-11-16 | EXTRA-login-b_redireccion | Tras iniciar sesión se llega a la lista | `4f239a8` · `evidencias/tdd/EXTRA-login-b_redireccion_rojo.txt` | `dd559e6` · `evidencias/tdd/EXTRA-login-b_redireccion_verde.txt` | Sin refactorización |
| 12 | 2026-11-16 | EXTRA-logout | Cerrar sesión por POST devuelve al inicio de sesión | `1c400ad` · `evidencias/tdd/EXTRA-logout_rojo.txt` | `c392fc2` · `evidencias/tdd/EXTRA-logout_verde.txt` | Sin refactorización |
| 13 | 2026-11-16 | EXTRA-raiz-redirige | La raíz del sitio lleva a la lista | `908200f` · `evidencias/tdd/EXTRA-raiz-redirige_rojo.txt` | `87450d5` · `evidencias/tdd/EXTRA-raiz-redirige_verde.txt` | Sin refactorización |
| 14 | 2026-11-16 | UT-11 | El formulario de nueva reservación exige sesión | `4029cf4` · `evidencias/tdd/UT-11_rojo.txt` | `57447e7` · `evidencias/tdd/UT-11_verde.txt` | Sin refactorización |
