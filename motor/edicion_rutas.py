"""R7 - Edicion de rutas: logica pura sobre la lista `rutas` compartida.

Estructura (contrato): rutas = [[id, [[orden, nombre], ...]], ...]
Las modificaciones se hacen EN SITIO para que R5/R6 vean el cambio.
"""
from ._comun import (buscar_ruta, buscar_posicion, insertar_parada,
                     quitar_parada_en)


def recorrido(rutas, id_ruta, al_reves=False):
    """Nombres de las paradas de la ruta en orden (o invertidas).

    Ruta inexistente -> []. Complejidad O(R + n).
    """
    ruta = buscar_ruta(rutas, id_ruta)
    if ruta is None:
        return []
    paradas = ruta[1]
    resultado = []
    if al_reves:
        i = len(paradas) - 1
        while i >= 0:
            resultado.append(paradas[i][1])
            i -= 1
    else:
        for p in paradas:
            resultado.append(p[1])
    return resultado


def validar_agregar(rutas, id_ruta, nueva, despues_de):
    """True si la insercion es valida (ruta existe, despues_de esta, nueva no)."""
    ruta = buscar_ruta(rutas, id_ruta)
    if ruta is None:
        return False
    if buscar_posicion(ruta[1], despues_de) == -1:
        return False
    if buscar_posicion(ruta[1], nueva) != -1:
        return False
    return True


def aplicar_agregar(rutas, id_ruta, nueva, despues_de):
    """Inserta `nueva` justo despues de `despues_de`. Devuelve la posicion."""
    paradas = buscar_ruta(rutas, id_ruta)[1]
    pos = buscar_posicion(paradas, despues_de) + 1
    insertar_parada(paradas, pos, nueva)
    return pos


def aplicar_quitar(rutas, id_ruta, estacion):
    """Elimina `estacion` de la ruta. Devuelve la posicion que tenia."""
    paradas = buscar_ruta(rutas, id_ruta)[1]
    pos = buscar_posicion(paradas, estacion)
    quitar_parada_en(paradas, pos)
    return pos


def revertir_agregar(rutas, id_ruta, pos):
    """Deshace aplicar_agregar quitando la parada de la posicion pos."""
    quitar_parada_en(buscar_ruta(rutas, id_ruta)[1], pos)


def revertir_quitar(rutas, id_ruta, nombre, pos):
    """Deshace aplicar_quitar reponiendo la parada en su sitio original."""
    insertar_parada(buscar_ruta(rutas, id_ruta)[1], pos, nombre)
