"""
Pruebas de Integrante 2: R4 (proximo_bus) y R6 (ranking).

Ejecutar desde la raiz del repositorio:
    python -m unittest Pruebas.test_p2 -v

- Las clases TestR4 y TestR6 prueban los indices SOLOS (no necesitan Red).
- TestIntegracion usa la Red definitiva con Datos/ (se salta si aun no existe).
"""

import unittest

from motor.horarios import (IndiceHorarios, ordenar_por, hora_a_minutos,
                            OK, HORA_INVALIDA, ESTACION_CERRADA,
                            RUTA_INEXISTENTE, ESTACION_NO_EN_RUTA, SIN_HORARIOS)
from motor.ranking import IndiceRanking

# Red pequena: A -> B -> C (ruta R1), C -> D -> E (ruta R2), R3 sin horarios.
ESTACIONES = ["A", "B", "C", "D", "E", "F"]
RUTAS = [
    ["R1", [[1, "A"], [2, "B"], [3, "C"]]],
    ["R2", [[1, "C"], [2, "D"], [3, "E"]]],
    ["R3", [[1, "E"], [2, "F"]]],
]
FILAS = [
    # R1 pasa 3 veces; las horas vienen desordenadas a proposito
    ["R1", "A", "08:00"], ["R1", "B", "08:05"], ["R1", "C", "08:10"],
    ["R1", "A", "06:00"], ["R1", "B", "06:05"], ["R1", "C", "06:10"],
    ["R1", "A", "22:00"], ["R1", "B", "22:05"], ["R1", "C", "22:10"],
    # R2 pasa 2 veces; una hora estilo GTFS 25:10 -> 01:10
    ["R2", "C", "07:00"], ["R2", "D", "07:10"], ["R2", "E", "07:20"],
    ["R2", "C", "25:10"], ["R2", "D", "25:20"], ["R2", "E", "25:30"],
]


class TestUtilidades(unittest.TestCase):
    def test_merge_sort(self):
        self.assertEqual(ordenar_por([5, 1, 4, 1, 3]), [1, 1, 3, 4, 5])
        self.assertEqual(ordenar_por([]), [])
        datos = [[2, "x"], [1, "y"], [2, "a"]]
        self.assertEqual(ordenar_por(datos, lambda a, b: a[0] < b[0]),
                         [[1, "y"], [2, "x"], [2, "a"]])   # estable

    def test_horas(self):
        self.assertEqual(hora_a_minutos("10:00"), 600)
        self.assertEqual(hora_a_minutos("25:10"), 70)
        self.assertEqual(hora_a_minutos("10:75"), -1)
        self.assertEqual(hora_a_minutos("abc"), -1)
        self.assertEqual(hora_a_minutos(None), -1)


class TestR4(unittest.TestCase):
    def setUp(self):
        self.h = IndiceHorarios(filas=FILAS)

    def p(self, est, ruta, hora, cerradas=None):
        return self.h.proximo(est, ruta, hora, RUTAS, cerradas or [])

    def test_siguiente_normal(self):
        self.assertEqual(self.p("A", "R1", "07:00"), "08:00")
        self.assertEqual(self.p("B", "R1", "06:06"), "08:05")

    def test_hora_exacta_cuenta(self):
        self.assertEqual(self.p("A", "R1", "08:00"), "08:00")

    def test_despues_del_ultimo_envuelve(self):
        self.assertEqual(self.p("A", "R1", "23:30"), "06:00")
        self.assertEqual(self.h.consultar("A", "R1", "23:30", RUTAS, []),
                         [OK, "06:00", True])

    def test_gtfs_mayor_24(self):
        self.assertEqual(self.p("C", "R2", "00:30"), "01:10")

    def test_casos_none(self):
        c = self.h.consultar
        self.assertEqual(c("A", "R9", "08:00", RUTAS, [])[0], RUTA_INEXISTENTE)
        self.assertEqual(c("D", "R1", "08:00", RUTAS, [])[0], ESTACION_NO_EN_RUTA)
        self.assertEqual(c("ZZZ", "R1", "08:00", RUTAS, [])[0], ESTACION_NO_EN_RUTA)
        self.assertEqual(c("E", "R3", "08:00", RUTAS, [])[0], SIN_HORARIOS)
        self.assertEqual(c("A", "R1", "8h", RUTAS, [])[0], HORA_INVALIDA)
        self.assertEqual(c("A", "R1", "08:00", RUTAS, ["A"])[0], ESTACION_CERRADA)
        self.assertIsNone(self.p("A", "R1", "08:00", ["A"]))

    def test_r7_quitar_parada(self):
        rutas = [["R1", [[1, "A"], [3, "C"]]], RUTAS[1], RUTAS[2]]   # sin B
        self.h.invalidar()
        self.assertIsNone(self.h.proximo("B", "R1", "07:00", rutas, []))
        self.h.invalidar()
        self.assertEqual(self.h.proximo("B", "R1", "07:00", RUTAS, []), "08:05")


