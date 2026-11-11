"""
R11 - Panel de rendimiento.  Integrante 2.

Archivo: Front/panel_rendimiento.py   (fuera de motor/: puede usar cualquier libreria)

Que hace
--------
1. Toma la carpeta de datos (por defecto Datos/) y fabrica redes de tamano
   n, 2n y 4n duplicando TODO: cada estacion, ruta y evento de horario se copia
   con un sufijo (" X2", " X3", ...).  Asi se imita lo que hace el script del
   profesor ("duplica la red y mide").
2. Corre cada operacion del contrato (menos R5, diap. 11) muchas veces en cada
   red y toma el mejor de varios lotes (reduce ruido del sistema operativo).
3. Grafica t(f*n)/t(n) medido junto a la curva de la O esperada y escribe
   el veredicto y la explicacion de cada desviacion.

Uso
---
    python Front/panel_rendimiento.py               # usa Datos/, guarda panel_rendimiento.png
    python Front/panel_rendimiento.py Pruebas/Red_pequena

Desde el front (Streamlit, Flask, Tk...):
    from Front.panel_rendimiento import correr_panel, graficar
    resultados = correr_panel("Datos")
    figura = graficar(resultados)        # figura de matplotlib

Las operaciones de otros integrantes que aun lancen NotImplementedError o
fallen se marcan "pendiente" sin detener el panel.
"""

import csv
import math
import os
import random
import shutil
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

FACTORES = [1, 2, 4]
LOTES = 5          # se toma el mejor de 5 lotes
LLAMADAS = 300     # llamadas por lote


# ----------------------------------------------------------------------
# Complejidades esperadas.  n = tamano de la red (eventos o estaciones,
# segun la operacion).  CADA INTEGRANTE CONFIRMA LAS SUYAS.
# ----------------------------------------------------------------------

def _crece(o, f, n_base):
    """Cuanto deberia crecer el tiempo al pasar de n a f*n."""
    n = float(n_base)
    if o == "1":
        return 1.0
    if o == "log n":
        return math.log2(f * n) / math.log2(n)
    if o == "n":
        return float(f)
    if o == "n log n":
        return f * math.log2(f * n) / math.log2(n)
    raise ValueError(o)


# clave, requisito, etiqueta, O esperada, "por que" (va al panel y al README)
OPERACIONES = [
    ["carga",   "Carga", "Red(carpeta)", "n log n",
     "Lee los 3 CSV y ordena ~E eventos de horarios con merge sort propio."],
    ["estado",  "R1", "estado(nombre)", "log n",
     "CONFIRMAR con Integrante 1."],
    ["autocompletar", "R2", "autocompletar('CAL', 5)", "log n",
     "CONFIRMAR con Integrante 1 (log n + k, k fijo)."],
    ["rango",   "R3", "rango('CALLE 26','CALLE 80')", "n",
     "CONFIRMAR con Integrante 1. Es O(log n + m); al duplicar la red las copias "
     "'CALLE 3X X2' caen dentro del rango, asi que m tambien se duplica."],
    ["proximo_bus", "R4", "proximo_bus(est, ruta, hora)", "log n",
     "Dos busquedas binarias: clave ruta-estacion (log G) y hora (log H)."],
    ["ranking", "R6", "ranking(10)", "1",
     "Precalculado: con cache valida solo copia k=10 elementos -> O(k)."],
    ["ranking_cierre", "R6", "cerrar + ranking(10) + reabrir", "n",
     "Cerrar invalida el nivel 2 de la cache: se refiltra la lista de S estaciones."],
    ["editar",  "R7", "agregar_parada + quitar_parada", "1",
     "CONFIRMAR con Integrante 4. Duplicar la red duplica la CANTIDAD de rutas, "
     "no su longitud; si la ruta se ubica en O(log R) o O(1) no deberia crecer."],
    ["cerrar",  "R8", "cerrar + reabrir", "log n",
     "CONFIRMAR con Integrante 4."],
    ["deshacer", "R9", "cerrar + deshacer", "1",
     "CONFIRMAR con Integrante 4 (pila: O(1) + costo de la operacion)."],
    ["fila",    "R10", "simular_fila(llegadas, 5, 100)", "n",
     "CONFIRMAR con Integrante 1. n = numero de llegadas."],
]


# ----------------------------------------------------------------------
# Fabricar redes de tamano f*n
# ----------------------------------------------------------------------

def _leer(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.reader(f))
    return filas[0], filas[1:]


def _escribir(ruta, encabezado, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)


