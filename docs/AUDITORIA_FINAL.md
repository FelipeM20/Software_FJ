# Auditoría final y lista de verificación (rúbrica)

Verificado ejecutando el proyecto en Python 3.12 (Linux): `python main.py` → 21/21 simulaciones APROBADAS;
`python -m unittest discover -s tests` → 37 pruebas OK; compilación y verificación de imports sin errores ni ciclos.
**No se ejecutó en Windows** (el código no usa nada específico de plataforma; el equipo debe confirmarlo).

| Requisito | Estado | Comprobación |
|---|---|---|
| Entidad y Servicio realmente abstractas | CUMPLIDO | TypeError al instanciar (test) |
| Cliente con encapsulación, @property, validación, duplicados | CUMPLIDO | TestCliente, S2–S4 |
| Tres servicios con polimorfismo real | CUMPLIDO | test_polimorfismo |
| Reglas de negocio y tarifas centralizadas | CUMPLIDO | `Tarifas` + docstring |
| Variantes de cálculo (base, IVA, descuento, ambos) | CUMPLIDO | pruebas y S19 con valores calculados a mano |
| Reserva con estados controlados | CUMPLIDO | TestReserva, S13–S15 |
| SistemaGestion con listas y todas las operaciones | CUMPLIDO | TestSistema |
| 7 excepciones personalizadas | CUMPLIDO | TestExcepciones |
| try/except, else, finally, `raise from`, específicas antes de generales | CUMPLIDO | código + pruebas de `__cause__` |
| Errores inesperados sin cerrar la app | CUMPLIDO | S20, test_continuidad_tras_errores |
| Logging con archivo automático, 5 niveles, fecha/hora, `logger.exception` | CUMPLIDO | TestLogging; CRITICAL solo existe en `main()` y no se provoca en las simulaciones |
| ≥ 10 simulaciones con los 6 campos solicitados | CUMPLIDO | 21 simulaciones |
| Continuidad tras cada fallo | CUMPLIDO | campo "Continuidad" |
| Sin bases de datos ni dependencias | CUMPLIDO | revisión de imports |
| Ejecutable desde main.py | CUMPLIDO | ejecución real |
| README, matriz, guía GitHub | CUMPLIDO | docs/ y README.md |
| Nombres reales, usuarios y enlace de GitHub en README | PENDIENTE DE EVIDENCIA | datos del equipo |
| Ramas, commits, PR, issues de los 5 integrantes | PENDIENTE DE EVIDENCIA | solo el equipo puede generarlo |
| Ejecución en Windows 10/11 | PENDIENTE DE EVIDENCIA | capturas del equipo |
| Requisitos NO CUMPLIDOS | ninguno identificado | — |

Limitaciones conocidas: la unicidad de reserva por día (salas y asesorías) es una regla de negocio propuesta, no del enunciado;
no se modelan horas dentro del día.
