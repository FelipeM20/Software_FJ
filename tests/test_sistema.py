"""Pruebas unitarias y de integración de Software FJ (unittest, sin dependencias)."""
import os
import sys
import tempfile
import unittest
from abc import ABC
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clientes import Cliente, EstadoCliente  # noqa: E402
from configuracion_logging import ARCHIVO_LOG, cerrar_logging, configurar_logging  # noqa: E402
from entidades import Entidad  # noqa: E402
from excepciones import (DatosInvalidos, ErrorCliente, ErrorReserva, ErrorServicio,  # noqa: E402
                         ErrorSoftwareFJ, OperacionNoPermitida, ReservaNoEncontrada,
                         ServicioNoDisponible)
from reservas import EstadoReserva, Reserva  # noqa: E402
from servicios import (AlquilerEquipo, AsesoriaEspecializada, ReservaSala,  # noqa: E402
                       Servicio)
from simulaciones import ejecutar_simulaciones  # noqa: E402
from sistema_gestion import SistemaGestion  # noqa: E402

CLI = dict(nombre="Ana", apellido="Gómez", documento="1012345678",
           correo="ana@example.com", telefono="3001234567")
SALA = dict(nombre="Sala Alfa", descripcion="Sala de prueba", precio_base=50000,
            tipo_sala="reuniones", capacidad=10, duracion_horas=2)
EQUIPO = dict(nombre="Portátiles", descripcion="Equipos de prueba", precio_base=8000,
              tipo_equipo="portatil", cantidad=5, duracion_horas=4)
ASESORIA = dict(nombre="Asesoría", descripcion="Asesoría de prueba", precio_base=90000,
                especialidad="Arquitectura", asesor="Asesor Uno", modalidad="virtual",
                duracion_horas=2)


def dia(n):
    return (date.today() + timedelta(days=n)).isoformat()


