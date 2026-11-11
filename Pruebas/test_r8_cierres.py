from _red_prueba import red_mini


def test_cerrar_y_abierta():
    r = red_mini()
    assert r._abierta("GAMMA") is True
    assert r.cerrar("GAMMA") is True
    assert r._abierta("GAMMA") is False
    assert r.cerradas == ["GAMMA"]


def test_cerrar_dos_veces():
    r = red_mini()
    r.cerrar("GAMMA")
    assert r.cerrar("GAMMA") is False
    assert r.cerradas == ["GAMMA"]          # sin duplicados


def test_reabrir():
    r = red_mini()
    r.cerrar("GAMMA")
    assert r.reabrir("GAMMA") is True
    assert r._abierta("GAMMA") is True
    assert r.cerradas == []


def test_reabrir_algo_abierto():
    assert red_mini().reabrir("GAMMA") is False


def test_nombre_inexistente():
    r = red_mini()
    assert r.cerrar("NO_EXISTE") is False
    assert r.reabrir("NO_EXISTE") is False
    assert r.cerradas == []


def test_cerrar_no_toca_las_rutas():
    r = red_mini()
    r.cerrar("GAMMA")
    assert r.recorrido("RUTA_A") == ["ALFA", "BETA", "GAMMA"]


def test_cierres_en_historial_no_se_registran_si_fallan():
    r = red_mini()
    r.cerrar("NO_EXISTE")
    assert r.deshacer() is False


if __name__ == "__main__":
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_"):
            f()
            print("OK", nombre)
