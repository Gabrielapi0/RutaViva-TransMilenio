"""Comprueba que R7-R9 SI quedan activos dentro de una clase Red.

Reproduce el problema encontrado en la integracion: Red tenia metodos `pass`
(devuelven None) y un `cerrar` propio que no pasaba por el historial. Si Red
define un metodo, ese pisa al de OperarRed aunque herede de el.

Si existe `motor.Red` (repo completo), tambien se revisa la clase real.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from motor.operar import OperarRed, instalar_operaciones, METODOS_OPERAR  # noqa: E402


def _datos():
    return (["ALFA", "BETA", "GAMMA", "DELTA", "EPSILON"],
            [["RUTA_A", [[1, "ALFA"], [2, "BETA"], [3, "GAMMA"]]]])


class RedRota(OperarRed):
    """Hereda bien, pero define metodos vacios: pisan a los de OperarRed."""

    def __init__(self):
        self.estaciones, self.rutas = _datos()
        self.cerradas = []

    def agregar_parada(self, ruta, nueva, despues_de):
        pass

    def quitar_parada(self, ruta, estacion):
        pass

    def cerrar(self, nombre):          # version propia: ni bool ni historial
        self.cerradas.append(nombre)

    def deshacer(self):
        pass


class RedArreglada:
    def __init__(self):
        self.estaciones, self.rutas = _datos()
        self.cerradas = []

    def agregar_parada(self, ruta, nueva, despues_de):
        pass

    def cerrar(self, nombre):
        self.cerradas.append(nombre)


instalar_operaciones(RedArreglada)


def test_el_problema_existe_sin_instalar():
    r = RedRota()
    assert r.agregar_parada("RUTA_A", "DELTA", "ALFA") is None     # pass pisa al mixin
    assert r.deshacer() is None


def test_instalar_operaciones_arregla_la_clase():
    r = RedArreglada()
    assert r.agregar_parada("RUTA_A", "DELTA", "ALFA") is True
    assert r.recorrido("RUTA_A") == ["ALFA", "DELTA", "BETA", "GAMMA"]
    assert r.cerrar("GAMMA") is True                  # ya no devuelve None
    assert r.cerrar("GAMMA") is False
    assert r.deshacer() is True                       # el cierre SI esta en el historial
    assert r.cerradas == []
    assert r.deshacer() is True                       # y la parada agregada tambien
    assert r.recorrido("RUTA_A") == ["ALFA", "BETA", "GAMMA"]
    assert r.deshacer() is False
    assert r.rehacer() is True and r.rehacer() is True and r.rehacer() is False


def test_todos_los_metodos_del_contrato_estan_instalados():
    for nombre in METODOS_OPERAR:
        assert getattr(RedArreglada, nombre) is getattr(OperarRed, nombre), nombre


def test_red_real_si_existe():
    try:
        from motor import Red
    except Exception:
        return    # repo parcial: nada que revisar
    for nombre in ["agregar_parada", "quitar_parada", "recorrido", "cerrar",
                   "reabrir", "deshacer", "rehacer"]:
        assert getattr(Red, nombre) is getattr(OperarRed, nombre), (
            "Red.%s no es el de OperarRed: esta pisado por una version vacia o propia. "
            "Borrarlo de Red o usar instalar_operaciones(Red)." % nombre)


if __name__ == "__main__":
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_"):
            f()
            print("OK", nombre)
