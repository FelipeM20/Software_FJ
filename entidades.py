"""Clase abstracta base de todas las entidades del sistema."""
from abc import ABC, abstractmethod

from validaciones import validar_identificador


class Entidad(ABC):
    """Características comunes: identificador único e interfaz mínima obligatoria."""

    PREFIJO = "ENT"

    def __init__(self, identificador):
        self._identificador = validar_identificador(identificador, self.PREFIJO)

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def describir(self):
        """Descripción legible de la entidad (sin datos sensibles)."""

    @abstractmethod
    def validar(self):
        """Verifica la consistencia interna; lanza DatosInvalidos si falla."""

    def __str__(self):
        return self.describir()

    def __repr__(self):
        return f"{type(self).__name__}(id={self._identificador!r})"

    def __eq__(self, otro):
        return type(self) is type(otro) and self._identificador == otro._identificador

    def __hash__(self):
        return hash((type(self).__name__, self._identificador))
