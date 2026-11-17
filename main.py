"""Punto de entrada de Software FJ: ejecuta python main.py"""
import sys

from configuracion_logging import configurar_logging
from sistema_gestion import SistemaGestion
from simulaciones import ejecutar_simulaciones


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # acentos correctos en consolas de Windows
    except (AttributeError, ValueError):
        pass
    logger = configurar_logging()
    logger.info("Inicio del programa Software FJ")
    codigo = 0
    try:
        sistema = SistemaGestion()
        resultados = ejecutar_simulaciones(sistema)
        print()
        print(sistema.mostrar_informacion_general())
        if any(r.estado != "APROBADA" for r in resultados):
            logger.error("Hay simulaciones FALLIDAS; revise el reporte")
            codigo = 1
    except Exception:  # noqa: BLE001 - último recurso: registrar y salir con código
        logger.critical("Error crítico no controlado en main()", exc_info=True)
        print("Error crítico: revise logs/sistema.log")
        codigo = 2
    finally:
        logger.info("Finalización del programa (código de salida %s)", codigo)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
