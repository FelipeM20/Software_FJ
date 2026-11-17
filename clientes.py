"""Clase Cliente con datos encapsulados y validación estricta."""
from enum import Enum

from entidades import Entidad
from excepciones import DatosInvalidos
from validaciones import (requerir_texto, validar_correo, validar_documento,
                          validar_telefono)


class EstadoCliente(Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"


# Validador por campo: una sola fuente de verdad para constructor, setters y actualizar().
_VALIDADORES = {
    "nombre": lambda v: requerir_texto(v, "nombre", 2, 50),
    "apellido": lambda v: requerir_texto(v, "apellido", 2, 50),
    "correo": validar_correo,
    "telefono": validar_telefono,
}


class Cliente(Entidad):
    PREFIJO = "CLI"

    def __init__(self, identificador, nombre=None, apellido=None, documento=None,
                 correo=None, telefono=None):
        super().__init__(identificador)
        self._nombre = _VALIDADORES["nombre"](nombre)
        self._apellido = _VALIDADORES["apellido"](apellido)
        self._documento = validar_documento(documento)
        self._correo = _VALIDADORES["correo"](correo)
        self._telefono = _VALIDADORES["telefono"](telefono)
        self._estado = EstadoCliente.ACTIVO

    # --- propiedades (el documento es de solo lectura: identifica a la persona) ---
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = _VALIDADORES["nombre"](valor)

    @property
    def apellido(self):
        return self._apellido

    @apellido.setter
    def apellido(self, valor):
        self._apellido = _VALIDADORES["apellido"](valor)

    @property
    def documento(self):
        return self._documento

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        self._correo = _VALIDADORES["correo"](valor)

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = _VALIDADORES["telefono"](valor)

    @property
    def estado(self):
        return self._estado

    @property
    def nombre_completo(self):
        return f"{self._nombre} {self._apellido}"

    # --- comportamiento ---
    def actualizar(self, **cambios):
        """Actualiza datos de forma atómica: si un dato es inválido no se aplica ninguno."""
        desconocidos = set(cambios) - set(_VALIDADORES)
        if desconocidos:
            raise DatosInvalidos(
                f"Campos no actualizables: {', '.join(sorted(desconocidos))}.")
        if not cambios:
            raise DatosInvalidos("No se indicó ningún dato para actualizar.")
        validados = {campo: _VALIDADORES[campo](valor) for campo, valor in cambios.items()}
        for campo, valor in validados.items():
            setattr(self, f"_{campo}", valor)

    def activar(self):
        self._estado = EstadoCliente.ACTIVO

    def desactivar(self):
        self._estado = EstadoCliente.INACTIVO

    def consultar(self):
        """Datos del cliente; el documento se muestra enmascarado."""
        return {
            "identificador": self.identificador,
            "nombre": self.nombre_completo,
            "documento": "*" * (len(self._documento) - 3) + self._documento[-3:],
            "correo": self._correo,
            "telefono": self._telefono,
            "estado": self._estado.value,
        }

    def describir(self):
        return f"Cliente {self.identificador}: {self.nombre_completo} ({self._estado.value})"

    def validar(self):
        for campo, validador in _VALIDADORES.items():
            validador(getattr(self, f"_{campo}"))
        validar_documento(self._documento)
