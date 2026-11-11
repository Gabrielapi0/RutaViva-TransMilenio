"""R9 - Deshacer / rehacer con el patron Comando y dos pilas.

Cada comando sabe aplicarse (aplicar) y revertirse (revertir) sobre la red.
Las pilas son listas usadas con append/pop: O(1) por operacion de pila
(mas el costo del propio comando).
"""
from . import edicion_rutas as er
from . import cierres as ci


class CmdCerrar:
    def __init__(self, nombre):
        self.nombre = nombre

    def aplicar(self, red):
        ci.aplicar_cerrar(red.cerradas, self.nombre)

    def revertir(self, red):
        ci.revertir_cerrar(red.cerradas, self.nombre)


class CmdReabrir:
    def __init__(self, nombre):
        self.nombre = nombre
        self.pos = -1

    def aplicar(self, red):
        self.pos = ci.aplicar_reabrir(red.cerradas, self.nombre)

    def revertir(self, red):
        ci.revertir_reabrir(red.cerradas, self.nombre, self.pos)


class CmdAgregarParada:
    def __init__(self, ruta, nueva, despues_de):
        self.ruta = ruta
        self.nueva = nueva
        self.despues_de = despues_de
        self.pos = -1

    def aplicar(self, red):
        self.pos = er.aplicar_agregar(red.rutas, self.ruta, self.nueva,
                                      self.despues_de)

    def revertir(self, red):
        er.revertir_agregar(red.rutas, self.ruta, self.pos)


class CmdQuitarParada:
    def __init__(self, ruta, estacion):
        self.ruta = ruta
        self.estacion = estacion
        self.pos = -1

    def aplicar(self, red):
        self.pos = er.aplicar_quitar(red.rutas, self.ruta, self.estacion)

    def revertir(self, red):
        er.revertir_quitar(red.rutas, self.ruta, self.estacion, self.pos)


class Historial:
    """Dos pilas: lo que se puede deshacer y lo que se puede rehacer."""

    def __init__(self):
        self.pila_deshacer = []
        self.pila_rehacer = []

    def ejecutar(self, cmd, red):
        """Aplica un cambio NUEVO: se apila y se borra lo que habia para rehacer."""
        cmd.aplicar(red)
        self.pila_deshacer.append(cmd)
        self.pila_rehacer = []

    def deshacer(self, red):
        """Revierte el ultimo comando. False si no hay nada que deshacer."""
        if len(self.pila_deshacer) == 0:
            return False
        cmd = self.pila_deshacer.pop()
        cmd.revertir(red)
        self.pila_rehacer.append(cmd)
        return True

    def rehacer(self, red):
        """Reaplica el ultimo comando deshecho. False si no hay nada."""
        if len(self.pila_rehacer) == 0:
            return False
        cmd = self.pila_rehacer.pop()
        cmd.aplicar(red)
        self.pila_deshacer.append(cmd)
        return True
