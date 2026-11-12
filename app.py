"""RutaViva · Planeador TransMilenio — servidor de la interfaz web.

Arranque (un solo comando):   python app.py
Opciones:  --datos CARPETA (por defecto ./Datos)   --puerto N (8000)   --sin-navegador

Solo usa la librería estándar. Toda la lógica vive en motor/ (del equipo); este
archivo únicamente traduce peticiones HTTP a llamadas del motor y adapta lo que
devuelve cada requisito al formato que dibuja la página. No reimplementa reglas.
"""

import argparse
import json
import mimetypes
import pathlib
import random
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
from motor import Red, simular_fila  # noqa: E402
from motor.viajes import IndiceViajes, detalle_recorrido  # noqa: E402

WEB = RAIZ / "web"
CANDADO = threading.Lock()
RED = None
CARPETA = None


def hhmm(m):
    m = int(m)
    return f"{(m // 60) % 24:02d}:{m % 60:02d}"


def minutos(h):
    a, b = h.split(":")
    return int(a) * 60 + int(b)


def norm(t):
    return (t or "").strip().upper()


# ------------------------------------------------------- adaptadores del motor
def estado_de(nombre):
    """R1 del equipo devuelve ('OPERATIVA'|'CERRADA'|'NO EXISTE', rutas)."""
    res = RED.estado(nombre)
    texto, rutas = (res[0], res[1]) if isinstance(res, (list, tuple)) else (res, [])
    est = {"OPERATIVA": "abierta", "ABIERTA": "abierta", "CERRADA": "cerrada"}.get(str(texto).upper())
    return est, list(rutas or [])


def conteos():
    """Buses al día por estación abierta, tomados del índice de R6 (Integrante 2)."""
    try:
        pares = RED._ranking.top_con_conteo(len(RED.estaciones), RED.estaciones, RED.rutas, RED.cerradas)
        return {p[0]: p[1] for p in pares}
    except Exception:  # noqa: BLE001
        return {}


def ranking(k):
    try:
        return [list(p) for p in RED._ranking.top_con_conteo(k, RED.estaciones, RED.rutas, RED.cerradas)]
    except Exception:  # noqa: BLE001
        return [[n, None] for n in (RED.ranking(k) or [])]


def nombres_rutas():
    return sorted(r[0] for r in RED.rutas)


def paradas_de(ruta, al_reves=False):
    """R7 recorrido(); si aún no está conectado en Red, se lee la lista de rutas del motor."""
    rec = RED.recorrido(ruta, al_reves)
    if rec is None:
        for r in RED.rutas:
            if r[0] == ruta:
                rec = [p[1] for p in r[1]]
                if al_reves:
                    rec = rec[::-1]
                break
    return rec or []


def capacidades():
    """¿Están conectados R7 y R9 en la clase Red? (los stubs devuelven None)."""
    r7 = RED.recorrido(RED.rutas[0][0]) is not None if RED.rutas else False
    vacio = (lambda self: None).__code__.co_code
    try:
        r9 = RED.deshacer.__func__.__code__.co_code != vacio
    except AttributeError:
        r9 = True
    return r7, r9


def info():
    r7, r9 = capacidades()
    h = getattr(RED, "_historial", None)
    deshacer = len(h.pila_deshacer) if h else 0
    rehacer = len(h.pila_rehacer) if h else 0
    return {"deshacer": deshacer, "rehacer": rehacer, "cerradas": sorted(RED.cerradas),
            "estaciones": len(RED.estaciones), "rutas": len(RED.rutas), "r7": r7, "r9": r9}


# ----------------------------------------------------------------- endpoints
def api_estado(q):
    n = norm(q.get("nombre"))
    est, rutas = estado_de(n)
    return {"nombre": n, "estado": est, "rutas": sorted(rutas), "buses": conteos().get(n, 0)}


def api_viaje(q):
    o, d = norm(q.get("origen")), norm(q.get("destino"))
    hora = q.get("hora") or "07:00"
    res = RED.viaje(o, d)
    eo, ed = estado_de(o)[0], estado_de(d)[0]
    if res is None or (isinstance(res, list) and res and res[0] == "ERROR"):
        motivo = "no_existe" if eo is None or ed is None else "cerrada" if "cerrada" in (eo, ed) else "sin_ruta"
        return {"ok": False, "motivo": motivo, "estado_origen": eo, "estado_destino": ed}
    if res[0] == "MISMO DESTINO":
        return {"ok": True, "tramos": [], "hora": hora, "total_paradas": 0}
    indice = IndiceViajes(RED.rutas, RED.estaciones)
    detalle = detalle_recorrido(RED.rutas, indice, res, o, d, RED.cerradas)
    salida, t = [], hora
    for ruta, estaciones in detalle:
        sube, baja = estaciones[0], estaciones[-1]
        bus = RED.proximo_bus(sube, ruta, t)
        llegada = RED.proximo_bus(baja, ruta, bus) if bus else None
        salida.append({"ruta": ruta, "sube": sube, "baja": baja, "paradas": len(estaciones) - 1,
                       "estaciones": [{"nombre": e, "estado": estado_de(e)[0]} for e in estaciones],
                       "bus": bus, "llegada": llegada,
                       "manana": bool(bus) and minutos(bus) < minutos(t)})
        if llegada:
            t = llegada
    return {"ok": True, "tramos": salida, "hora": hora, "total_paradas": res[4], "tipo": res[0]}


