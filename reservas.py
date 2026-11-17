"""Clase Reserva: integra cliente y servicio y controla las transiciones de estado."""
import logging
from datetime import date, datetime
from enum import Enum

from clientes import Cliente, EstadoCliente
from entidades import Entidad
from excepciones import DatosInvalidos, OperacionNoPermitida
from servicios import Servicio

logger = logging.getLogger("software_fj.reservas")


class EstadoReserva(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"


def normalizar_fecha(fecha, hoy=None):
    """Convierte a ``date`` (acepta date, datetime o texto AAAA-MM-DD); no admite pasado."""
    hoy = hoy or date.today()
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    if isinstance(fecha, str):
        try:
            fecha = date.fromisoformat(fecha.strip())
        except ValueError as exc:
            raise DatosInvalidos("La fecha debe tener formato AAAA-MM-DD.", "fecha") from exc
    if not isinstance(fecha, date):
        raise DatosInvalidos("La fecha es obligatoria y debe ser válida.", "fecha")
    if fecha < hoy:
        raise DatosInvalidos("La fecha de la reserva no puede estar en el pasado.", "fecha")
    return fecha


class Reserva(Entidad):
    PREFIJO = "RES"

    def __init__(self, identificador, cliente, servicio, fecha, duracion_horas=None,
                 descuento=None, aplicar_impuestos=True, hoy=None):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise DatosInvalidos("La reserva requiere un cliente válido.", "cliente")
        if cliente.estado is not EstadoCliente.ACTIVO:
            raise OperacionNoPermitida("No se pueden crear reservas para un cliente inactivo.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidos("La reserva requiere un servicio válido.", "servicio")
        servicio.validar_disponibilidad()
        self._cliente = cliente
        self._servicio = servicio
        self._fecha = normalizar_fecha(fecha, hoy)
        self._duracion_horas = servicio.resolver_duracion(duracion_horas)
        self._descuento = descuento
        self._aplica_impuestos = bool(aplicar_impuestos)
        self._costo_total = servicio.calcular_costo(
            self._duracion_horas, impuestos=self._aplica_impuestos, descuento=descuento)
        self._estado = EstadoReserva.PENDIENTE

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def fecha(self):
        return self._fecha

    @property
    def duracion_horas(self):
        return self._duracion_horas

    @property
    def costo_total(self):
        return self._costo_total

    @property
    def estado(self):
        return self._estado

    def confirmar(self):
        if self._estado is EstadoReserva.CANCELADA:
            raise OperacionNoPermitida("No se puede confirmar una reserva cancelada.")
        if self._estado is EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitida("La reserva ya está confirmada.")
        self._servicio.validar_disponibilidad()
        self._estado = EstadoReserva.CONFIRMADA

    def cancelar(self):
        if self._estado is EstadoReserva.CANCELADA:
            raise OperacionNoPermitida("La reserva ya está cancelada.")
        self._estado = EstadoReserva.CANCELADA

    def procesar(self, operacion):
        """Ejecuta 'confirmar' o 'cancelar' controlando errores y registrando el resultado."""
        acciones = {"confirmar": self.confirmar, "cancelar": self.cancelar}
        try:
            accion = acciones[operacion]
        except KeyError as exc:
            raise OperacionNoPermitida(f"Operación desconocida: {operacion!r}.") from exc
        estado_previo = self._estado
        try:
            accion()
        except OperacionNoPermitida:
            logger.warning("Transición rechazada en %s: %s -> %s",
                           self.identificador, estado_previo.value, operacion)
            raise
        else:
            logger.info("Reserva %s: %s -> %s", self.identificador,
                        estado_previo.value, self._estado.value)
        finally:
            logger.debug("Fin de procesar(%s) sobre %s", operacion, self.identificador)

    def describir(self):
        return (f"Reserva {self.identificador} [{self._estado.value}] cliente "
                f"{self._cliente.identificador}, servicio {self._servicio.identificador}, "
                f"fecha {self._fecha.isoformat()}, {self._duracion_horas} h, "
                f"total ${self._costo_total:,.2f}")

    def validar(self):
        self._servicio.validar()
        self._cliente.validar()
        if self._costo_total <= 0:
            raise DatosInvalidos("El costo total de la reserva debe ser positivo.", "costo")
