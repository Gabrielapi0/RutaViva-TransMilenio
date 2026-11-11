"""Red minima SOLO para probar R7-R9 sin depender de la clase Red real.

Carga los CSV (estaciones.csv y rutas.csv) con el modulo csv, igual que el
formato del contrato: estaciones, rutas, cerradas.
"""
import csv
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from motor.operar import OperarRed  # noqa: E402


class RedPrueba(OperarRed):
    def __init__(self, estaciones=None, rutas=None, cerradas=None):
        self.estaciones = estaciones if estaciones is not None else []
        self.rutas = rutas if rutas is not None else []
        self.cerradas = cerradas if cerradas is not None else []

    @classmethod
    def desde_csv(cls, carpeta):
        red = cls()
        with open(os.path.join(carpeta, "estaciones.csv"), encoding="utf-8-sig") as f:
            for fila in csv.DictReader(f):
                red.estaciones.append(fila["nombre"])
        with open(os.path.join(carpeta, "rutas.csv"), encoding="utf-8-sig") as f:
            for fila in csv.DictReader(f):
                if len(red.rutas) == 0 or red.rutas[-1][0] != fila["ruta"]:
                    red.rutas.append([fila["ruta"], []])
                red.rutas[-1][1].append([int(fila["orden"]), fila["estacion"]])
        return red


def red_mini():
    """ALFA-BETA-GAMMA (RUTA_A) y GAMMA-DELTA-EPSILON (RUTA_B)."""
    return RedPrueba(
        ["ALFA", "BETA", "GAMMA", "DELTA", "EPSILON", "ZETA"],
        [["RUTA_A", [[1, "ALFA"], [2, "BETA"], [3, "GAMMA"]]],
         ["RUTA_B", [[1, "GAMMA"], [2, "DELTA"], [3, "EPSILON"]]]])


def nombres(red, ruta):
    return red.recorrido(ruta)
