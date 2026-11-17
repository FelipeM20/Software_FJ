# Guía de trabajo colaborativo con GitHub (5 integrantes)

> Esta guía es una **propuesta**. Los commits, ramas, pull requests e issues deben crearse realmente
> por cada integrante; no se deben simular ni copiar entre cuentas.

## 1. Distribución de responsabilidades
| # | Rama | Archivos | Issue asignado |
|---|---|---|---|
| 1 | `feature/excepciones-logging` | excepciones.py, validaciones.py, configuracion_logging.py | #1 Excepciones, validadores y logging |
| 2 | `feature/entidad-cliente` | entidades.py, clientes.py | #2 Entidad abstracta y Cliente |
| 3 | `feature/servicios` | servicios.py | #3 Servicios, tarifas y cálculo de costos |
| 4 | `feature/reservas-sistema` | reservas.py, sistema_gestion.py | #4 Reserva y SistemaGestion |
| 5 | `feature/simulaciones-docs` | simulaciones.py, main.py, README.md, tests/, docs/ | #5 Simulaciones, pruebas y documentación |

Orden de integración sugerido (por dependencias): 1 → 2 y 3 → 4 → 5. Cada integrante hace
revisión cruzada: 1 revisa a 2, 2 a 3, 3 a 4, 4 a 5, 5 a 1 (al menos un comentario real por PR).
Cada integrante debe escribir además las pruebas de su propio módulo en `tests/`.

## 2. Comandos (Windows, PowerShell o Git Bash)
Quien crea el repositorio (en github.com, vacío, `Software_FJ`) y lo sube:
```
git init -b main
git add .
git commit -m "chore: estructura inicial del proyecto Software FJ"
git remote add origin https://github.com/<usuario>/Software_FJ.git
git push -u origin main
```
Cada integrante:
```
git clone https://github.com/<usuario>/Software_FJ.git
cd Software_FJ
git checkout -b feature/<su-rama>
# trabajar y probar: python -m unittest discover -s tests
git add <sus archivos>
git commit -m "feat(servicios): agregar cálculo de costo con impuestos y descuentos"
git push -u origin feature/<su-rama>
```
Luego, en GitHub: **Compare & pull request** → asignar revisor → vincular el issue (`Closes #3`) → fusionar a `main` tras la revisión. Antes de empezar cada sesión: `git pull origin main`.
Para resolver conflictos: `git checkout feature/<rama>` → `git merge main` → resolver → `git commit`.

## 3. Ejemplos de mensajes de commit (convención `tipo(ámbito): descripción`)
- `feat(excepciones): crear jerarquía de excepciones personalizadas`
- `feat(clientes): validar correo y prevenir duplicados`
- `feat(servicios): implementar descuento con singledispatchmethod`
- `fix(reservas): impedir confirmar una reserva cancelada`
- `test(sistema): agregar pruebas de continuidad tras errores`
- `docs(readme): documentar manejo de excepciones y logging`

## 4. Issues sugeridos (crear los cinco anteriores más)
#6 Revisión de código cruzada · #7 Matriz de trazabilidad · #8 Evidencias de ejecución y video/capturas.

## 5. Evidencias reales que debe generar el equipo
1. Captura del repositorio con las 5 ramas y sus commits (cada integrante con varios commits propios).
2. Pull Requests fusionados con comentarios de revisión.
3. Issues cerrados y vinculados a los PR.
4. Captura de `python main.py` (21/21 APROBADAS) y de las pruebas unitarias en verde.
5. `logs/sistema.log` generado en la máquina del equipo.
6. README con nombres reales, usuarios de GitHub y enlace del repositorio.
