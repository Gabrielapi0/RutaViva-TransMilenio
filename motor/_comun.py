"""Auxiliares compartidos por R7, R8 y R9 (Integrante 4).

Solo usa listas, ciclos for/while y metodos de str. Nada prohibido en motor/.
"""

_CON_ACENTO = "ÁÉÍÓÚÜ"
_SIN_ACENTO = "AEIOUU"


def normalizar(texto):
    """Texto en MAYUSCULAS, sin tildes y sin espacios sobrantes.

    No toca la letra Ñ: los nombres deben quedar como vienen en los CSV.
    Entrada: str. Salida: str, o None si la entrada no es str.
    """
    if not isinstance(texto, str):
        return None
    t = texto.strip().upper()
    for i in range(len(_CON_ACENTO)):
        t = t.replace(_CON_ACENTO[i], _SIN_ACENTO[i])
    return t


def _clave(x, por_clave):
    if por_clave:
        return x[0]
    return x


def limite_inferior(lista, clave, por_clave=False):
    """Primera posicion cuyo valor es >= clave (busqueda binaria, O(log n))."""
    lo = 0
    hi = len(lista)
    while lo < hi:
        medio = (lo + hi) // 2
        if _clave(lista[medio], por_clave) < clave:
            lo = medio + 1
        else:
            hi = medio
    return lo


def buscar_binario(lista, clave, por_clave=False):
    """Posicion exacta de `clave` en una lista ordenada, o -1. O(log n)."""
    pos = limite_inferior(lista, clave, por_clave)
    if pos < len(lista) and _clave(lista[pos], por_clave) == clave:
        return pos
    return -1


def buscar_posicion(paradas, nombre):
    """Indice (desde 0) de la parada con ese nombre, o -1. O(p)."""
    for i in range(len(paradas)):
        if paradas[i][1] == nombre:
            return i
    return -1


def renumerar(paradas, desde=0):
    """Reasigna orden = posicion + 1 desde `desde`. O(p - desde)."""
    for i in range(desde, len(paradas)):
        paradas[i][0] = i + 1


def insertar_parada(paradas, pos, nombre):
    """Inserta [orden, nombre] en la posicion pos (0-based) y renumera."""
    paradas.insert(pos, [pos + 1, nombre])
    renumerar(paradas, pos + 1)


def quitar_parada_en(paradas, pos):
    """Elimina la parada en la posicion pos (0-based) y renumera."""
    paradas.pop(pos)
    renumerar(paradas, pos)
