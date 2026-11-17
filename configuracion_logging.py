"""Configuración centralizada del logging (módulo estándar de Python)."""
import logging
from pathlib import Path

NOMBRE_LOGGER = "software_fj"
DIRECTORIO_LOGS = Path(__file__).resolve().parent / "logs"
ARCHIVO_LOG = "sistema.log"
FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


def cerrar_logging():
    """Cierra y retira los manejadores (necesario antes de borrar el archivo en Windows)."""
    logger = logging.getLogger(NOMBRE_LOGGER)
    for manejador in list(logger.handlers):
        manejador.close()
        logger.removeHandler(manejador)


def configurar_logging(directorio=None, nivel=logging.DEBUG, consola=False):
    """Crea el directorio ``logs`` y el archivo ``sistema.log`` si no existen.

    Devuelve el logger raíz de la aplicación ("software_fj"); los módulos usan
    loggers hijos ("software_fj.reservas", etc.) que heredan esta configuración.
    """
    carpeta = Path(directorio) if directorio else DIRECTORIO_LOGS
    carpeta.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(NOMBRE_LOGGER)
    cerrar_logging()  # evita manejadores duplicados si se llama más de una vez
    logger.setLevel(nivel)
    logger.propagate = False
    formateador = logging.Formatter(FORMATO, FORMATO_FECHA)
    archivo = logging.FileHandler(carpeta / ARCHIVO_LOG, mode="a", encoding="utf-8")
    archivo.setFormatter(formateador)
    logger.addHandler(archivo)
    if consola:
        salida = logging.StreamHandler()
        salida.setLevel(logging.WARNING)
        salida.setFormatter(formateador)
        logger.addHandler(salida)
    return logger
