"""R7 - Edicion de rutas: logica pura sobre la lista de paradas de UNA ruta.

Estructura (contrato): rutas = [[id, [[orden, nombre], ...]], ...]
Estas funciones reciben `paradas` (la lista interna de la ruta) y la modifican
EN SITIO, para que R5/R6 vean el cambio sin copias.
"""
from ._comun import buscar_posicion, insertar_parada, quitar_parada_en


def recorrido(paradas, al_reves=False):
    """Nombres de las paradas en orden (o invertidas). O(p)."""
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


def validar_agregar(paradas, nueva, despues_de):
    """True si despues_de esta en la ruta y nueva no. O(p)."""
    if buscar_posicion(paradas, despues_de) == -1:
        return False
    return buscar_posicion(paradas, nueva) == -1


def aplicar_agregar(paradas, nueva, despues_de):
    """Inserta `nueva` justo despues de `despues_de`. Devuelve la posicion."""
    pos = buscar_posicion(paradas, despues_de) + 1
    insertar_parada(paradas, pos, nueva)
    return pos


def aplicar_quitar(paradas, estacion):
    """Elimina `estacion`. Devuelve la posicion que tenia."""
    pos = buscar_posicion(paradas, estacion)
    quitar_parada_en(paradas, pos)
    return pos


def revertir_agregar(paradas, pos):
    quitar_parada_en(paradas, pos)


def revertir_quitar(paradas, nombre, pos):
    insertar_parada(paradas, pos, nombre)
