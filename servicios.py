"""Servicios de Software FJ: clase abstracta Servicio y tres servicios especializados.

REGLAS DE NEGOCIO (centralizadas en ``Tarifas``)
- precio_base es la tarifa por hora (COP) de una unidad del servicio.
- Costo base = precio_base * factor de la variante * horas (* cantidad en equipos).
- Orden de cálculo: base -> descuento (sobre la base) -> IVA (sobre el valor ya descontado).
- Descuento máximo permitido: 30 % de la base.
- Sobrecarga en Python: parámetros opcionales/nombrados en ``calcular_costo`` y
  ``functools.singledispatchmethod`` en ``valor_descuento`` (float = fracción,
  int = monto fijo en pesos, str "10%" = porcentaje, None = sin descuento).
"""
import math
import re
from abc import abstractmethod
from functools import singledispatchmethod

from entidades import Entidad
from excepciones import DatosInvalidos, ServicioNoDisponible
from validaciones import (requerir_entero_positivo, requerir_numero_positivo,
                          requerir_opcion, requerir_texto)


class Tarifas:
    """Única fuente de verdad de tarifas y límites."""
    IVA = 0.19
    DESCUENTO_MAXIMO = 0.30
    PRECIO_BASE_MAXIMO = 10_000_000
    SALA_FACTOR_TIPO = {"reuniones": 1.0, "capacitacion": 1.5, "auditorio": 2.5}
    SALA_CAPACIDAD_MAXIMA = {"reuniones": 12, "capacitacion": 40, "auditorio": 150}
    SALA_DURACION_MAXIMA = 12
    EQUIPOS_PERMITIDOS = ("portatil", "proyector", "tablet", "servidor")
    EQUIPO_CANTIDAD_MAXIMA = 20
    EQUIPO_DURACION_MAXIMA = 720
    ASESORIA_FACTOR_MODALIDAD = {"virtual": 1.0, "presencial": 1.25}
    ASESORIA_DURACION_MAXIMA = 8