class TestR6(unittest.TestCase):
    def setUp(self):
        self.r = IndiceRanking(IndiceHorarios(filas=FILAS))

    def test_ranking_basico_y_empates(self):
        # C: 3 (R1) + 2 (R2) = 5.  A, B: 3.  D, E: 2.  F: 0.
        self.assertEqual(self.r.top_con_conteo(10, ESTACIONES, RUTAS, []),
                         [["C", 5], ["A", 3], ["B", 3], ["D", 2], ["E", 2], ["F", 0]])
        self.assertEqual(self.r.top(2, ESTACIONES, RUTAS, []), ["C", "A"])

    def test_k_borde(self):
        self.assertEqual(self.r.top(0, ESTACIONES, RUTAS, []), [])
        self.assertEqual(self.r.top(-3, ESTACIONES, RUTAS, []), [])
        self.assertEqual(len(self.r.top(100, ESTACIONES, RUTAS, [])), 6)

    def test_cerrar_y_reabrir(self):
        cerradas = ["C"]
        self.r.invalidar_cierres()
        self.assertEqual(self.r.top(2, ESTACIONES, RUTAS, cerradas), ["A", "B"])
        cerradas = []
        self.r.invalidar_cierres()
        self.assertEqual(self.r.top(1, ESTACIONES, RUTAS, cerradas), ["C"])

    def test_r7_agregar_hereda(self):
        rutas = [["R1", [[1, "A"], [2, "B"], [3, "F"], [4, "C"]]], RUTAS[1], RUTAS[2]]
        self.r.invalidar()
        # F hereda 3 buses de B en R1.
        self.assertEqual(self.r.top_con_conteo(10, ESTACIONES, rutas, [])[3], ["F", 3])

    def test_r7_quitar(self):
        rutas = [["R1", [[1, "A"], [2, "B"]]], RUTAS[1], RUTAS[2]]   # sin C en R1
        self.r.invalidar()
        self.assertEqual(self.r.top_con_conteo(1, ESTACIONES, rutas, []), [["A", 3]])


class TestIntegracion(unittest.TestCase):
    """Usa la Red definitiva del equipo con los datos reales."""

    @classmethod
    def setUpClass(cls):
        try:
            from motor import Red
            cls.red = Red("Datos")
        except Exception as e:      # Red aun no lista o faltan datos
            raise unittest.SkipTest("Red no disponible: %s" % e)

    def test_ejemplo_enunciado(self):
        self.assertEqual(self.red.proximo_bus("UNIVERSIDADES", "1-1", "10:00"), "10:08")

    def test_ultimo_bus_envuelve(self):
        self.assertEqual(self.red.proximo_bus("UNIVERSIDADES", "1-1", "23:30"), "09:57")

    def test_inexistentes(self):
        self.assertIsNone(self.red.proximo_bus("UNIVERSIDADES", "NO-EXISTE", "10:00"))
        self.assertIsNone(self.red.proximo_bus("NO EXISTE", "1-1", "10:00"))

    def test_integracion_con_red(self):
        red = self.red
        primero = red.ranking(1)[0]
        self.assertEqual(primero, "RICAURTE")
        red.cerrar(primero)
        self.assertNotEqual(red.ranking(1)[0], primero)
        self.assertIsNone(red.proximo_bus(primero, "4-3", "10:00"))
        red.reabrir(primero)
        self.assertEqual(red.ranking(1)[0], primero)

        # R7: quitar RICAURTE de varias rutas lo debe bajar del primer lugar.
        antes = red._ranking.top_con_conteo(1, red.estaciones, red.rutas, red.cerradas)[0][1]
        red.quitar_parada("4-3", "RICAURTE")
        despues = red._ranking.top_con_conteo(1, red.estaciones, red.rutas, red.cerradas)
        self.assertLess(despues[0][1] if despues[0][0] == "RICAURTE" else 0, antes)
        self.assertIsNone(red.proximo_bus("RICAURTE", "4-3", "10:00"))
        red.deshacer()
        self.assertIsNotNone(red.proximo_bus("RICAURTE", "4-3", "10:00"))
        self.assertEqual(red.ranking(1)[0], "RICAURTE")


if __name__ == "__main__":
    unittest.main()
