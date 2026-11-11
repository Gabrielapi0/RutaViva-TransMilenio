from _red_prueba import red_mini, RedPrueba
import os

DATOS = os.environ.get("DATOS_RUTAVIVA", "")


def test_recorrido_y_reves():
    r = red_mini()
    assert r.recorrido("RUTA_A") == ["ALFA", "BETA", "GAMMA"]
    assert r.recorrido("RUTA_A", al_reves=True) == ["GAMMA", "BETA", "ALFA"]
    assert r.recorrido("RUTA_A", False) == ["ALFA", "BETA", "GAMMA"]


def test_recorrido_ruta_inexistente():
    assert red_mini().recorrido("NO_EXISTE") == []


def test_agregar_en_medio_y_renumera():
    r = red_mini()
    assert r.agregar_parada("RUTA_A", "ZETA", "ALFA") is True
    assert r.recorrido("RUTA_A") == ["ALFA", "ZETA", "BETA", "GAMMA"]
    assert [p[0] for p in r.rutas[0][1]] == [1, 2, 3, 4]


def test_agregar_al_final():
    r = red_mini()
    assert r.agregar_parada("RUTA_A", "ZETA", "GAMMA")
    assert r.recorrido("RUTA_A")[-1] == "ZETA"


def test_agregar_casos_borde():
    r = red_mini()
    assert r.agregar_parada("NO_EXISTE", "ZETA", "ALFA") is False   # ruta inexistente
    assert r.agregar_parada("RUTA_A", "ZETA", "DELTA") is False     # despues_de no esta en la ruta
    assert r.agregar_parada("RUTA_A", "BETA", "ALFA") is False      # nueva ya esta
    assert r.agregar_parada("RUTA_A", "QUE_ES_ESTO", "ALFA") is False  # estacion inexistente
    r.cerrar("ZETA")
    assert r.agregar_parada("RUTA_A", "ZETA", "ALFA") is False      # nueva cerrada: se rechaza
    assert r.recorrido("RUTA_A") == ["ALFA", "BETA", "GAMMA"]       # nada cambio


def test_quitar_y_casos_borde():
    r = red_mini()
    assert r.quitar_parada("RUTA_A", "BETA") is True
    assert r.recorrido("RUTA_A") == ["ALFA", "GAMMA"]
    assert [p[0] for p in r.rutas[0][1]] == [1, 2]
    assert r.quitar_parada("RUTA_A", "BETA") is False               # ya no esta
    assert r.quitar_parada("NO_EXISTE", "ALFA") is False            # ruta inexistente


def test_normaliza_entrada():
    r = red_mini()
    assert r.agregar_parada(" ruta_a ", "zeta", "alfa") is True
    assert r.recorrido("ruta_a") == ["ALFA", "ZETA", "BETA", "GAMMA"]


def test_se_modifica_en_sitio():
    r = red_mini()
    lista_rutas = r.rutas
    r.quitar_parada("RUTA_A", "GAMMA")
    assert lista_rutas is r.rutas and len(r.rutas[0][1]) == 2


def test_datos_reales_ruta_1_1():
    if DATOS == "":
        return
    r = RedPrueba.desde_csv(DATOS)
    esperado = ["UNIVERSIDADES", "RECINTO FERIAL", "EL TIEMPO - MALOKA", "PORTAL ELDORADO"]
    assert r.recorrido("1-1") == esperado
    assert r.recorrido("1-1", al_reves=True) == esperado[::-1]


if __name__ == "__main__":
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_"):
            f()
            print("OK", nombre)