class BaseConLog(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.carpeta = os.path.join(tmp.name, "logs")
        configurar_logging(self.carpeta)
        self.addCleanup(cerrar_logging)  # se ejecuta antes que tmp.cleanup (LIFO)
        self.sistema = SistemaGestion()

    def leer_log(self):
        with open(os.path.join(self.carpeta, ARCHIVO_LOG), encoding="utf-8") as f:
            return f.read()

    def preparar(self):
        c = self.sistema.registrar_cliente(**CLI)
        s = self.sistema.crear_servicio("sala", **SALA)
        return c, s


class TestAbstraccion(unittest.TestCase):
    def test_clases_abstractas_no_se_instancian(self):
        for clase in (Entidad, Servicio):
            with self.assertRaises(TypeError):
                clase("SRV-001")

    def test_herencia(self):
        self.assertTrue(issubclass(Cliente, Entidad))
        for clase in (ReservaSala, AlquilerEquipo, AsesoriaEspecializada):
            self.assertTrue(issubclass(clase, Servicio))
        self.assertTrue(issubclass(Servicio, Entidad) and issubclass(Entidad, ABC))

    def test_subclase_incompleta_no_se_instancia(self):
        class Incompleta(Servicio):
            pass
        with self.assertRaises(TypeError):
            Incompleta("SRV-001")


class TestCliente(unittest.TestCase):
    def test_creacion_valida_y_normalizacion(self):
        c = Cliente("CLI-001", "  Ana  ", "Gómez", 1012345678, "ANA@Example.com", "300 123 4567")
        self.assertEqual(c.nombre, "Ana")
        self.assertEqual(c.correo, "ana@example.com")
        self.assertEqual(c.estado, EstadoCliente.ACTIVO)

    def test_correos_invalidos(self):
        for correo in ("sin_arroba", "a@@b.com", "a@b", "a b@c.com", "a@b..com", "", None, 5):
            with self.subTest(correo=correo), self.assertRaises(DatosInvalidos):
                Cliente("CLI-001", **{**CLI, "correo": correo})

    def test_datos_faltantes_o_incorrectos(self):
        for campo in CLI:
            with self.subTest(campo=campo), self.assertRaises(DatosInvalidos):
                Cliente("CLI-001", **{**CLI, campo: None})
        for campo, valor in (("documento", "12ab5"), ("telefono", "123"), ("nombre", "A")):
            with self.subTest(campo=campo), self.assertRaises(DatosInvalidos):
                Cliente("CLI-001", **{**CLI, campo: valor})

    def test_identificador_invalido(self):
        for ident in ("001", "cli-001", "SRV-001", None, "CLI-1"):
            with self.subTest(ident=ident), self.assertRaises(DatosInvalidos):
                Cliente(ident, **CLI)

    def test_encapsulacion_y_actualizacion_atomica(self):
        c = Cliente("CLI-001", **CLI)
        with self.assertRaises(AttributeError):
            c.documento = "999999999"
        with self.assertRaises(DatosInvalidos):
            c.actualizar(nombre="Beatriz", correo="malo")
        self.assertEqual(c.nombre, "Ana")  # nada se aplicó
        c.actualizar(nombre="Beatriz", telefono="3109998888")
        self.assertEqual((c.nombre, c.telefono), ("Beatriz", "3109998888"))
        with self.assertRaises(DatosInvalidos):
            c.actualizar(documento="1")
        self.assertTrue(c.consultar()["documento"].startswith("*"))

    def test_estado(self):
        c = Cliente("CLI-001", **CLI)
        c.desactivar()
        self.assertEqual(c.estado, EstadoCliente.INACTIVO)
        c.activar()
        self.assertEqual(c.estado, EstadoCliente.ACTIVO)


class TestServicios(unittest.TestCase):
    def setUp(self):
        self.sala = ReservaSala("SRV-001", **SALA)
        self.equipo = AlquilerEquipo("SRV-002", **EQUIPO)
        self.asesoria = AsesoriaEspecializada("SRV-003", **ASESORIA)

    def test_cuatro_variantes_de_calculo(self):
        self.assertAlmostEqual(self.sala.calcular_costo(), 100000)
        self.assertAlmostEqual(self.sala.calcular_costo(impuestos=True), 119000)
        self.assertAlmostEqual(self.sala.calcular_costo(descuento="10%"), 90000)
        self.assertAlmostEqual(self.sala.calcular_costo(impuestos=True, descuento=0.10), 107100)
        self.assertAlmostEqual(self.sala.calcular_costo_con_impuestos(), 119000)
        self.assertAlmostEqual(self.sala.calcular_costo_con_descuento(descuento=5000), 95000)
        self.assertAlmostEqual(self.sala.calcular_costo(3), 150000)  # duración explícita

    def test_descuentos_por_tipo_y_errores(self):
        self.assertAlmostEqual(self.sala.calcular_costo(descuento=0.3), 70000)
        for malo in (0.31, "31%", 40000, -1, "abc", True, 1.5, [1], float("nan")):
            with self.subTest(descuento=malo), self.assertRaises(DatosInvalidos):
                self.sala.calcular_costo(descuento=malo)

    def test_polimorfismo(self):
        costos = [s.calcular_costo_base() for s in (self.sala, self.equipo, self.asesoria)]
        self.assertEqual(costos, [100000.0, 160000.0, 180000.0])
        textos = [s.describir() for s in (self.sala, self.equipo, self.asesoria)]
        self.assertTrue(textos[0].startswith("Sala") and textos[1].startswith("Alquiler")
                        and textos[2].startswith("Asesoría"))
        presencial = AsesoriaEspecializada("SRV-004", **{**ASESORIA, "modalidad": "presencial"})
        self.assertAlmostEqual(presencial.calcular_costo_base(), 225000)

    def test_parametros_invalidos(self):
        casos = [(ReservaSala, {**SALA, "tipo_sala": "gigante"}),
                 (ReservaSala, {**SALA, "capacidad": 13}),
                 (ReservaSala, {**SALA, "duracion_horas": 13}),
                 (ReservaSala, {**SALA, "precio_base": -1}),
                 (ReservaSala, {**SALA, "precio_base": "caro"}),
                 (ReservaSala, {**SALA, "disponible": "si"}),
                 (AlquilerEquipo, {**EQUIPO, "cantidad": 0}),
                 (AlquilerEquipo, {**EQUIPO, "tipo_equipo": "nave"}),
                 (AsesoriaEspecializada, {**ASESORIA, "modalidad": "mixta"}),
                 (AsesoriaEspecializada, {**ASESORIA, "asesor": None})]
        for clase, datos in casos:
            with self.subTest(clase=clase.__name__, datos=datos), self.assertRaises(DatosInvalidos):
                clase("SRV-009", **datos)

    def test_disponibilidad(self):
        self.sala.disponible = False
        with self.assertRaises(ServicioNoDisponible):
            self.sala.validar_disponibilidad()
        with self.assertRaises(DatosInvalidos):
            self.sala.disponible = "no"


class TestReserva(unittest.TestCase):
    def setUp(self):
        self.cliente = Cliente("CLI-001", **CLI)
        self.servicio = ReservaSala("SRV-001", **SALA)

    def nueva(self, **kw):
        datos = dict(cliente=self.cliente, servicio=self.servicio, fecha=dia(2))
        datos.update(kw)
        return Reserva("RES-001", **datos)

    def test_creacion_y_costo(self):
        r = self.nueva(descuento="10%")
        self.assertEqual(r.estado, EstadoReserva.PENDIENTE)
        self.assertAlmostEqual(r.costo_total, 107100)
        self.assertAlmostEqual(self.nueva(aplicar_impuestos=False).costo_total, 100000)

    def test_transiciones_validas_e_invalidas(self):
        r = self.nueva()
        r.confirmar()
        self.assertEqual(r.estado, EstadoReserva.CONFIRMADA)
        with self.assertRaises(OperacionNoPermitida):
            r.confirmar()
        r.cancelar()
        with self.assertRaises(OperacionNoPermitida):
            r.confirmar()
        with self.assertRaises(OperacionNoPermitida):
            r.cancelar()

    def test_procesar(self):
        r = self.nueva()
        r.procesar("confirmar")
        self.assertEqual(r.estado, EstadoReserva.CONFIRMADA)
        with self.assertRaises(OperacionNoPermitida) as ctx:
            r.procesar("borrar")
        self.assertIsInstance(ctx.exception.__cause__, KeyError)

    def test_validaciones(self):
        with self.assertRaises(DatosInvalidos):
            self.nueva(cliente="Ana")
        with self.assertRaises(DatosInvalidos):
            self.nueva(servicio=None)
        with self.assertRaises(DatosInvalidos):
            self.nueva(fecha=dia(-1))
        with self.assertRaises(DatosInvalidos):
            self.nueva(fecha=None)
        with self.assertRaises(DatosInvalidos):
            self.nueva(duracion_horas=99)
        self.cliente.desactivar()
        with self.assertRaises(OperacionNoPermitida):
            self.nueva()
        self.cliente.activar()
        self.servicio.disponible = False
        with self.assertRaises(ServicioNoDisponible):
            self.nueva()

    def test_fecha_invalida_encadena_valueerror(self):
        with self.assertRaises(DatosInvalidos) as ctx:
            self.nueva(fecha="31/12/2030")
        self.assertIsInstance(ctx.exception.__cause__, ValueError)


class TestExcepciones(unittest.TestCase):
    def test_jerarquia(self):
        for clase in (ErrorCliente, ErrorServicio, ErrorReserva, DatosInvalidos,
                      ServicioNoDisponible, ReservaNoEncontrada, OperacionNoPermitida):
            self.assertTrue(issubclass(clase, ErrorSoftwareFJ))
            self.assertTrue(issubclass(clase, Exception))
        self.assertTrue(issubclass(ServicioNoDisponible, ErrorServicio))
        self.assertTrue(issubclass(ReservaNoEncontrada, ErrorReserva))
        self.assertEqual(DatosInvalidos("x", "campo").campo, "campo")


class TestSistema(BaseConLog):
    def test_registro_y_consulta_de_clientes(self):
        c = self.sistema.registrar_cliente(**CLI)
        self.assertIs(self.sistema.consultar_cliente(c.identificador), c)
        self.assertEqual(len(self.sistema.listar_clientes()), 1)
        with self.assertRaises(ErrorCliente):
            self.sistema.consultar_cliente("CLI-099")

    def test_duplicados_y_encadenamiento(self):
        self.sistema.registrar_cliente(**CLI)
        with self.assertRaises(ErrorCliente):
            self.sistema.registrar_cliente(**{**CLI, "correo": "otro@example.com"})
        with self.assertRaises(ErrorCliente):
            self.sistema.registrar_cliente(**{**CLI, "documento": "2000000001"})
        with self.assertRaises(ErrorCliente) as ctx:
            self.sistema.registrar_cliente(**{**CLI, "documento": "2000000001", "correo": "x@@y"})
        self.assertIsInstance(ctx.exception.__cause__, DatosInvalidos)
        self.assertEqual(len(self.sistema.listar_clientes()), 1)

    def test_datos_incompletos(self):
        with self.assertRaises(ErrorCliente):
            self.sistema.registrar_cliente(nombre="Luis")

    def test_ids_no_se_consumen_en_fallos(self):
        with self.assertRaises(ErrorCliente):
            self.sistema.registrar_cliente(nombre="Luis")
        self.assertEqual(self.sistema.registrar_cliente(**CLI).identificador, "CLI-001")

    def test_crear_servicios(self):
        for tipo, datos in (("sala", SALA), ("equipo", EQUIPO), ("asesoria", ASESORIA)):
            self.sistema.crear_servicio(tipo, **datos)
        self.assertEqual(len(self.sistema.listar_servicios()), 3)
        with self.assertRaises(ErrorServicio) as ctx:
            self.sistema.crear_servicio("sala", **{**SALA, "capacidad": 0})
        self.assertIsInstance(ctx.exception.__cause__, DatosInvalidos)
        with self.assertRaises(ErrorServicio) as ctx:
            self.sistema.crear_servicio("sala", **SALA, extra=1)
        self.assertIsInstance(ctx.exception.__cause__, TypeError)
        for tipo in ("hotel", None, 3):
            with self.assertRaises(ErrorServicio):
                self.sistema.crear_servicio(tipo, **SALA)
        self.assertEqual(len(self.sistema.listar_servicios()), 3)

    def test_flujo_completo_de_reserva(self):
        c, s = self.preparar()
        r = self.sistema.crear_reserva(c.identificador, s.identificador, dia(3), descuento=0.1)
        self.sistema.confirmar_reserva(r.identificador)
        self.assertEqual(self.sistema.resumen()["reservas_por_estado"]["confirmada"], 1)
        self.assertAlmostEqual(self.sistema.resumen()["ingresos_confirmados"], r.costo_total)
        self.sistema.cancelar_reserva(r.identificador)
        with self.assertRaises(OperacionNoPermitida):
            self.sistema.confirmar_reserva(r.identificador)
        self.assertIn("RES-001", self.sistema.mostrar_informacion_general())

    def test_reserva_inexistente_y_ids_invalidos(self):
        with self.assertRaises(ReservaNoEncontrada):
            self.sistema.cancelar_reserva("RES-999")
        c, s = self.preparar()
        with self.assertRaises(ErrorCliente):
            self.sistema.crear_reserva("CLI-999", s.identificador, dia(1))
        with self.assertRaises(ErrorServicio):
            self.sistema.crear_reserva(c.identificador, "SRV-999", dia(1))

    def test_disponibilidad_y_conflictos(self):
        c, s = self.preparar()
        self.assertTrue(self.sistema.validar_disponibilidad(s.identificador, dia(4)))
        r = self.sistema.crear_reserva(c.identificador, s.identificador, dia(4))
        with self.assertRaises(ServicioNoDisponible):
            self.sistema.crear_reserva(c.identificador, s.identificador, dia(4))
        with self.assertRaises(ServicioNoDisponible):
            self.sistema.validar_disponibilidad(s.identificador, dia(4))
        self.sistema.cancelar_reserva(r.identificador)  # al cancelar, la fecha se libera
        self.sistema.crear_reserva(c.identificador, s.identificador, dia(4))
        with self.assertRaises(ErrorReserva):
            self.sistema.validar_disponibilidad(s.identificador, "no-es-fecha")
        s.disponible = False
        with self.assertRaises(ServicioNoDisponible):
            self.sistema.crear_reserva(c.identificador, s.identificador, dia(6))
        self.assertEqual(len(self.sistema.listar_servicios(solo_disponibles=True)), 0)

    def test_equipo_no_es_exclusivo(self):
        c = self.sistema.registrar_cliente(**CLI)
        e = self.sistema.crear_servicio("equipo", **EQUIPO)
        self.sistema.crear_reserva(c.identificador, e.identificador, dia(2))
        self.sistema.crear_reserva(c.identificador, e.identificador, dia(2))
        self.assertEqual(len(self.sistema.listar_reservas()), 2)

    def test_reserva_invalida_encadena_error(self):
        c, s = self.preparar()
        with self.assertRaises(ErrorReserva) as ctx:
            self.sistema.crear_reserva(c.identificador, s.identificador, dia(-3))
        self.assertIsInstance(ctx.exception.__cause__, DatosInvalidos)

    def test_ejecutar_operacion_controla_errores(self):
        ok = self.sistema.ejecutar_operacion(self.sistema.resumen)
        self.assertTrue(ok.exito)
        propio = self.sistema.ejecutar_operacion(self.sistema.cancelar_reserva, "RES-404")
        self.assertFalse(propio.exito)
        self.assertIsInstance(propio.error, ReservaNoEncontrada)
        inesperado = self.sistema.ejecutar_operacion(lambda: 1 / 0)
        self.assertFalse(inesperado.exito)
        self.assertIsInstance(inesperado.error, ZeroDivisionError)

    def test_continuidad_tras_errores(self):
        for _ in range(3):
            self.sistema.ejecutar_operacion(self.sistema.registrar_cliente, nombre="X")
            self.sistema.ejecutar_operacion(lambda: 1 / 0)
        res = self.sistema.ejecutar_operacion(self.sistema.registrar_cliente, **CLI)
        self.assertTrue(res.exito)
        self.assertEqual(self.sistema.resumen()["clientes"], 1)

    def test_listas_devueltas_son_copias(self):
        self.sistema.registrar_cliente(**CLI)
        self.assertIsInstance(self.sistema.listar_clientes(), tuple)


class TestLogging(BaseConLog):
    def test_archivo_y_niveles(self):
        self.assertTrue(os.path.isfile(os.path.join(self.carpeta, ARCHIVO_LOG)))
        self.preparar()
        with self.assertRaises(ErrorCliente):
            self.sistema.registrar_cliente(nombre="X")
        self.sistema.ejecutar_operacion(lambda: 1 / 0)
        log = self.leer_log()
        for nivel in ("DEBUG", "INFO", "WARNING", "ERROR"):
            self.assertIn(f"| {nivel}", log)
        self.assertIn("Traceback", log)  # logger.exception
        self.assertIn("Cliente registrado: CLI-001", log)
        self.assertRegex(log, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    def test_no_registra_datos_personales(self):
        self.sistema.registrar_cliente(**CLI)
        with self.assertRaises(ErrorCliente):
            self.sistema.registrar_cliente(**{**CLI, "correo": "malo@@x"})
        log = self.leer_log()
        for dato in (CLI["documento"], CLI["correo"], CLI["telefono"], "malo@@x"):
            self.assertNotIn(dato, log)

    def test_configurar_dos_veces_no_duplica(self):
        configurar_logging(self.carpeta)
        self.sistema.registrar_cliente(**CLI)
        self.assertEqual(self.leer_log().count("Cliente registrado: CLI-001"), 1)


class TestSimulaciones(BaseConLog):
    def test_diez_o_mas_simulaciones_aprobadas(self):
        resultados = ejecutar_simulaciones(self.sistema, imprimir=False)
        self.assertGreaterEqual(len(resultados), 10)
        fallidas = [r for r in resultados if r.estado != "APROBADA"]
        self.assertEqual(fallidas, [], fallidas)
        nombres = " ".join(r.nombre for r in resultados)
        for n in range(1, 11):
            self.assertIn(f"Obligatoria {n})", nombres)
        self.assertIn("ERROR", self.leer_log())


if __name__ == "__main__":
    unittest.main(verbosity=2)
