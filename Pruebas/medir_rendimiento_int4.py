"""Mide como crece cada operacion de R7-R9 con redes de 10.000 a 80.000 estaciones.

Uso:  python Pruebas/medir_rendimiento_int4.py [raiz_del_repo]
Pendiente ~0 = constante/logaritmico, ~1 = lineal (mismo metodo del profesor).
Esto es una herramienta de medicion: NO esta dentro de motor/.
"""
import math
import os
import random
import sys
import time

RAIZ = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from motor.operar import OperarRed  # noqa: E402

TAMANOS = [10000, 20000, 40000, 80000]
REPS = 15


class RedMedida(OperarRed):
    def __init__(self, n):
        azar = random.Random(7)
        self.estaciones = ["E%06d" % i for i in range(n)]
        self.cerradas = []
        self.rutas = []
        for r in range(n // 10):
            ids = azar.sample(range(n), 25)
            self.rutas.append(["R%05d" % r, [[k + 1, "E%06d" % ids[k]] for k in range(25)]])
        if hasattr(self, "_preparar_operaciones"):
            self._preparar_operaciones()


def mediana(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]


def medir(n):
    red = RedMedida(n)
    azar = random.Random(3)
    t = {k: [] for k in ["recorrido", "cerrar", "reabrir", "agregar_parada",
                         "quitar_parada", "deshacer", "rehacer"]}
    for _ in range(REPS):
        ruta = red.rutas[azar.randrange(len(red.rutas))]
        rid, paradas = ruta[0], ruta[1]
        a0 = time.perf_counter(); red.recorrido(rid); t["recorrido"].append(time.perf_counter() - a0)
        est = "E%06d" % azar.randrange(n)
        a0 = time.perf_counter(); red.cerrar(est); t["cerrar"].append(time.perf_counter() - a0)
        a0 = time.perf_counter(); red.reabrir(est); t["reabrir"].append(time.perf_counter() - a0)
        nueva = "E%06d" % azar.randrange(n)
        a0 = time.perf_counter()
        ok = red.agregar_parada(rid, nueva, paradas[3][1])
        t["agregar_parada"].append(time.perf_counter() - a0)
        if ok:
            a0 = time.perf_counter(); red.deshacer(); t["deshacer"].append(time.perf_counter() - a0)
            a0 = time.perf_counter(); red.rehacer(); t["rehacer"].append(time.perf_counter() - a0)
        a0 = time.perf_counter(); red.quitar_parada(rid, paradas[5][1]); t["quitar_parada"].append(time.perf_counter() - a0)
    return {k: mediana(v) for k, v in t.items() if len(v) > 0}


def main():
    res = [medir(n) for n in TAMANOS]
    print("%-16s" % "operacion" + "".join("%12d" % n for n in TAMANOS) + "   pendiente")
    for op in res[0]:
        pend = math.log(res[-1][op] / res[0][op]) / math.log(TAMANOS[-1] / TAMANOS[0])
        print("%-16s" % op + "".join("%10.1fus" % (r[op] * 1e6) for r in res) + "   %5.2f" % pend)


if __name__ == "__main__":
    main()
