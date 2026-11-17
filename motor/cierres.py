"""R8 - Estado compartido de estaciones cerradas.

`cerradas` es la lista de nombres (contrato) y se mantiene ORDENADA
alfabeticamente: consultar es busqueda binaria, O(log c). Nadie debe agregar
o quitar elementos por fuera de Red.cerrar / Red.reabrir.

Los demas requisitos (R1-R6) deben preguntar con Red._abierta(nombre).
"""
from ._comun import limite_inferior, buscar_binario


def abierta(cerradas, nombre):
    """True si `nombre` NO esta en cerradas. O(log c)."""
    return buscar_binario(cerradas, nombre) == -1


def aplicar_cerrar(cerradas, nombre):
    """Inserta `nombre` en su sitio ordenado. O(log c) + desplazamiento."""
    pos = limite_inferior(cerradas, nombre)
    if pos < len(cerradas) and cerradas[pos] == nombre:
        return
    cerradas.insert(pos, nombre)


def aplicar_reabrir(cerradas, nombre):
    """Quita `nombre` de cerradas si esta."""
    pos = buscar_binario(cerradas, nombre)
    if pos != -1:
        cerradas.pop(pos)


# Deshacer un cierre es reabrir, y deshacer una reapertura es cerrar.
revertir_cerrar = aplicar_reabrir
revertir_reabrir = aplicar_cerrar
