# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto de la **Fase 4 – Programación (213023)**, UNAD · ECBTI · Ingeniería de Sistemas.

## Descripción

Aplicación de consola en Python que gestiona clientes, servicios y reservas de la empresa ficticia
**Software FJ** usando programación orientada a objetos. Toda la información vive en objetos y
listas en memoria (**sin bases de datos**); los archivos solo se usan para el log.

## Objetivo general

Desarrollar un sistema estable, modular y extensible que continúe funcionando ante errores de ejecución.

## Objetivos específicos

* Aplicar abstracción, herencia, polimorfismo y encapsulación.
* Validar estrictamente los datos y controlar las transiciones de estado de las reservas.
* Implementar excepciones personalizadas y manejo avanzado (`try/except/else/finally`, `raise ... from`).
* Registrar eventos y errores con `logging` en `logs/sistema.log`.
* Demostrar el comportamiento con 21 simulaciones y 37 pruebas unitarias.

## Tecnologías

Python 3.8+ (probado en 3.12), solo biblioteca estándar (`abc`, `enum`, `functools`, `logging`, `unittest`).

## Instalación (Windows 10/11)

1. Instale Python desde https://www.python.org/downloads/ marcando **"Add python.exe to PATH"**.
2. Descomprima el ZIP, abra **PowerShell** o **CMD** dentro de la carpeta `Software\\\_FJ`.
3. No hay dependencias que instalar (`requirements.txt` está vacío a propósito).

## Ejecución

```
python main.py                          # simulaciones + informe general (use py main.py si "python" no responde)
python -m unittest discover -s tests -v # pruebas unitarias
```

Código de salida: 0 = todo APROBADO, 1 = alguna simulación fallida, 2 = error crítico.

## Estructura

```
Software\\\_FJ/
├── main.py                  # punto de entrada (función main)
├── excepciones.py           # jerarquía de excepciones personalizadas
├── validaciones.py          # validadores reutilizables (correo, teléfono, documento, ids, números)
├── entidades.py             # clase abstracta Entidad
├── clientes.py              # Cliente (encapsulación, @property)
├── servicios.py             # Servicio (abstracta), ReservaSala, AlquilerEquipo, AsesoriaEspecializada, Tarifas
├── reservas.py              # Reserva y EstadoReserva (máquina de estados)
├── sistema\\\_gestion.py       # SistemaGestion: listas internas y coordinación
├── simulaciones.py          # 21 simulaciones con reporte
├── configuracion\\\_logging.py # crea logs/sistema.log
├── logs/sistema.log         # generado automáticamente
├── tests/test\\\_sistema.py    # 37 pruebas unittest
└── docs/                    # matriz de trazabilidad, guía GitHub, auditoría final
```

Dependencias entre módulos (sin ciclos): `excepciones` ← `validaciones` ← `entidades` ← `clientes`/`servicios` ← `reservas` ← `sistema\\\_gestion` ← `simulaciones` ← `main`.

## Clases

|Clase|Rol|
|-|-|
|`Entidad` (abstracta)|Identificador validado (`PPP-NNN`); abstractos `describir()` y `validar()`|
|`Cliente(Entidad)`|Nombre, apellido, documento (solo lectura), correo, teléfono, estado; `actualizar()` atómico|
|`Servicio(Entidad)` (abstracta)|Nombre, descripción, precio base, disponibilidad; abstractos `calcular\\\_costo\\\_base`, `validar\\\_parametros`, `describir`|
|`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`|Servicios con reglas y tarifas propias|
|`Tarifas`|Única fuente de IVA (19 %), descuento máximo (30 %), factores y límites|
|`Reserva(Entidad)`|Cliente + servicio + fecha + duración + costo; `confirmar`, `cancelar`, `procesar`|
|`SistemaGestion`|Listas de clientes/servicios/reservas, operaciones, informes y `ejecutar\\\_operacion`|

## Principios POO

