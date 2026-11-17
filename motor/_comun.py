"""Auxiliares compartidos por R7, R8 y R9 (Integrante 4).

Solo usa listas, ciclos for/while y metodos de str. Nada prohibido en motor/.
"""

_CON_ACENTO = "ÁÉÍÓÚÜÑ"
_SIN_ACENTO = "AEIOUUN"


def normalizar(texto):
    """Devuelve el texto en MAYUSCULAS, sin tildes y sin espacios sobrantes.

    Entrada: str. Salida: str, o None si la entrada no es str.
    """
    if not isinstance(texto, str):
        return None
    t = texto.strip().upper()
    for i in range(len(_CON_ACENTO)):
        t = t.replace(_CON_ACENTO[i], _SIN_ACENTO[i])
    return t


# Cache de la tabla hash de rutas: [lista de rutas para la que se armó, tabla].
_CACHE_RUTAS = [None, None]


def buscar_ruta(rutas, id_ruta):
    """Devuelve la ruta [id, paradas] cuyo id coincide, o None.
    Usa una tabla hash propia (id -> ruta) que se arma una sola vez por red,
    en O(R); después cada búsqueda es O(1) esperado. La tabla guarda la misma
    lista de paradas de cada ruta, así que ve los cambios de R7 en sitio."""
    if _CACHE_RUTAS[0] is not rutas:
        from .tabla_hash import TablaHash
        tabla = TablaHash(2 * len(rutas) + 16)
        for ruta in rutas:
            tabla.poner(normalizar(ruta[0]), ruta)
        _CACHE_RUTAS[0] = rutas
        _CACHE_RUTAS[1] = tabla
    return _CACHE_RUTAS[1].obtener(id_ruta)


def buscar_posicion(paradas, nombre):
    """Indice (desde 0) de la parada con ese nombre, o -1. O(n)."""
    for i in range(len(paradas)):
        if paradas[i][1] == nombre:
            return i
    return -1


def renumerar(paradas):
    """Reasigna orden 1..n para que la ruta quede coherente. O(n)."""
    for i in range(len(paradas)):
        paradas[i][0] = i + 1


def insertar_parada(paradas, pos, nombre):
    """Inserta [orden, nombre] en la posicion pos (0-based) y renumera."""
    paradas.insert(pos, [0, nombre])
    renumerar(paradas)


def quitar_parada_en(paradas, pos):
    """Elimina la parada en la posicion pos (0-based) y renumera."""
    paradas.pop(pos)
    renumerar(paradas)
