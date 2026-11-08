"""
Adaptador de integración del requisito R5.
Conecta los datos compartidos del motor con el algoritmo de viajes.
"""

from .viajes import IndiceViajes, buscar_mejor_viaje


def ejecutar_r5(rutas, estaciones, cerradas, origen, destino):
    """
    Busca el recorrido con menos tramos y máximo un transbordo.
    """

    # Construimos el índice con los datos actuales de la red.
    indice = IndiceViajes(rutas, estaciones)

    # Ejecutamos nuestro algoritmo R5.
    return buscar_mejor_viaje(
        rutas,
        estaciones,
        cerradas,
        origen,
        destino,
        indice=indice,
        criterio="paradas"
    )
