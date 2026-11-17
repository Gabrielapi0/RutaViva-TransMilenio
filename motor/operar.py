"""Operar la red (R7-R9, Integrante 4).

DOS formas de conectarlo a Red (la segunda es la que arregla el problema de
los metodos `pass`):

  1) class Red(OperarRed): ...      y BORRAR de Red los metodos agregar_parada,
     quitar_parada, recorrido, cerrar, reabrir, deshacer, rehacer. Si Red los
     define (aunque sea con `pass`), pisan a los de OperarRed.

  2) Al final del archivo de Red:   instalar_operaciones(Red)
     Copia los metodos de este modulo SOBRE la clase y tapa cualquier version
     vacia o propia que tuviera Red.

Requisitos sobre Red (contrato): self.estaciones, self.rutas, self.cerradas
(listas compartidas; `cerradas` empieza vacia y la maneja este modulo).
Opcional: llamar self._preparar_operaciones() al final de Red.__init__ para
construir los indices al cargar (si no, se construyen en la primera llamada).

Retornos (enunciado oficial): agregar_parada, quitar_parada, cerrar, reabrir,
deshacer y rehacer devuelven True si cambiaron algo y False si no (sin
excepciones y sin tocar la red ni el historial). recorrido devuelve una lista
de nombres ([] si la ruta no existe).
"""
from ._comun import normalizar, buscar_posicion
from . import edicion_rutas as er
from . import cierres as ci
from . import indices as ix
from .historial import (Historial, CmdCerrar, CmdReabrir,
                        CmdAgregarParada, CmdQuitarParada)


class OperarRed:

    # ---------- soporte interno ----------
    def _hist(self):
        if getattr(self, "_historial", None) is None:
            self._historial = Historial()
        return self._historial

    def _cambio(self):
        """Sube el contador de version. R6 puede usarlo para invalidar su cache."""
        self._version = getattr(self, "_version", 0) + 1

    def _preparar_operaciones(self):
        """Arma las tablas hash de rutas y estaciones (opcional, al cargar)."""
        ix.tabla_rutas(self)
        ix.tabla_estaciones(self)

    def _ruta(self, id_normalizado):
        """Objeto [id, paradas] de la ruta o None. O(1) esperado (tabla hash)."""
        return ix.buscar_ruta(self, id_normalizado)

    def _existe_estacion(self, nombre):
        """True si la estacion existe (nombre ya normalizado). O(1) esperado."""
        return ix.existe_estacion(self, nombre)

    def _abierta(self, nombre):
        """True si la estacion no esta cerrada. Usar en R1-R6. O(log c)."""
        return ci.abierta(self.cerradas, normalizar(nombre))

    # ---------- R7 ----------
    def agregar_parada(self, ruta, nueva, despues_de):
        r, n, d = normalizar(ruta), normalizar(nueva), normalizar(despues_de)
        if r is None or n is None or d is None:
            return False
        obj = self._ruta(r)
        if obj is None or not er.validar_agregar(obj[1], n, d):
            return False
        if not self._existe_estacion(n):
            return False
        if not ci.abierta(self.cerradas, n):      # decision: no se agrega una cerrada
            return False
        self._hist().ejecutar(CmdAgregarParada(obj, n, d), self)
        self._cambio()
        return True

    def quitar_parada(self, ruta, estacion):
        r, e = normalizar(ruta), normalizar(estacion)
        if r is None or e is None:
            return False
        obj = self._ruta(r)
        if obj is None or buscar_posicion(obj[1], e) == -1:
            return False
        self._hist().ejecutar(CmdQuitarParada(obj, e), self)
        self._cambio()
        return True

    def recorrido(self, ruta, al_reves=False):
        r = normalizar(ruta)
        if r is None:
            return []
        obj = self._ruta(r)
        if obj is None:
            return []
        return er.recorrido(obj[1], al_reves)

    # ---------- R8 ----------
    def cerrar(self, nombre):
        n = normalizar(nombre)
        if n is None or not self._existe_estacion(n):
            return False
        if not ci.abierta(self.cerradas, n):      # ya estaba cerrada
            return False
        self._hist().ejecutar(CmdCerrar(n), self)
        self._cambio()
        return True

    def reabrir(self, nombre):
        n = normalizar(nombre)
        if n is None or not self._existe_estacion(n):
            return False
        if ci.abierta(self.cerradas, n):          # ya estaba abierta
            return False
        self._hist().ejecutar(CmdReabrir(n), self)
        self._cambio()
        return True

    # ---------- R9 ----------
    def deshacer(self):
        ok = self._hist().deshacer(self)
        if ok:
            self._cambio()
        return ok

    def rehacer(self):
        ok = self._hist().rehacer(self)
        if ok:
            self._cambio()
        return ok


# Metodos que instalar_operaciones copia sobre la clase Red.
METODOS_OPERAR = [
    "agregar_parada", "quitar_parada", "recorrido",
    "cerrar", "reabrir", "deshacer", "rehacer",
    "_abierta", "_existe_estacion", "_ruta", "_hist", "_cambio",
    "_preparar_operaciones",
]


def instalar_operaciones(clase):
    """Pone los metodos de R7-R9 en `clase` (normalmente Red), reemplazando
    versiones vacias (`pass`) o propias que ya tuviera. Devuelve la clase."""
    for nombre in METODOS_OPERAR:
        setattr(clase, nombre, getattr(OperarRed, nombre))
    return clase
