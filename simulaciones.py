"""Simulaciones de operaciones válidas e inválidas sobre SistemaGestion.

Los datos son ficticios. Un rechazo correcto (excepción esperada) es APROBADA.
"""
from dataclasses import dataclass
from datetime import date, timedelta

from excepciones import (ErrorCliente, ErrorReserva, ErrorServicio, OperacionNoPermitida,
                         ReservaNoEncontrada, ServicioNoDisponible)
from sistema_gestion import SistemaGestion


@dataclass
class ResultadoSimulacion:
    numero: int
    nombre: str
    datos: str
    esperado: str
    obtenido: str
    estado: str
    continuidad: str


def _verificar_costos(servicio):
    """Comprueba las cuatro variantes de cálculo con valores calculados a mano."""
    esperados = {
        "base": (servicio.calcular_costo(), 100000.0),
        "con impuestos": (servicio.calcular_costo_con_impuestos(), 119000.0),
        "con descuento 10%": (servicio.calcular_costo_con_descuento(descuento="10%"), 90000.0),
        "con descuento fijo $5000": (servicio.calcular_costo(descuento=5000), 95000.0),
        "impuestos y descuento": (servicio.calcular_costo(impuestos=True, descuento=0.10), 107100.0),
    }
    for variante, (obtenido, esperado) in esperados.items():
        if abs(obtenido - esperado) > 0.01:
            raise ErrorServicio(f"Costo '{variante}' incorrecto: {obtenido} != {esperado}")
    return {k: v[0] for k, v in esperados.items()}


def _operacion_defectuosa():
    """Simula un fallo no previsto (división por cero) para probar la red de seguridad."""
    return 1 / 0


