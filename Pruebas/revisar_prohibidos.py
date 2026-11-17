"""Revisa que motor/ no use nada prohibido (para el rol de integracion).

Uso:  python Pruebas/revisar_prohibidos.py [carpeta_motor]
Heuristica sobre tokens (ignora comentarios y textos). Revisar a mano los avisos.
"""
import io
import os
import sys
import tokenize

PROHIBIDOS_NOMBRE = ["dict", "set", "sorted", "min", "max", "frozenset"]
PROHIBIDOS_METODO = ["sort", "index", "count"]
PROHIBIDOS_MODULO = ["heapq", "bisect", "collections", "functools", "numpy", "pandas"]


def revisar(ruta):
    avisos = []
    with open(ruta, encoding="utf-8") as f:
        fuente = f.read()
    tokens = list(tokenize.generate_tokens(io.StringIO(fuente).readline))
    linea_for = {}
    linea_in = {}
    for i, t in enumerate(tokens):
        if t.type == tokenize.NAME:
            sig = tokens[i + 1].string if i + 1 < len(tokens) else ""
            ant = tokens[i - 1].string if i > 0 else ""
            if t.string in PROHIBIDOS_NOMBRE and sig == "(":
                avisos.append((t.start[0], t.string + "()"))
            if t.string in PROHIBIDOS_METODO and ant == "." and sig == "(":
                avisos.append((t.start[0], "." + t.string + "()"))
            if t.string in PROHIBIDOS_MODULO:
                avisos.append((t.start[0], "modulo " + t.string))
            if t.string == "for":
                linea_for[t.start[0]] = linea_for.get(t.start[0], 0) + 1
            if t.string == "in":
                linea_in[t.start[0]] = linea_in.get(t.start[0], 0) + 1
        if t.type == tokenize.OP and t.string == "{":
            avisos.append((t.start[0], "literal {} (dict/set)"))
    for n, c in linea_in.items():
        if c > linea_for.get(n, 0):
            avisos.append((n, "'in' fuera de un for (membresia)"))
    return avisos


def main():
    carpeta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "motor")
    total = 0
    for nombre in os.listdir(carpeta):
        if nombre.endswith(".py"):
            for linea, que in revisar(os.path.join(carpeta, nombre)):
                print("%s:%d  %s" % (nombre, linea, que))
                total += 1
    print("Sin hallazgos." if total == 0 else "%d hallazgo(s)." % total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
