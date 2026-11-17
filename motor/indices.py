"""Indices PRIVADOS de R7/R8: tablas hash (la TablaHash del equipo, motor/tabla_hash.py).

  rutas:      id de ruta normalizado -> el objeto ruta [id, paradas]
  estaciones: nombre de estacion     -> True

Se arman UNA vez por red, en O(R) y O(E). Despues cada busqueda es O(1)
esperado, en vez de recorrer todas las rutas o todas las estaciones.

No duplican estado que cambie: las estaciones no cambian al operar y la tabla
de rutas guarda el MISMO objeto ruta que `Red.rutas`, asi que lo que R7 y R9
modifican en sitio se sigue viendo. Si `Red.rutas` / `Red.estaciones` se
reemplaza por otra lista o cambia de tamano, la tabla se rearma sola.

Atributos que se guardan en la Red (privados de este modulo):
  _idx_rutas, _idx_rutas_ref, _idx_rutas_n
  _idx_est,   _idx_est_ref,   _idx_est_n
"""
from ._comun import normalizar
from .tabla_hash import TablaHash # type: ignore


def tabla_rutas(red):
    """TablaHash id_normalizado -> ruta. O(R) la primera vez, O(1) despues."""
    rutas = red.rutas
    if (getattr(red, "_idx_rutas_ref", None) is not rutas
            or getattr(red, "_idx_rutas_n", -1) != len(rutas)):
        tabla = TablaHash(2 * len(rutas) + 16)
        for ruta in rutas:
            tabla.poner(normalizar(ruta[0]), ruta)
        red._idx_rutas = tabla
        red._idx_rutas_ref = rutas
        red._idx_rutas_n = len(rutas)
    return red._idx_rutas


def buscar_ruta(red, id_normalizado):
    """Devuelve la ruta [id, paradas] o None. O(1) esperado."""
    return tabla_rutas(red).obtener(id_normalizado)


def tabla_estaciones(red):
    """TablaHash nombre -> True. O(E) la primera vez, O(1) despues."""
    est = red.estaciones
    if (getattr(red, "_idx_est_ref", None) is not est
            or getattr(red, "_idx_est_n", -1) != len(est)):
        tabla = TablaHash(2 * len(est) + 16)
        for nombre in est:
            tabla.poner(nombre, True)
        red._idx_est = tabla
        red._idx_est_ref = est
        red._idx_est_n = len(est)
    return red._idx_est


def existe_estacion(red, nombre_normalizado):
    """True si la estacion existe. O(1) esperado."""
    return tabla_estaciones(red).obtener(nombre_normalizado) is not None
