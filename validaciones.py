"""Funciones de validación reutilizables. Lanzan DatosInvalidos con mensajes
comprensibles que NO incluyen el valor recibido (evita registrar datos personales)."""
import math
import re
from numbers import Real

from excepciones import DatosInvalidos

_PATRON_CORREO = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$")
_PATRON_ID = re.compile(r"^([A-Z]{3})-([0-9]{3,})$")


def requerir_texto(valor, campo, minimo=2, maximo=80):
    """Exige texto no vacío; normaliza espacios y valida la longitud."""
    if valor is None:
        raise DatosInvalidos(f"El campo '{campo}' es obligatorio.", campo)
    if not isinstance(valor, str):
        raise DatosInvalidos(f"El campo '{campo}' debe ser texto.", campo)
    limpio = " ".join(valor.split())
    if not limpio:
        raise DatosInvalidos(f"El campo '{campo}' no puede estar vacío.", campo)
    if not minimo <= len(limpio) <= maximo:
        raise DatosInvalidos(
            f"El campo '{campo}' debe tener entre {minimo} y {maximo} caracteres.", campo)
    return limpio


def validar_correo(correo):
    texto = requerir_texto(correo, "correo electrónico", 6, 80).lower()
    if " " in texto or ".." in texto or not _PATRON_CORREO.match(texto):
        raise DatosInvalidos("El correo electrónico no tiene un formato válido.", "correo")
    return texto


def validar_telefono(telefono):
    texto = requerir_texto(telefono, "teléfono", 7, 20)
    digitos = re.sub(r"[\s-]", "", texto)
    if digitos.startswith("+"):
        digitos = digitos[1:]
    if not re.fullmatch(r"[0-9]{7,15}", digitos):
        raise DatosInvalidos("El teléfono debe contener entre 7 y 15 dígitos.", "teléfono")
    return texto


def validar_documento(documento):
    if isinstance(documento, int) and not isinstance(documento, bool):
        documento = str(documento)
    texto = requerir_texto(documento, "documento", 5, 12)
    if not re.fullmatch(r"[0-9]{5,12}", texto):
        raise DatosInvalidos("El documento debe contener solo dígitos (5 a 12).", "documento")
    return texto


def validar_identificador(valor, prefijo=None):
    """Formato PPP-NNN (tres letras mayúsculas, guion y al menos tres dígitos)."""
    coincidencia = _PATRON_ID.match(valor) if isinstance(valor, str) else None
    if coincidencia is None or (prefijo and coincidencia.group(1) != prefijo):
        esperado = f"{prefijo}-001" if prefijo else "AAA-001"
        raise DatosInvalidos(f"Identificador inválido; formato esperado: {esperado}.", "identificador")
    return valor


def requerir_numero_positivo(valor, campo, maximo=None):
    if valor is None:
        raise DatosInvalidos(f"El campo '{campo}' es obligatorio.", campo)
    if isinstance(valor, bool) or not isinstance(valor, Real):
        raise DatosInvalidos(f"El campo '{campo}' debe ser numérico.", campo)
    if not math.isfinite(valor) or valor <= 0:
        raise DatosInvalidos(f"El campo '{campo}' debe ser mayor que cero.", campo)
    if maximo is not None and valor > maximo:
        raise DatosInvalidos(f"El campo '{campo}' no puede superar {maximo}.", campo)
    return valor


def requerir_entero_positivo(valor, campo, maximo=None):
    if valor is None:
        raise DatosInvalidos(f"El campo '{campo}' es obligatorio.", campo)
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise DatosInvalidos(f"El campo '{campo}' debe ser un número entero.", campo)
    return requerir_numero_positivo(valor, campo, maximo)


def requerir_opcion(valor, campo, opciones):
    texto = requerir_texto(valor, campo, 1, 40).lower()
    if texto not in opciones:
        raise DatosInvalidos(
            f"El campo '{campo}' debe ser uno de: {', '.join(sorted(opciones))}.", campo)
    return texto