def api_pantalla(q):
    est, hora = norm(q.get("estacion")), q.get("hora") or "07:00"
    estado, rutas = estado_de(est)
    filas = []
    if estado == "abierta":
        for r in sorted(rutas):
            prox = RED.proximo_bus(est, r, hora)
            rec = paradas_de(r)
            filas.append({"ruta": r, "destino": rec[-1] if rec else "", "proximo": prox,
                          "minutos": (minutos(prox) - minutos(hora)) if prox else None})
        filas.sort(key=lambda f: (f["minutos"] is None, f["minutos"] or 0, f["ruta"]))
    return {"estacion": est, "estado": estado, "filas": filas}


def api_fila(q):
    """R10 del equipo: simular_fila(llegadas, frecuencia, capacidad) con
    llegadas[minuto] = personas que llegan en ese minuto. Devuelve un dict con
    atendidos, en_espera y espera_promedio."""
    p = max(1, min(int(q.get("pasajeros", 15000)), 50000))
    ventana = max(5, min(int(q.get("ventana", 90)), 240))
    frec = max(1, int(q.get("frecuencia", 1)))
    cap = max(1, int(q.get("capacidad", 160)))
    patron = q.get("patron", "pico")
    rnd = random.Random(int(q.get("semilla", 42)))
    llegadas = [0] * ventana
    for _ in range(p):
        if patron == "uniforme":
            m = rnd.randrange(ventana)
        elif patron == "oleadas":
            m = min(ventana - 1, rnd.randrange(0, ventana, 6) + int(rnd.expovariate(1.2)))
        else:
            m = min(ventana - 1, int(rnd.triangular(0, ventana, ventana * 0.45)))
        llegadas[m] += 1

    t0 = time.perf_counter()
    total = simular_fila(llegadas, frec, cap)
    ms = (time.perf_counter() - t0) * 1000

    # Serie para la animación: el MISMO motor corrido sobre los primeros m minutos,
    # en cada minuto en que sale un bus (así la página no recalcula nada por su cuenta).
    salidas = [m for m in range(ventana) if (m + 1) % frec == 0]
    paso = max(1, len(salidas) // 120)
    serie, atendidos_antes = [], 0
    for m in salidas[::paso]:
        parcial = simular_fila(llegadas[:m + 1], frec, cap)
        serie.append({"t": 360 + m, "h": hhmm(360 + m), "cola": parcial["en_espera"],
                      "suben": parcial["atendidos"] - atendidos_antes})
        atendidos_antes = parcial["atendidos"]
    if not serie:
        serie = [{"t": 360, "h": "06:00", "cola": total["en_espera"], "suben": 0}]
    return {
        "pasajeros": p, "frecuencia": frec, "capacidad": cap, "ms_motor": round(ms, 1),
        "buses": len(salidas), "atendidos": total["atendidos"], "en_espera": total["en_espera"],
        "espera_promedio": total["espera_promedio"], "cola_max": max(s["cola"] for s in serie),
        "llenos": sum(1 for s in serie if s["suben"] >= cap * paso) if paso == 1 else None,
        "serie": serie, "inicio": "06:00", "fin": hhmm(360 + ventana),
    }


def api_rendimiento(q, recalcular=False):
    """R11 del Integrante 2 (Front/panel_rendimiento.py), presentado en esta página."""
    archivo = WEB / "rendimiento.json"
    if recalcular or not archivo.exists():
        from Front.panel_rendimiento import correr_panel
        res = correr_panel(CARPETA)
        n = len(RED.estaciones)
        ops = []
        for f in res["filas"]:
            if not f["tiempos"] or f["tiempos"][0] is None:
                ops.append({"clave": f["clave"], "requisito": f["requisito"], "etiqueta": f["operacion"], "o": f["O"],
                            "n": "", "pendiente": True, "explicacion": f.get("error") or f["porque"]})
                continue
            med = [t * 1e6 if t else 0 for t in f["tiempos"]]
            esp = [med[0] * e for e in f["esperadas"]]
            raz = [med[i + 1] / med[i] for i in range(len(med) - 1) if med[i]]
            raz_e = [f["esperadas"][i + 1] / f["esperadas"][i] for i in range(len(med) - 1)]
            ops.append({"clave": f["clave"], "requisito": f["requisito"], "etiqueta": f["operacion"], "o": f["O"],
                        "n": "", "medido": med, "esperado": esp,
                        "razon": sum(raz) / len(raz) if raz else 1, "razon_esperada": sum(raz_e) / len(raz_e) if raz_e else 1,
                        "coincide": f["veredicto"] == "coincide", "explicacion": f["porque"]})
        data = {"copias": res["factores"], "tamanos": [c * n for c in res["factores"]],
                "fecha": time.strftime("%Y-%m-%d %H:%M"), "operaciones": ops}
        archivo.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    return json.loads(archivo.read_text(encoding="utf-8"))


def cambio(fn, *args, verificar=None):
    """Llama una operación del motor. Si devuelve None (todavía es un stub o no
    informa), se verifica el efecto comparando el estado antes y después."""
    antes = verificar() if verificar else None
    r = fn(*args)
    if r is None and verificar:
        r = verificar() != antes
    res = {"ok": bool(r)}
    res.update(info())
    return res


GET = {
    "/api/info": lambda q: info(),
    "/api/estado": api_estado,
    "/api/autocompletar": lambda q: RED.autocompletar(norm(q.get("prefijo")), int(q.get("k", 8))) or [],
    "/api/rango": lambda q: RED.rango(norm(q.get("desde")), norm(q.get("hasta"))) or [],
    "/api/proximo": lambda q: {"hora": RED.proximo_bus(norm(q.get("estacion")), q.get("ruta", ""), q.get("hora", "07:00"))},
    "/api/viaje": api_viaje,
    "/api/pantalla": api_pantalla,
    "/api/ranking": lambda q: ranking(int(q.get("k", 10))),
    "/api/rutas": lambda q: nombres_rutas(),
    "/api/recorrido": lambda q: [{"nombre": e, "estado": estado_de(e)[0]}
                                 for e in paradas_de(q.get("ruta", ""), q.get("al_reves") == "1")],
    "/api/fila": api_fila,
    "/api/rendimiento": api_rendimiento,
}

POST = {
    "/api/agregar": lambda b: cambio(RED.agregar_parada, b.get("ruta", ""), norm(b.get("nueva")), b.get("despues_de", ""),
                                     verificar=lambda: paradas_de(b.get("ruta", ""))),
    "/api/quitar": lambda b: cambio(RED.quitar_parada, b.get("ruta", ""), norm(b.get("estacion")),
                                    verificar=lambda: paradas_de(b.get("ruta", ""))),
    "/api/cerrar": lambda b: cambio(RED.cerrar, norm(b.get("nombre")), verificar=lambda: sorted(RED.cerradas)),
    "/api/reabrir": lambda b: cambio(RED.reabrir, norm(b.get("nombre")), verificar=lambda: sorted(RED.cerradas)),
    "/api/deshacer": lambda b: cambio(RED.deshacer, verificar=lambda: (sorted(RED.cerradas), str(RED.rutas))),
    "/api/rehacer": lambda b: cambio(RED.rehacer, verificar=lambda: (sorted(RED.cerradas), str(RED.rutas))),
    "/api/rendimiento": lambda b: api_rendimiento(b, recalcular=True),
}


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _json(self, data, codigo=200):
        cuerpo = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in GET:
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            try:
                with CANDADO:
                    return self._json(GET[url.path](q))
            except Exception as e:  # noqa: BLE001
                return self._json({"error": f"{type(e).__name__}: {e}"}, 400)
        ruta = "index.html" if url.path in ("/", "") else url.path.lstrip("/")
        archivo = (WEB / ruta).resolve()
        if not str(archivo).startswith(str(WEB.resolve())) or not archivo.is_file():
            self.send_error(404)
            return
        datos = archivo.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(str(archivo))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_POST(self):
        url = urlparse(self.path)
        if url.path not in POST:
            self.send_error(404)
            return
        largo = int(self.headers.get("Content-Length") or 0)
        cuerpo = json.loads(self.rfile.read(largo) or b"{}") if largo else {}
        try:
            with CANDADO:
                return self._json(POST[url.path](cuerpo))
        except Exception as e:  # noqa: BLE001
            return self._json({"error": f"{type(e).__name__}: {e}"}, 400)


def main():
    global RED, CARPETA
    ap = argparse.ArgumentParser(description="RutaViva · Planeador TransMilenio")
    ap.add_argument("--datos", default=str(RAIZ / "Datos"))
    ap.add_argument("--puerto", type=int, default=8000)
    ap.add_argument("--sin-navegador", action="store_true")
    a = ap.parse_args()
    CARPETA = a.datos
    print(f"Cargando la red desde {a.datos} …")
    RED = Red(a.datos)
    url = f"http://localhost:{a.puerto}"
    srv = ThreadingHTTPServer(("127.0.0.1", a.puerto), Manejador)
    print(f"RutaViva lista en {url}  (Ctrl+C para salir)")
    if not a.sin_navegador:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nHasta luego.")


if __name__ == "__main__":
    main()