* **Abstracción:** `Entidad` y `Servicio` usan `abc.ABC`; no se pueden instanciar (probado).
* **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`; tres servicios heredan de `Servicio`.
* **Polimorfismo:** `calcular\\\_costo\\\_base()` y `describir()` se resuelven según la clase; `Servicio.calcular\\\_costo()` los usa sin conocer el tipo concreto.
* **Encapsulación:** atributos privados con `@property`; validación en cada setter; listas devueltas como `tuple`.
* **Sobrecarga (equivalente en Python):** `calcular\\\_costo(duracion=None, \\\*, impuestos=False, descuento=None)` cubre base / con IVA / con descuento / ambos, y `functools.singledispatchmethod` en `valor\\\_descuento` distingue `float` (fracción), `int` (monto fijo), `str` ("10%") y `None`. Python no tiene sobrecarga tradicional como Java.

## Reglas de negocio

Costo base = tarifa/hora × factor × horas (× cantidad en equipos) → descuento sobre la base (máx. 30 %) → IVA 19 % sobre el valor descontado. Salas y asesorías son recursos exclusivos: una reserva activa por día.

## Manejo de excepciones

Jerarquía: `ErrorSoftwareFJ` → `DatosInvalidos`, `ErrorCliente`, `ErrorServicio` (→ `ServicioNoDisponible`), `ErrorReserva` (→ `ReservaNoEncontrada`, `OperacionNoPermitida`).

|Mecanismo|Dónde|
|-|-|
|`try/except`|`Reserva.procesar`, `SistemaGestion.\\\_procesar\\\_reserva`|
|`try/except/else`|`registrar\\\_cliente`, `crear\\\_servicio`, `crear\\\_reserva` (el alta solo ocurre en `else`)|
|`try/except/finally`|mismos métodos (`finally` deja traza DEBUG) y `main()`|
|`raise ... from`|`DatosInvalidos` → `ErrorCliente`/`ErrorServicio`/`ErrorReserva`; `ValueError` → `DatosInvalidos` en fechas; `KeyError` → `OperacionNoPermitida`|
|Específicas antes que generales|`ejecutar\\\_operacion`: `ErrorSoftwareFJ` y luego `Exception`|
|Errores inesperados sin caída|`ejecutar\\\_operacion` usa `logger.exception` y devuelve `ResultadoOperacion`|

## Logging

`configurar\\\_logging()` crea `logs/` y `sistema.log` (modo append, UTF-8). Formato: `fecha hora | NIVEL | módulo | mensaje`. Niveles: DEBUG (cierres de intento), INFO (altas, confirmaciones), WARNING (validaciones rechazadas), ERROR (errores inesperados con traceback), CRITICAL (fallo no controlado en `main`). No se registran documentos, correos ni teléfonos (hay una prueba que lo verifica).

## Simulaciones (21)

Cubren las 10 obligatorias (marcadas "Obligatoria N" en su nombre) y 11 adicionales: cliente duplicado, servicio no disponible creado, cancelación válida, confirmar reserva cancelada, conflicto de fecha, fecha pasada, variantes de cálculo, error inesperado (`1/0`) y reserva posterior. Tras cada rechazo se verifica que el estado no cambió y que el sistema sigue operando. Cada una muestra número, nombre, datos, esperado, obtenido y estado (APROBADA/FALLIDA).

## Ejemplo de ejecución

```
\\\[Prueba 02] Registro con correo inválido (Obligatoria 2)
   Esperado:   Rechazo controlado: ErrorCliente
   Obtenido:   ErrorCliente: No fue posible registrar el cliente: El correo electrónico no tiene un formato válido.
   Continuidad: OK (estado intacto y sistema operativo)
   Estado:     APROBADA
...
RESUMEN: 21/21 simulaciones APROBADAS
```

## \## Autor

## Proyecto desarrollado de forma individual por:

## 

## | Nombre | Usuario GitHub | Responsabilidad |

## |---|---|---|

## | Juan Felipe Mahecha Leal | FelipeM20 | Diseño, desarrollo, pruebas y documentación completos |

## 

## \## Repositorio

## https://github.com/FelipeM20/Software\_FJ


## Ejecución en Windows y pruebas
Verificado en Windows 10/11 con Python 3.15. Si el comando `python` no responde, use la ruta completa del intérprete o `py`.

Ejecutar el programa (resultado esperado: 21/21 simulaciones APROBADAS):

```
python main.py
```

Ejecutar las pruebas unitarias (resultado esperado: Ran 37 tests ... OK):

```
python -m unittest discover -s tests -v
```

El archivo de registro se genera automáticamente en `logs/sistema.log`.