def ejecutar_simulaciones(sistema=None, imprimir=True):
    sistema = sistema or SistemaGestion()
    resultados, ctx = [], {}
    hoy = date.today()

    def dia(n):
        return (hoy + timedelta(days=n)).isoformat()

    def simular(nombre, datos, esperado, operacion, guardar=None):
        antes = sistema.resumen()
        res = sistema.ejecutar_operacion(operacion)
        if esperado is None:
            cumple, texto_esperado = res.exito, "Operación exitosa"
            obtenido = f"Éxito: {res.valor}" if res.exito else f"Falló: {res.mensaje}"
            continuidad = "N/A (operación válida)"
            if res.exito and guardar:
                ctx[guardar] = res.valor
        else:
            cumple = (not res.exito) and isinstance(res.error, esperado)
            texto_esperado = f"Rechazo controlado: {esperado.__name__}"
            obtenido = (f"{type(res.error).__name__}: {res.mensaje}" if not res.exito
                        else "La operación NO fue rechazada")
            seguro = sistema.ejecutar_operacion(sistema.resumen)
            continuidad = ("OK (estado intacto y sistema operativo)"
                           if seguro.exito and sistema.resumen() == antes else "FALLÓ")
            cumple = cumple and continuidad.startswith("OK")
        resultados.append(ResultadoSimulacion(
            len(resultados) + 1, nombre, datos, texto_esperado, obtenido,
            "APROBADA" if cumple else "FALLIDA", continuidad))

    cli = dict(nombre="Ana María", apellido="Gómez", documento="1012345678",
               correo="ana.gomez@example.com", telefono="3001234567")
    sala = dict(nombre="Sala de reuniones Alfa", descripcion="Sala con TV y tablero",
                precio_base=50000, tipo_sala="reuniones", capacidad=10, duracion_horas=2)
    equipo = dict(nombre="Alquiler de portátiles", descripcion="Portátiles para capacitación",
                  precio_base=8000, tipo_equipo="portatil", cantidad=5, duracion_horas=4)
    asesoria = dict(nombre="Asesoría en arquitectura", descripcion="Revisión de arquitectura",
                    precio_base=90000, especialidad="Arquitectura de software",
                    asesor="Asesor de ejemplo", modalidad="virtual", duracion_horas=2)

    simular("Registro correcto de un cliente (Obligatoria 1)", str(cli), None,
            lambda: sistema.registrar_cliente(**cli), "cliente")
    simular("Registro con correo inválido (Obligatoria 2)", "correo='ana.gomez@@example'", ErrorCliente,
            lambda: sistema.registrar_cliente(**{**cli, "documento": "2000000001",
                                                  "correo": "ana.gomez@@example"}))
    simular("Registro con información incompleta (Obligatoria 3)", "sin documento ni teléfono",
            ErrorCliente, lambda: sistema.registrar_cliente(nombre="Luis", apellido="Pérez",
                                                            correo="luis@example.com"))
    simular("Registro de cliente duplicado (documento repetido)", "mismo documento que CLI-001",
            ErrorCliente, lambda: sistema.registrar_cliente(**{**cli, "correo": "otra@example.com"}))
    simular("Creación correcta de servicio ReservaSala", str(sala), None,
            lambda: sistema.crear_servicio("sala", **sala), "sala")
    simular("Creación correcta de una reserva de sala (Obligatoria 4)", f"CLI-001, SRV-001, {dia(7)}",
            None, lambda: sistema.crear_reserva(ctx["cliente"].identificador,
                                                ctx["sala"].identificador, dia(7)), "res_sala")
    simular("Creación incorrecta de un servicio (Obligatoria 5)",
            "tipo_sala='gigante', capacidad=0, precio=-100", ErrorServicio,
            lambda: sistema.crear_servicio("sala", **{**sala, "tipo_sala": "gigante",
                                                      "capacidad": 0, "precio_base": -100}))
    simular("Creación correcta de un alquiler de equipo (Obligatoria 6)", str(equipo), None,
            lambda: sistema.crear_servicio("equipo", **equipo), "equipo")
    simular("Creación correcta de una asesoría (Obligatoria 7)", str(asesoria), None,
            lambda: sistema.crear_servicio("asesoria", **asesoria), "asesoria")

    def reservar_y_confirmar():
        reserva = sistema.crear_reserva(ctx["cliente"].identificador,
                                        ctx["equipo"].identificador, dia(3), descuento="10%")
        return sistema.confirmar_reserva(reserva.identificador)

    simular("Creación y confirmación de una reserva válida (Obligatoria 8)",
            f"equipo SRV-002, {dia(3)}, descuento 10%", None, reservar_y_confirmar)
    simular("Creación de servicio marcado como no disponible", "tablet, disponible=False", None,
            lambda: sistema.crear_servicio("equipo", **{**equipo, "tipo_equipo": "tablet", "nombre": "Alquiler de tablets",
                                                         "disponible": False}), "no_disp")
    simular("Reserva de un servicio no disponible (Obligatoria 9)", "servicio no disponible",
            ServicioNoDisponible, lambda: sistema.crear_reserva(
                ctx["cliente"].identificador, ctx["no_disp"].identificador, dia(5)))
    simular("Cancelación de una reserva inexistente (Obligatoria 10)", "RES-999",
            ReservaNoEncontrada, lambda: sistema.cancelar_reserva("RES-999"))
    simular("Cancelación de una reserva válida", "reserva de sala", None,
            lambda: sistema.cancelar_reserva(ctx["res_sala"].identificador))
    simular("Confirmación de una reserva cancelada", "reserva ya cancelada", OperacionNoPermitida,
            lambda: sistema.confirmar_reserva(ctx["res_sala"].identificador))
    simular("Reserva válida de sala en una fecha libre", f"sala SRV-001, {dia(9)}", None,
            lambda: sistema.crear_reserva(ctx["cliente"].identificador,
                                          ctx["sala"].identificador, dia(9)))
    simular("Conflicto de fecha en recurso exclusivo",
            f"sala ya reservada el {dia(9)}", ServicioNoDisponible,
            lambda: sistema.crear_reserva(ctx["cliente"].identificador,
                                          ctx["sala"].identificador, dia(9)))
    simular("Reserva con fecha en el pasado", "fecha de ayer", ErrorReserva,
            lambda: sistema.crear_reserva(ctx["cliente"].identificador,
                                          ctx["equipo"].identificador, dia(-1)))
    simular("Variantes de cálculo de costos (base, IVA, descuentos)",
            "sala 50000/h, 2 h, reuniones", None, lambda: _verificar_costos(ctx["sala"]))
    simular("Error inesperado capturado sin detener la aplicación", "1/0 deliberado",
            ZeroDivisionError, _operacion_defectuosa)
    simular("Reserva válida posterior a los errores (continuidad)", f"asesoría, {dia(12)}", None,
            lambda: sistema.crear_reserva(ctx["cliente"].identificador,
                                          ctx["asesoria"].identificador, dia(12)))
    if imprimir:
        imprimir_resultados(resultados)
    return resultados


def imprimir_resultados(resultados):
    print("=" * 78)
    print("SIMULACIONES - SOFTWARE FJ")
    print("=" * 78)
    for r in resultados:
        print(f"[Prueba {r.numero:02d}] {r.nombre}")
        print(f"   Datos:      {r.datos}")
        print(f"   Esperado:   {r.esperado}")
        print(f"   Obtenido:   {r.obtenido}")
        print(f"   Continuidad:{' ' + r.continuidad}")
        print(f"   Estado:     {r.estado}")
        print("-" * 78)
    aprobadas = sum(r.estado == "APROBADA" for r in resultados)
    print(f"RESUMEN: {aprobadas}/{len(resultados)} simulaciones APROBADAS")
