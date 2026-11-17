"""SistemaGestion: coordina clientes, servicios y reservas (todo en listas en memoria)."""
import logging
from dataclasses import dataclass
from typing import Any, Optional

from clientes import Cliente
from excepciones import (DatosInvalidos, ErrorCliente, ErrorReserva, ErrorServicio,
                         ErrorSoftwareFJ, OperacionNoPermitida, ReservaNoEncontrada,
                         ServicioNoDisponible)
from reservas import EstadoReserva, Reserva, normalizar_fecha
from servicios import TIPOS_SERVICIO

logger = logging.getLogger("software_fj.sistema")


@dataclass(frozen=True)
class ResultadoOperacion:
    exito: bool
    mensaje: str
    valor: Any = None
    error: Optional[Exception] = None


class SistemaGestion:
    def __init__(self):
        self._clientes = []
        self._servicios = []
        self._reservas = []
        self._sig_cliente = self._sig_servicio = self._sig_reserva = 1

    # ------------------------------------------------------------ utilidades
    @staticmethod
    def _buscar(lista, identificador):
        return next((e for e in lista if e.identificador == identificador), None)

    # --------------------------------------------------------------- clientes
    def registrar_cliente(self, nombre=None, apellido=None, documento=None,
                          correo=None, telefono=None):
        identificador = f"CLI-{self._sig_cliente:03d}"
        try:
            cliente = Cliente(identificador, nombre, apellido, documento, correo, telefono)
            self._verificar_cliente_unico(cliente)
        except DatosInvalidos as exc:
            logger.warning("Registro de cliente rechazado por validación: %s", exc)
            raise ErrorCliente(f"No fue posible registrar el cliente: {exc}") from exc
        except ErrorCliente as exc:
            logger.warning("Registro de cliente rechazado: %s", exc)
            raise
        else:
            self._clientes.append(cliente)
            self._sig_cliente += 1
            logger.info("Cliente registrado: %s", cliente.identificador)
            return cliente
        finally:
            logger.debug("Fin del intento de registro de cliente (%s)", identificador)

    def _verificar_cliente_unico(self, nuevo):
        for existente in self._clientes:
            if existente.documento == nuevo.documento:
                raise ErrorCliente("Ya existe un cliente con ese documento.")
            if existente.correo == nuevo.correo:
                raise ErrorCliente("Ya existe un cliente con ese correo electrónico.")

    def consultar_cliente(self, identificador):
        cliente = self._buscar(self._clientes, identificador)
        if cliente is None:
            raise ErrorCliente(f"No existe el cliente {identificador}.")
        return cliente

    def listar_clientes(self):
        return tuple(self._clientes)

    # --------------------------------------------------------------- servicios
    def crear_servicio(self, tipo, **datos):
        clase = TIPOS_SERVICIO.get(tipo.lower()) if isinstance(tipo, str) else None
        if clase is None:
            logger.warning("Tipo de servicio desconocido solicitado")
            raise ErrorServicio(
                f"Tipo de servicio no soportado. Opciones: {', '.join(sorted(TIPOS_SERVICIO))}.")
        identificador = f"SRV-{self._sig_servicio:03d}"
        try:
            servicio = clase(identificador, **datos)
        except DatosInvalidos as exc:
            logger.warning("Creación de servicio rechazada por validación: %s", exc)
            raise ErrorServicio(f"No fue posible crear el servicio: {exc}") from exc
        except TypeError as exc:
            logger.warning("Parámetros incorrectos al crear servicio: %s", exc)
            raise ErrorServicio("Parámetros incorrectos para crear el servicio.") from exc
        else:
            self._servicios.append(servicio)
            self._sig_servicio += 1
            logger.info("Servicio creado: %s (%s)", servicio.identificador, clase.__name__)
            return servicio
        finally:
            logger.debug("Fin del intento de creación de servicio (%s)", identificador)

    def consultar_servicio(self, identificador):
        servicio = self._buscar(self._servicios, identificador)
        if servicio is None:
            raise ErrorServicio(f"No existe el servicio {identificador}.")
        return servicio

    def listar_servicios(self, solo_disponibles=False):
        return tuple(s for s in self._servicios if s.disponible or not solo_disponibles)

    def validar_disponibilidad(self, servicio_id, fecha=None):
        servicio = self.consultar_servicio(servicio_id)
        servicio.validar_disponibilidad()
        if fecha is not None:
            try:
                dia = normalizar_fecha(fecha)
            except DatosInvalidos as exc:
                raise ErrorReserva(f"Fecha inválida: {exc}") from exc
            self._verificar_conflicto(servicio, dia)
        return True

    def _verificar_conflicto(self, servicio, dia):
        """Un recurso exclusivo (sala, asesor) admite una sola reserva activa por día."""
        if not servicio.exclusivo:
            return
        for r in self._reservas:
            if (r.servicio is servicio and r.fecha == dia
                    and r.estado is not EstadoReserva.CANCELADA):
                raise ServicioNoDisponible(
                    f"El servicio {servicio.identificador} ya está reservado el {dia.isoformat()}.")

    # ---------------------------------------------------------------- reservas
    def crear_reserva(self, cliente_id, servicio_id, fecha, duracion_horas=None,
                      descuento=None, aplicar_impuestos=True):
        cliente = self.consultar_cliente(cliente_id)
        servicio = self.consultar_servicio(servicio_id)
        identificador = f"RES-{self._sig_reserva:03d}"
        try:
            reserva = Reserva(identificador, cliente, servicio, fecha, duracion_horas,
                              descuento, aplicar_impuestos)
            self._verificar_conflicto(servicio, reserva.fecha)
        except DatosInvalidos as exc:
            logger.warning("Creación de reserva rechazada por validación: %s", exc)
            raise ErrorReserva(f"No fue posible crear la reserva: {exc}") from exc
        except (ServicioNoDisponible, OperacionNoPermitida) as exc:
            logger.warning("Creación de reserva rechazada (%s): %s", type(exc).__name__, exc)
            raise
        else:
            self._reservas.append(reserva)
            self._sig_reserva += 1
            logger.info("Reserva creada: %s (cliente %s, servicio %s)", identificador,
                        cliente_id, servicio_id)
            return reserva
        finally:
            logger.debug("Fin del intento de creación de reserva (%s)", identificador)

    def consultar_reserva(self, identificador):
        reserva = self._buscar(self._reservas, identificador)
        if reserva is None:
            logger.warning("Reserva inexistente consultada: %s", identificador)
            raise ReservaNoEncontrada(f"No existe la reserva {identificador}.")
        return reserva

    def listar_reservas(self, estado=None):
        return tuple(r for r in self._reservas if estado is None or r.estado is estado)

    def confirmar_reserva(self, identificador):
        return self._procesar_reserva(identificador, "confirmar")

    def cancelar_reserva(self, identificador):
        return self._procesar_reserva(identificador, "cancelar")

    def _procesar_reserva(self, identificador, operacion):
        reserva = self.consultar_reserva(identificador)
        try:
            reserva.procesar(operacion)
        except (OperacionNoPermitida, ServicioNoDisponible) as exc:
            logger.warning("No se pudo %s la reserva %s: %s", operacion, identificador, exc)
            raise
        return reserva

    # -------------------------------------------------------------- informes
    def resumen(self):
        por_estado = {e.value: len(self.listar_reservas(e)) for e in EstadoReserva}
        ingresos = sum(r.costo_total for r in self._reservas
                       if r.estado is EstadoReserva.CONFIRMADA)
        return {"clientes": len(self._clientes), "servicios": len(self._servicios),
                "reservas": len(self._reservas), "reservas_por_estado": por_estado,
                "ingresos_confirmados": round(ingresos, 2)}

    def mostrar_informacion_general(self):
        r = self.resumen()
        lineas = ["=== INFORMACIÓN GENERAL - SOFTWARE FJ ===",
                  f"Clientes registrados: {r['clientes']}",
                  f"Servicios creados:    {r['servicios']}",
                  f"Reservas totales:     {r['reservas']} {r['reservas_por_estado']}",
                  f"Ingresos confirmados: ${r['ingresos_confirmados']:,.2f}", "--- Servicios ---"]
        lineas += [f"  {s.describir()} [{'disponible' if s.disponible else 'no disponible'}]"
                   for s in self._servicios]
        lineas.append("--- Reservas ---")
        lineas += [f"  {x.describir()}" for x in self._reservas]
        return "\n".join(lineas)

    # --------------------------------------------- manejo de errores de operaciones
    def ejecutar_operacion(self, operacion, *args, **kwargs):
        """Ejecuta una operación sin dejar caer la aplicación.

        Errores propios -> mensaje claro; errores inesperados -> logger.exception.
        Los específicos se capturan antes que el Exception general.
        """
        nombre = getattr(operacion, "__name__", repr(operacion))
        try:
            valor = operacion(*args, **kwargs)
        except ErrorSoftwareFJ as exc:
            logger.info("Operación '%s' rechazada de forma controlada (%s)",
                        nombre, type(exc).__name__)
            return ResultadoOperacion(False, str(exc), error=exc)
        except Exception as exc:  # noqa: BLE001 - red de seguridad deliberada
            logger.exception("Error inesperado en la operación '%s'", nombre)
            return ResultadoOperacion(
                False, "Ocurrió un error inesperado; fue registrado en el log.", error=exc)
        else:
            return ResultadoOperacion(True, "Operación completada.", valor)
