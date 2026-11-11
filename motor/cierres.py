"""R8 - Estado compartido de estaciones cerradas.

`cerradas` es la lista de nombres (contrato). Los demas requisitos
(R1, R2, R3, R4, R5, R6) deben preguntar con `abierta(cerradas, nombre)`
o con el metodo Red._abierta(nombre).
"""


def abierta(cerradas, nombre):
    """True si `nombre` NO esta en la lista de cerradas. O(c)."""
    for c in cerradas:
        if c == nombre:
            return False
    return True


def posicion_cerrada(cerradas, nombre):
    """Indice de `nombre` en cerradas, o -1."""
    for i in range(len(cerradas)):
        if cerradas[i] == nombre:
            return i
    return -1


def aplicar_cerrar(cerradas, nombre):
    cerradas.append(nombre)


def revertir_cerrar(cerradas, nombre):
    pos = posicion_cerrada(cerradas, nombre)
    if pos != -1:
        cerradas.pop(pos)


def aplicar_reabrir(cerradas, nombre):
    """Quita `nombre` de cerradas. Devuelve la posicion que tenia."""
    pos = posicion_cerrada(cerradas, nombre)
    cerradas.pop(pos)
    return pos


def revertir_reabrir(cerradas, nombre, pos):
    cerradas.insert(pos, nombre)