class Servicio(Entidad):
    """Comportamiento común de los servicios (clase abstracta)."""

    PREFIJO = "SRV"
    EXCLUSIVO = False  # True: un recurso único (no admite dos reservas el mismo día)

    def __init__(self, identificador, nombre=None, descripcion=None, precio_base=None,
                 duracion_horas=1, disponible=True):
        super().__init__(identificador)
        self._nombre = requerir_texto(nombre, "nombre", 3, 80)
        self._descripcion = requerir_texto(descripcion, "descripción", 3, 200)
        self._precio_base = requerir_numero_positivo(
            precio_base, "precio base", Tarifas.PRECIO_BASE_MAXIMO)
        if not isinstance(disponible, bool):
            raise DatosInvalidos("El campo 'disponible' debe ser verdadero o falso.", "disponible")
        self._disponible = disponible
        self._duracion_horas = self.validar_parametros(duracion_horas)

    @property
    def nombre(self):
        return self._nombre

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def precio_base(self):
        return self._precio_base

    @property
    def duracion_horas(self):
        return self._duracion_horas

    @property
    def exclusivo(self):
        return self.EXCLUSIVO

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            raise DatosInvalidos("La disponibilidad debe ser verdadero o falso.", "disponible")
        self._disponible = valor

    def validar_disponibilidad(self):
        if not self._disponible:
            raise ServicioNoDisponible(f"El servicio {self.identificador} no está disponible.")
        return True

    def resolver_duracion(self, duracion=None):
        """Duración efectiva: la indicada o, si es None, la estándar del servicio."""
        return self.validar_parametros(self._duracion_horas if duracion is None else duracion)

    def validar(self):
        requerir_texto(self._nombre, "nombre", 3, 80)
        requerir_numero_positivo(self._precio_base, "precio base", Tarifas.PRECIO_BASE_MAXIMO)
        self.validar_parametros(self._duracion_horas)

    # --- métodos abstractos (cada servicio los sobrescribe) ---
    @abstractmethod
    def calcular_costo_base(self, duracion=None):
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida y devuelve la duración (horas) según los límites del servicio."""

    @abstractmethod
    def describir(self):
        """Descripción legible del servicio."""

    # --- variantes de la misma operación (sobrecarga mediante opcionales) ---
    def calcular_costo(self, duracion=None, *, impuestos=False, descuento=None):
        base = self.calcular_costo_base(duracion)
        neto = base - self.valor_descuento(descuento, base)
        if impuestos:
            neto += neto * Tarifas.IVA
        return round(neto, 2)

    def calcular_costo_con_impuestos(self, duracion=None):
        return self.calcular_costo(duracion, impuestos=True)

    def calcular_costo_con_descuento(self, duracion=None, descuento=None):
        return self.calcular_costo(duracion, descuento=descuento)

    # --- sobrecarga por tipo del descuento ---
    @singledispatchmethod
    def valor_descuento(self, descuento, base):
        raise DatosInvalidos(
            f"Tipo de descuento no soportado: {type(descuento).__name__}.", "descuento")

    @valor_descuento.register(type(None))
    def _(self, descuento, base):
        return 0.0

    @valor_descuento.register(float)
    def _(self, descuento, base):
        if not (math.isfinite(descuento) and 0 <= descuento <= 1):
            raise DatosInvalidos("El descuento fraccional debe estar entre 0 y 1.", "descuento")
        return self._limitar_descuento(base * descuento, base)

    @valor_descuento.register(int)
    def _(self, descuento, base):
        if isinstance(descuento, bool) or descuento < 0:
            raise DatosInvalidos("El descuento fijo debe ser un entero no negativo.", "descuento")
        return self._limitar_descuento(float(descuento), base)

    @valor_descuento.register(str)
    def _(self, descuento, base):
        coincidencia = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*%\s*", descuento)
        if coincidencia is None:
            raise DatosInvalidos("El descuento en texto debe tener forma '10%'.", "descuento")
        return self._limitar_descuento(base * float(coincidencia.group(1)) / 100, base)

    @staticmethod
    def _limitar_descuento(valor, base):
        if valor > base * Tarifas.DESCUENTO_MAXIMO + 1e-9:
            raise DatosInvalidos(
                f"El descuento supera el máximo permitido ({Tarifas.DESCUENTO_MAXIMO:.0%}).",
                "descuento")
        return valor


class ReservaSala(Servicio):
    EXCLUSIVO = True

    def __init__(self, identificador, nombre=None, descripcion=None, precio_base=None,
                 tipo_sala=None, capacidad=None, duracion_horas=1, disponible=True):
        self._tipo_sala = requerir_opcion(tipo_sala, "tipo de sala", Tarifas.SALA_FACTOR_TIPO)
        self._capacidad = requerir_entero_positivo(
            capacidad, "capacidad", Tarifas.SALA_CAPACIDAD_MAXIMA[self._tipo_sala])
        super().__init__(identificador, nombre, descripcion, precio_base, duracion_horas, disponible)

    @property
    def tipo_sala(self):
        return self._tipo_sala

    @property
    def capacidad(self):
        return self._capacidad

    def validar_parametros(self, duracion):
        return requerir_numero_positivo(duracion, "duración (horas)", Tarifas.SALA_DURACION_MAXIMA)

    def calcular_costo_base(self, duracion=None):
        horas = self.resolver_duracion(duracion)
        return round(self._precio_base * Tarifas.SALA_FACTOR_TIPO[self._tipo_sala] * horas, 2)

    def describir(self):
        return (f"Sala {self._tipo_sala} '{self._nombre}' ({self.identificador}), capacidad "
                f"{self._capacidad}, tarifa/hora ${self._precio_base:,.0f}")


class AlquilerEquipo(Servicio):
    def __init__(self, identificador, nombre=None, descripcion=None, precio_base=None,
                 tipo_equipo=None, cantidad=None, duracion_horas=1, disponible=True):
        self._tipo_equipo = requerir_opcion(tipo_equipo, "tipo de equipo", Tarifas.EQUIPOS_PERMITIDOS)
        self._cantidad = requerir_entero_positivo(
            cantidad, "cantidad", Tarifas.EQUIPO_CANTIDAD_MAXIMA)
        super().__init__(identificador, nombre, descripcion, precio_base, duracion_horas, disponible)

    @property
    def tipo_equipo(self):
        return self._tipo_equipo

    @property
    def cantidad(self):
        return self._cantidad

    def validar_parametros(self, duracion):
        return requerir_numero_positivo(
            duracion, "tiempo de alquiler (horas)", Tarifas.EQUIPO_DURACION_MAXIMA)

    def calcular_costo_base(self, duracion=None):
        horas = self.resolver_duracion(duracion)
        return round(self._precio_base * self._cantidad * horas, 2)

    def describir(self):
        return (f"Alquiler de {self._cantidad} {self._tipo_equipo}(s) '{self._nombre}' "
                f"({self.identificador}), tarifa/hora/unidad ${self._precio_base:,.0f}")


class AsesoriaEspecializada(Servicio):
    EXCLUSIVO = True

    def __init__(self, identificador, nombre=None, descripcion=None, precio_base=None,
                 especialidad=None, asesor=None, modalidad=None, duracion_horas=1,
                 disponible=True):
        self._especialidad = requerir_texto(especialidad, "especialidad", 3, 60)
        self._asesor = requerir_texto(asesor, "asesor", 3, 60)
        self._modalidad = requerir_opcion(
            modalidad, "modalidad", Tarifas.ASESORIA_FACTOR_MODALIDAD)
        super().__init__(identificador, nombre, descripcion, precio_base, duracion_horas, disponible)

    @property
    def especialidad(self):
        return self._especialidad

    @property
    def asesor(self):
        return self._asesor

    @property
    def modalidad(self):
        return self._modalidad

    def validar_parametros(self, duracion):
        return requerir_numero_positivo(
            duracion, "duración (horas)", Tarifas.ASESORIA_DURACION_MAXIMA)

    def calcular_costo_base(self, duracion=None):
        horas = self.resolver_duracion(duracion)
        return round(self._precio_base * Tarifas.ASESORIA_FACTOR_MODALIDAD[self._modalidad] * horas, 2)

    def describir(self):
        return (f"Asesoría de {self._especialidad} '{self._nombre}' ({self.identificador}) con "
                f"{self._asesor}, modalidad {self._modalidad}, tarifa/hora ${self._precio_base:,.0f}")


# Registro de tipos: añadir un servicio nuevo no exige modificar SistemaGestion.
TIPOS_SERVICIO = {
    "sala": ReservaSala,
    "equipo": AlquilerEquipo,
    "asesoria": AsesoriaEspecializada,
}