def fabricar_red(carpeta_base, factor, destino):
    """Escribe en `destino` una red con `factor` copias de la original."""
    os.makedirs(destino, exist_ok=True)
    sufijos = [""] + [" X%d" % c for c in range(2, factor + 1)]

    enc, est = _leer(os.path.join(carpeta_base, "estaciones.csv"))
    _escribir(os.path.join(destino, "estaciones.csv"), enc,
              [[e[0] + s] for s in sufijos for e in est])

    enc, rut = _leer(os.path.join(carpeta_base, "rutas.csv"))
    _escribir(os.path.join(destino, "rutas.csv"), enc,
              [[r[0] + s.replace(" ", ""), r[1], r[2] + s] for s in sufijos for r in rut])

    ruta_h = os.path.join(carpeta_base, "horarios.csv")
    if os.path.exists(ruta_h):
        enc, hor = _leer(ruta_h)
        _escribir(os.path.join(destino, "horarios.csv"), enc,
                  [[h[0] + s.replace(" ", ""), h[1] + s, h[2]] for s in sufijos for h in hor])
    return destino


# ----------------------------------------------------------------------
# Medicion
# ----------------------------------------------------------------------

def _mejor_tiempo(funcion, llamadas=LLAMADAS, lotes=LOTES):
    """Mejor promedio por llamada (segundos) entre varios lotes."""
    mejor = None
    for _ in range(lotes):
        t0 = time.perf_counter()
        for i in range(llamadas):
            funcion(i)
        t = (time.perf_counter() - t0) / llamadas
        if mejor is None or t < mejor:
            mejor = t
    return mejor


def _preparar_casos(red, semilla=7):
    """Entradas aleatorias reales tomadas de la red, iguales en tamano para n y 2n."""
    rnd = random.Random(semilla)
    pares = []
    for ruta in red.rutas:
        for parada in ruta[1]:
            pares.append((parada[1], ruta[0]))
    casos_bus = [(*rnd.choice(pares), "%02d:%02d" % (rnd.randrange(24), rnd.randrange(60)))
                 for _ in range(LLAMADAS)]
    estaciones = [rnd.choice(red.estaciones) for _ in range(LLAMADAS)]
    # Una ruta con al menos 2 paradas para editar
    ruta_ed = None
    for ruta in red.rutas:
        if len(ruta[1]) >= 2:
            ruta_ed = ruta
            break
    return casos_bus, estaciones, ruta_ed


def medir_red(Red, simular_fila, carpeta, factor):
    """Devuelve {clave: segundos_por_llamada o None si pendiente}."""
    res = {}
    t0 = time.perf_counter()
    red = Red(carpeta)
    res["carga"] = time.perf_counter() - t0

    casos_bus, estaciones, ruta_ed = _preparar_casos(red)

    def intentar(clave, funcion, llamadas=LLAMADAS, lotes=LOTES):
        try:
            res[clave] = _mejor_tiempo(funcion, llamadas, lotes)
        except Exception as e:                 # NotImplementedError u otro
            res[clave] = None
            res[clave + "_error"] = type(e).__name__ + ": " + str(e)[:80]

    intentar("estado", lambda i: red.estado(estaciones[i]))
    intentar("autocompletar", lambda i: red.autocompletar("CAL", 5))
    intentar("rango", lambda i: red.rango("CALLE 26", "CALLE 80"), llamadas=50)
    intentar("proximo_bus", lambda i: red.proximo_bus(*casos_bus[i]))
    red.ranking(10)                            # calienta la cache
    intentar("ranking", lambda i: red.ranking(10))

    def cierre_ranking(i):
        red.cerrar(estaciones[i]); red.ranking(10); red.reabrir(estaciones[i])
    intentar("ranking_cierre", cierre_ranking, llamadas=40)

    if ruta_ed is not None:
        rid, primera = ruta_ed[0], ruta_ed[1][0][1]
        def editar(i):
            red.agregar_parada(rid, "PANEL TEMP", primera)
            red.quitar_parada(rid, "PANEL TEMP")
        intentar("editar", editar, llamadas=40)

    intentar("cerrar", lambda i: (red.cerrar(estaciones[i]), red.reabrir(estaciones[i])),
             llamadas=40)
    intentar("deshacer", lambda i: (red.cerrar(estaciones[i]), red.deshacer()), llamadas=40)

    # R10: n = llegadas, 20.000 por cada factor (formato a CONFIRMAR con Integrante 1)
    llegadas = list(range(0, 20000 * factor))
    intentar("fila", lambda i: simular_fila(llegadas, 5, 100), llamadas=1, lotes=3)
    return res


