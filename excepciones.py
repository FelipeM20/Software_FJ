"""Excepciones personalizadas de Software FJ.

Jerarquía:
    Exception
    └── ErrorSoftwareFJ (base del sistema)
        ├── DatosInvalidos
        ├── ErrorCliente
        ├── ErrorServicio
        │   └── ServicioNoDisponible
        └── ErrorReserva
            ├── ReservaNoEncontrada
            └── OperacionNoPermitida
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base de la aplicación; permite capturar cualquier error propio."""


class DatosInvalidos(ErrorSoftwareFJ):
    """Un dato falta, tiene tipo incorrecto, formato inválido o es inconsistente."""

    def __init__(self, mensaje="Datos inválidos.", campo=None):
        super().__init__(mensaje)
        self.campo = campo


class ErrorCliente(ErrorSoftwareFJ):
    """Error en el registro, consulta o actualización de clientes."""


class ErrorServicio(ErrorSoftwareFJ):
    """Error en la creación o consulta de servicios."""


class ServicioNoDisponible(ErrorServicio):
    """El servicio solicitado no está disponible (o ya está ocupado)."""


class ErrorReserva(ErrorSoftwareFJ):
    """Error en la creación o gestión de reservas."""


class ReservaNoEncontrada(ErrorReserva):
    """La reserva consultada no existe en el sistema."""


class OperacionNoPermitida(ErrorReserva):
    """La operación no es válida para el estado actual del objeto."""
