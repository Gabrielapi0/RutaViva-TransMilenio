"""Operar la red (R7-R9, Integrante 4).

Uso: la clase Red hereda de OperarRed.

    from .operar import OperarRed
    class Red(OperarRed):
        ...

Requisitos sobre Red (contrato): self.estaciones, self.rutas, self.cerradas
(listas compartidas). No hay que llamar a ningun __init__ extra: el
historial se crea solo la primera vez que se usa.

Valores de retorno (decision del equipo, el enunciado no los fija):
las operaciones devuelven True si se aplicaron y False si se rechazaron
(sin excepcion y sin tocar la red ni el historial).
"""
from ._comun import normalizar, buscar_ruta, buscar_posicion
from . import edicion_rutas as er
from . import cierres as ci
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

    def _existe_estacion(self, nombre):
        """Busqueda lineal por defecto; Red puede sobreescribirla con algo mas rapido."""
        for e in self.estaciones:
            if e == nombre:
                return True
        return False

    def _abierta(self, nombre):
        """True si la estacion no esta cerrada. Usar en R1-R6."""
        return ci.abierta(self.cerradas, normalizar(nombre))

    # ---------- R7 ----------
    def agregar_parada(self, ruta, nueva, despues_de):
        r, n, d = normalizar(ruta), normalizar(nueva), normalizar(despues_de)
        if r is None or n is None or d is None:
            return False
        if not er.validar_agregar(self.rutas, r, n, d):
            return False
        if not self._existe_estacion(n):
            return False
        if not ci.abierta(self.cerradas, n):      # decision: no se agrega una cerrada
            return False
        id_real = buscar_ruta(self.rutas, r)[0]
        self._hist().ejecutar(CmdAgregarParada(id_real, n, d), self)
        self._cambio()
        return True

    def quitar_parada(self, ruta, estacion):
        r, e = normalizar(ruta), normalizar(estacion)
        if r is None or e is None:
            return False
        obj = buscar_ruta(self.rutas, r)
        if obj is None or buscar_posicion(obj[1], e) == -1:
            return False
        self._hist().ejecutar(CmdQuitarParada(obj[0], e), self)
        self._cambio()
        return True

    def recorrido(self, ruta, al_reves=False):
        return er.recorrido(self.rutas, normalizar(ruta), al_reves)

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
