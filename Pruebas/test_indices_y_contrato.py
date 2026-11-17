from _red_prueba import red_mini, RedPrueba


def test_retornos_son_booleanos_y_listas():
    r = red_mini()
    for valor in [r.agregar_parada("RUTA_A", "ZETA", "ALFA"), r.quitar_parada("RUTA_A", "ZETA"),
                  r.cerrar("ALFA"), r.reabrir("ALFA"), r.deshacer(), r.rehacer(),
                  r.cerrar("NO_EXISTE"), r.reabrir("ALFA"), r.agregar_parada("X", "A", "B")]:
        assert valor is True or valor is False
    assert isinstance(r.recorrido("RUTA_A"), list) and r.recorrido("X") == []


def test_estaciones_sin_ordenar():
    r = RedPrueba(["ZETA", "ALFA", "MU", "BETA"], [["R", [[1, "ALFA"], [2, "BETA"]]]])
    assert r.cerrar("MU") and r.cerrar("ZETA") and r.cerrar("ALFA")
    assert r.cerradas == ["ALFA", "MU", "ZETA"]       # cerradas siempre ordenada
    assert r.agregar_parada("R", "MU", "ALFA") is False  # cerrada
    assert r.reabrir("MU") and r.agregar_parada("R", "MU", "ALFA")
    assert r.recorrido("R") == ["ALFA", "MU", "BETA"]


def test_cerradas_siempre_ordenada_con_deshacer_y_rehacer():
    r = RedPrueba(["C", "A", "E", "B", "D"], [])
    for n in ["C", "A", "E", "B"]:
        r.cerrar(n)
    r.reabrir("A")
    r.reabrir("E")
    for _ in range(3):
        r.deshacer()
    assert r.cerradas == ["A", "C", "E"]
    r.rehacer()
    r.rehacer()
    assert r.cerradas == ["B", "C", "E"]
    assert r._abierta("A") and r._abierta("D")
    assert not r._abierta("B") and not r._abierta("C") and not r._abierta("E")


def test_indice_de_rutas_se_actualiza_si_cambia_la_lista():
    r = red_mini()
    assert r.recorrido("RUTA_C") == []
    r.rutas.append(["RUTA_C", [[1, "ZETA"], [2, "ALFA"]]])
    assert r.recorrido("RUTA_C") == ["ZETA", "ALFA"]
    assert r.quitar_parada("RUTA_C", "ZETA") is True


def test_rutas_desordenadas_y_ids_como_en_csv():
    r = RedPrueba(["A", "B", "C"], [["10-2", [[1, "A"], [2, "B"]]],
                                    ["1-1", [[1, "B"], [2, "C"]]],
                                    ["B7", [[1, "A"], [2, "C"]]]])
    assert r.recorrido("1-1") == ["B", "C"]
    assert r.recorrido("10-2", True) == ["B", "A"]
    assert r.recorrido("b7") == ["A", "C"]
    assert r.recorrido("1-2") == []


def test_ene_no_se_cambia():
    r = RedPrueba(["ESPAÑA", "NORTE"], [["R", [[1, "NORTE"]]]])
    assert r.cerrar("españa") is True and r.cerradas == ["ESPAÑA"]
    assert r.agregar_parada("R", "ESPAÑA", "NORTE") is False


def test_cerradas_y_rutas_son_las_mismas_listas_que_ve_r5():
    r = red_mini()
    rutas, cerradas = r.rutas, r.cerradas
    r.cerrar("ALFA")
    r.agregar_parada("RUTA_A", "ZETA", "ALFA")
    r.deshacer()
    r.rehacer()
    assert rutas is r.rutas and cerradas is r.cerradas
    assert cerradas == ["ALFA"] and rutas[0][1][1] == [2, "ZETA"]


def test_tabla_hash_con_colisiones_encuentra_todo():
    from motor import indices
    rutas = []
    for i in range(500):
        rutas.append(["%d-%d" % (i // 4 + 1, i % 4 + 1), [[1, "A"], [2, "B"]]])
    r = RedPrueba(["A", "B"], rutas)
    tabla = indices.tabla_rutas(r)
    assert len(tabla) == 500
    assert any(len(c) > 1 for c in tabla._cubetas)        # hubo colisiones
    for ruta in rutas:
        assert indices.buscar_ruta(r, ruta[0]) is ruta       # y todas se encuentran
    assert indices.buscar_ruta(r, "999-9") is None
    assert r.recorrido("125-4") == ["A", "B"]


def test_tabla_de_estaciones():
    from motor import indices
    r = RedPrueba(["ZETA", "ALFA", "ESPAÑA"], [])
    assert indices.existe_estacion(r, "ALFA") and indices.existe_estacion(r, "ESPAÑA")
    assert not indices.existe_estacion(r, "BETA")
    r.estaciones.append("BETA")                      # cambio de tamano -> se rearma
    assert indices.existe_estacion(r, "BETA")


def test_sin_rutas():
    r = RedPrueba(["A"], [])
    assert r.recorrido("X") == [] and r.agregar_parada("X", "A", "A") is False


def test_datos_reales():
    import os
    d = os.environ.get("DATOS_RUTAVIVA", "")
    if d == "":
        return
    r = RedPrueba.desde_csv(d)
    assert len(r.estaciones) == 147 and len(r.rutas) == 181
    esperado = ["UNIVERSIDADES", "RECINTO FERIAL", "EL TIEMPO - MALOKA", "PORTAL ELDORADO"]
    assert r.recorrido("1-1") == esperado and r.recorrido("1-1", al_reves=True) == esperado[::-1]
    assert r.cerrar("CALLE 26") and not r._abierta("CALLE 26") and r.cerrar("CALLE 26") is False


if __name__ == "__main__":
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_"):
            f()
            print("OK", nombre)
