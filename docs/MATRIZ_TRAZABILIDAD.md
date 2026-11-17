# Matriz de trazabilidad (requisito → implementación → prueba → evidencia)

Pruebas: `tests/test_sistema.py` (T) y simulaciones (S, numeradas como en la salida de `main.py`).

| Requisito | Archivo | Clase / método | Prueba | Evidencia que debe presentar el equipo |
|---|---|---|---|---|
| Clase abstracta Entidad (abc) | entidades.py | `Entidad` | T `TestAbstraccion` | Captura de la prueba en verde |
| Cliente con @property, validación, estado | clientes.py | `Cliente`, `actualizar`, `_VALIDADORES` | T `TestCliente` | Commit de la rama del integrante 2 |
| Correo / ids / datos faltantes / duplicados | validaciones.py, sistema_gestion.py | `validar_correo`, `validar_identificador`, `_verificar_cliente_unico` | T `test_correos_invalidos`, `test_duplicados_y_encadenamiento`; S2, S3, S4 | Log con WARNING de rechazo |
| Servicio abstracto | servicios.py | `Servicio` | T `TestAbstraccion` | PR del integrante 3 |
| ReservaSala / AlquilerEquipo / AsesoriaEspecializada | servicios.py | clases homónimas | T `test_polimorfismo`, `test_parametros_invalidos`; S5, S8, S9 | Salida de simulaciones |
| Polimorfismo | servicios.py | `calcular_costo_base`, `describir` | T `test_polimorfismo` | Captura de la prueba |
| Tarifas centralizadas y documentadas | servicios.py | `Tarifas`, docstring del módulo | T `test_cuatro_variantes_de_calculo` | README (reglas de negocio) |
| Métodos "sobrecargados" (equivalente Python) | servicios.py | `calcular_costo`, `valor_descuento` (singledispatchmethod) | T `test_cuatro_variantes_de_calculo`, `test_descuentos_por_tipo_y_errores`; S19 | Salida S19 |
| Reserva: validación, costo, impuestos, descuentos | reservas.py | `Reserva.__init__` | T `TestReserva.test_creacion_y_costo`, `test_validaciones`; S6 | PR del integrante 4 |
| Transiciones de estado | reservas.py | `confirmar`, `cancelar`, `procesar` | T `test_transiciones_validas_e_invalidas`; S10, S13, S14, S15 | Salida de simulaciones |
| SistemaGestion con listas internas | sistema_gestion.py | `_clientes`, `_servicios`, `_reservas` y métodos públicos | T `TestSistema` | Informe de `mostrar_informacion_general()` |
| Disponibilidad | servicios.py, sistema_gestion.py | `validar_disponibilidad`, `_verificar_conflicto` | T `test_disponibilidad_y_conflictos`; S12, S17 | Salida S12/S17 |
| Excepciones personalizadas (7) | excepciones.py | jerarquía completa | T `TestExcepciones` | Archivo excepciones.py |
| try/except | reservas.py | `procesar` | T `test_procesar` | Código revisado en PR |
| try/except/else | sistema_gestion.py | `registrar_cliente`, `crear_servicio`, `crear_reserva` | T `test_ids_no_se_consumen_en_fallos` | Código revisado en PR |
| try/except/finally | sistema_gestion.py, reservas.py, main.py | `finally` con DEBUG | T `test_archivo_y_niveles` (DEBUG en log) | Líneas DEBUG del log |
| raise ... from | sistema_gestion.py, reservas.py | `__cause__` en conversiones | T `test_duplicados_y_encadenamiento`, `test_fecha_invalida_encadena_valueerror`, `test_crear_servicios` | Captura de la prueba |
| Específicas antes de generales; errores inesperados | sistema_gestion.py | `ejecutar_operacion` | T `test_ejecutar_operacion_controla_errores`; S20 | Línea ERROR con traceback en el log |
| Operaciones no permitidas | reservas.py | `OperacionNoPermitida` | T `test_transiciones_validas_e_invalidas`; S15 | Salida S15 |
| Logging (archivo automático, niveles, fecha/hora) | configuracion_logging.py | `configurar_logging` | T `TestLogging` | `logs/sistema.log` generado por el equipo al ejecutar |
| Sin datos personales en el log | sistema_gestion.py, validaciones.py | mensajes sin valores | T `test_no_registra_datos_personales` | Revisión del log |
| ≥ 10 simulaciones válidas e inválidas | simulaciones.py | `ejecutar_simulaciones` | T `TestSimulaciones` | Captura de `python main.py` |
| Continuidad tras errores | simulaciones.py, sistema_gestion.py | verificación de estado y `resumen()` | T `test_continuidad_tras_errores`; S2, S3, S4, S7, S12, S13, S15, S17, S18, S20 | Campo "Continuidad: OK" |
| Sin base de datos | todos | listas en memoria | búsqueda sin imports de BD | — |
| Punto de entrada main() | main.py | `main` | ejecución real | Captura de ejecución |
| GitHub: ramas, commits, PR, issues, 5 integrantes | docs/GUIA_GITHUB.md | — | — | **Evidencia real que solo el equipo puede generar** |

(S = número de simulación en `python main.py`: 1 Cliente OK, 2 correo inválido, 3 incompleto, 4 duplicado, 5 servicio sala, 6 reserva sala, 7 servicio inválido, 8 equipo, 9 asesoría, 10 reserva+confirmación, 11 servicio no disponible, 12 reserva no disponible, 13 cancelar inexistente, 14 cancelar válida, 15 confirmar cancelada, 16 reserva libre, 17 conflicto fecha, 18 fecha pasada, 19 costos, 20 error inesperado, 21 reserva posterior.)