def correr_panel(carpeta_base="Datos", factores=FACTORES):
    """Mide todas las operaciones en redes de tamano f*n.
    Devuelve una lista de filas listas para graficar o mostrar en tabla."""
    from motor.__initial__ import Red, simular_fila

    temporal = tempfile.mkdtemp(prefix="rutaviva_panel_")
    mediciones = {}
    n_eventos = 0
    try:
        for f in factores:
            carpeta = fabricar_red(carpeta_base, f, os.path.join(temporal, "x%d" % f))
            mediciones[f] = medir_red(Red, simular_fila, carpeta, f)
        with open(os.path.join(carpeta_base, "horarios.csv"), encoding="utf-8") as fh:
            n_eventos = sum(1 for _ in fh) - 1
    finally:
        shutil.rmtree(temporal, ignore_errors=True)

    filas = []
    for clave, req, etiqueta, o, porque in OPERACIONES:
        base = mediciones[factores[0]].get(clave)
        fila = {"clave": clave, "requisito": req, "operacion": etiqueta,
                "O": "O(%s)" % o, "porque": porque, "tiempos": [], "razones": [],
                "esperadas": [], "veredicto": "pendiente",
                "error": mediciones[factores[0]].get(clave + "_error", "")}
        if base:
            n_ref = max(n_eventos, 2)
            for f in factores:
                t = mediciones[f].get(clave)
                fila["tiempos"].append(t)
                fila["razones"].append(t / base if t else None)
                fila["esperadas"].append(_crece(o, f, n_ref))
            ultima, esperada = fila["razones"][-1], fila["esperadas"][-1]
            if ultima is None:
                fila["veredicto"] = "pendiente"
            elif ultima <= esperada * 1.5 + 0.3:
                fila["veredicto"] = "coincide"
            else:
                fila["veredicto"] = "crece mas de lo esperado"
        filas.append(fila)
    return {"factores": factores, "filas": filas, "n_eventos": n_eventos}


# ----------------------------------------------------------------------
# Grafica y tabla
# ----------------------------------------------------------------------

def graficar(resultados):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    factores = resultados["factores"]
    filas = [f for f in resultados["filas"] if f["razones"]]
    columnas = 4
    renglones = max(1, math.ceil(len(filas) / columnas))
    fig, ejes = plt.subplots(renglones, columnas, figsize=(4 * columnas, 3.2 * renglones),
                             squeeze=False)
    for i, fila in enumerate(filas):
        ax = ejes[i // columnas][i % columnas]
        ax.plot(factores, fila["esperadas"], "--", color="#888888", lw=1.5,
                label="esperado " + fila["O"])
        ax.plot(factores, fila["razones"], "o-", color="#1f6feb", lw=2, label="medido")
        ax.set_title("%s  %s" % (fila["requisito"], fila["operacion"]), fontsize=9)
        ax.set_xticks(factores)
        ax.set_xticklabels(["%dn" % f if f > 1 else "n" for f in factores])
        ax.set_ylabel("t / t(n)", fontsize=8)
        tope = 2.0
        for v in fila["esperadas"] + [r for r in fila["razones"] if r]:
            if v * 1.25 > tope:
                tope = v * 1.25
        ax.set_ylim(0, tope)          # escala desde 0: el ruido no parece crecimiento
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc="upper left", frameon=True, framealpha=0.9)
        color = "#1a7f37" if fila["veredicto"] == "coincide" else "#cf222e"
        ax.text(0.98, 0.04, fila["veredicto"], transform=ax.transAxes, ha="right",
                fontsize=8, color=color)
    for j in range(len(filas), renglones * columnas):
        ejes[j // columnas][j % columnas].axis("off")
    fig.suptitle("RutaViva - crecimiento del tiempo al duplicar la red (n = %d eventos)"
                 % resultados["n_eventos"], fontsize=11)
    fig.tight_layout()
    return fig


def tabla_texto(resultados):
    lineas = []
    fs = resultados["factores"]
    lineas.append("%-4s %-34s %-11s %s   %s" % (
        "Req", "Operacion", "O esperada",
        "  ".join("t(%dn)/t(n)" % f for f in fs[1:]), "Veredicto"))
    for f in resultados["filas"]:
        if f["razones"]:
            rz = "  ".join(("%10.2f" % r) if r else "         -" for r in f["razones"][1:])
            esp = "  (esp. " + " / ".join("%.2f" % e for e in f["esperadas"][1:]) + ")"
        else:
            rz, esp = "pendiente: " + f["error"], ""
        lineas.append("%-4s %-34s %-11s %s%s   %s" % (
            f["requisito"], f["operacion"], f["O"], rz, esp,
            f["veredicto"] if f["razones"] else ""))
    return "\n".join(lineas)


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "Datos")
    resultados = correr_panel(carpeta)
    print(tabla_texto(resultados))
    salida = os.path.join(RAIZ, "panel_rendimiento.png")
    graficar(resultados).savefig(salida, dpi=130)
    print("\nGrafica guardada en", salida)
