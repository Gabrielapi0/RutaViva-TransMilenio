# RED SIMULADA SOLO PARA PROBAR P2 LOCALMENTE. NO SE ENTREGA.
# La Red real es la de Integrante 1; aquí solo se pega lo de INTEGRACION_P2.md.
import csv
from .horarios import IndiceHorarios
from .ranking import IndiceRanking


class Red:
    def __init__(self, carpeta):
        base = carpeta.rstrip("/\\")
        self.estaciones = []
        with open(base + "/estaciones.csv", encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                self.estaciones.append(fila["nombre"].strip())
        self.rutas = []
        with open(base + "/rutas.csv", encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                if not self.rutas or self.rutas[-1][0] != fila["ruta"]:
                    self.rutas.append([fila["ruta"], []])
                self.rutas[-1][1].append([int(fila["orden"]), fila["estacion"].strip()])
        self.cerradas = []
        self._hist = []
        self._redo = []
        # --- Integrante 2 ---
        self._horarios = IndiceHorarios(base + "/horarios.csv")
        self._ranking = IndiceRanking(self._horarios)

    # --- Integrante 2 (copiado de INTEGRACION_P2.md) ---
    def proximo_bus(self, estacion, ruta, hora):
        return self._horarios.proximo(estacion, ruta, hora, self.rutas, self.cerradas)

    def ranking(self, k):
        return self._ranking.top(k, self.estaciones, self.rutas, self.cerradas)

    def _invalidar_p2(self, rutas_cambiaron=True):
        if rutas_cambiaron:
            self._horarios.invalidar()
            self._ranking.invalidar()
        else:
            self._ranking.invalidar_cierres()

    # --- Simulaciones mínimas de otros integrantes (solo para probar) ---
    def _ruta(self, rid):
        for r in self.rutas:
            if r[0] == rid:
                return r
        return None

    def cerrar(self, nombre):
        self.cerradas.append(nombre)
        self._hist.append(("cerrar", nombre)); self._redo = []
        self._invalidar_p2(False)

    def reabrir(self, nombre):
        self.cerradas = [c for c in self.cerradas if c != nombre]
        self._hist.append(("reabrir", nombre)); self._redo = []
        self._invalidar_p2(False)

    def quitar_parada(self, ruta, estacion):
        r = self._ruta(ruta)
        for i, p in enumerate(r[1]):
            if p[1] == estacion:
                r[1].pop(i)
                self._hist.append(("quitar", ruta, estacion, i)); self._redo = []
                break
        self._invalidar_p2()

    def agregar_parada(self, ruta, nueva, despues_de):
        r = self._ruta(ruta)
        for i, p in enumerate(r[1]):
            if p[1] == despues_de:
                r[1].insert(i + 1, [0, nueva])
                self._hist.append(("agregar", ruta, nueva, i + 1)); self._redo = []
                break
        self._invalidar_p2()

    def deshacer(self):
        op = self._hist.pop()
        if op[0] == "quitar":
            self._ruta(op[1])[1].insert(op[3], [0, op[2]])
        elif op[0] == "agregar":
            self._ruta(op[1])[1].pop(op[3])
        elif op[0] == "cerrar":
            self.cerradas = [c for c in self.cerradas if c != op[1]]
        else:
            self.cerradas.append(op[1])
        self._redo.append(op)
        self._invalidar_p2()

    def estado(self, nombre): raise NotImplementedError
    def autocompletar(self, prefijo, k): raise NotImplementedError
    def rango(self, desde, hasta): raise NotImplementedError
    def viaje(self, origen, destino): raise NotImplementedError
    def recorrido(self, ruta, al_reves=False): raise NotImplementedError
    def rehacer(self): raise NotImplementedError


def simular_fila(llegadas, frecuencia, capacidad):
    raise NotImplementedError
