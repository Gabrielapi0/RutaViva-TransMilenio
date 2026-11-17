from _red_prueba import red_mini


def foto(r):
    """Copia del estado para comparar antes/despues."""
    return ([[x[0], [list(p) for p in x[1]]] for x in r.rutas], list(r.cerradas))


def test_secuencia_del_enunciado():
    r = red_mini()
    inicial = foto(r)
    r.cerrar("DELTA")
    r.agregar_parada("RUTA_A", "ZETA", "ALFA")
    final = foto(r)
    assert r.deshacer() is True
    assert r.deshacer() is True
    assert foto(r) == inicial                      # todo como estaba
    assert r.rehacer() is True
    assert r.rehacer() is True
    assert foto(r) == final                        # todo re-aplicado
    assert r.rehacer() is False                    # nada mas


def test_cambio_nuevo_borra_rehacer():
    r = red_mini()
    r.cerrar("DELTA")
    r.agregar_parada("RUTA_A", "ZETA", "ALFA")
    r.deshacer()
    r.cerrar("EPSILON")                            # cambio nuevo
    assert r.rehacer() is False
    assert r.cerradas == ["DELTA", "EPSILON"]


def test_pilas_vacias():
    r = red_mini()
    assert r.deshacer() is False
    assert r.rehacer() is False


def test_quitar_se_restaura_en_su_sitio():
    r = red_mini()
    antes = foto(r)
    r.quitar_parada("RUTA_A", "BETA")
    r.deshacer()
    assert foto(r) == antes
    assert r.recorrido("RUTA_A") == ["ALFA", "BETA", "GAMMA"]


def test_reabrir_deshacer():
    r = red_mini()
    r.cerrar("ALFA")
    r.cerrar("BETA")
    r.reabrir("ALFA")
    assert r.cerradas == ["BETA"]
    r.deshacer()
    assert r.cerradas == ["BETA", "ALFA"] or r.cerradas == ["ALFA", "BETA"]
    assert r._abierta("ALFA") is False


def test_mezcla_larga():
    r = red_mini()
    inicial = foto(r)
    r.cerrar("ZETA")
    r.quitar_parada("RUTA_B", "DELTA")
    r.agregar_parada("RUTA_B", "ALFA", "GAMMA")
    r.reabrir("ZETA")
    for _ in range(4):
        assert r.deshacer()
    assert foto(r) == inicial
    for _ in range(4):
        assert r.rehacer()
    assert r.recorrido("RUTA_B") == ["GAMMA", "ALFA", "EPSILON"]
    assert r._abierta("ZETA") is True


def test_version_sube_en_cada_cambio():
    r = red_mini()
    r.cerrar("ALFA")
    v1 = r._version
    r.deshacer()
    assert r._version == v1 + 1
    r.cerrar("NO_EXISTE")                          # rechazada: no cambia la version
    assert r._version == v1 + 1


if __name__ == "__main__":
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_"):
            f()
            print("OK", nombre)
