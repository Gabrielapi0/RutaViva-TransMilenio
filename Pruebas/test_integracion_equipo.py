"""
Pruebas de integración de RutaViva.

Estas pruebas se ejecutarán cuando estén disponibles
las implementaciones reales de Red, R7, R8 y R9.
"""

from pathlib import Path
import sys

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))


def probar_integracion():
    try:
        from Pruebas import Red
    except ImportError:
        print("PENDIENTE: el integrante 1 debe integrar la clase Red.")
        return

    carpeta = str(raiz / "Pruebas" / "Red_pequena")
    red = Red(carpeta)

    # Comprobamos que la red inicialmente permita viajar.
    assert red.viaje("ALFA", "EPSILON") is not None
    print("OK: viaje inicial")

    # Cerramos el punto de transbordo.
    red.cerrar("GAMMA")
    assert red.viaje("ALFA", "EPSILON") is None
    print("OK: cierre de estación")

    # Reabrimos la estación.
    red.reabrir("GAMMA")
    assert red.viaje("ALFA", "EPSILON") is not None
    print("OK: reapertura de estación")

    # Eliminamos GAMMA de la primera ruta.
    red.quitar_parada("RUTA_A", "GAMMA")
    assert red.viaje("ALFA", "EPSILON") is None
    print("OK: modificación de ruta")

    # Deshacemos la modificación.
    red.deshacer()
    assert red.viaje("ALFA", "EPSILON") is not None
    print("OK: deshacer modificación")

    print("\nPRUEBAS DE INTEGRACIÓN SUPERADAS")


if __name__ == "__main__":
    probar_integracion()