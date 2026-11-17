"""
Adaptador de integración del requisito R5.
Conecta los datos compartidos del motor con el algoritmo de viajes y entrega
el resultado en el formato del contrato:

    [(ruta, sube_en, baja_en)]                                  viaje directo
    [(ruta1, sube_en, transbordo), (ruta2, transbordo, baja_en)] con un transbordo
    []                                                           origen == destino
    None                                                         no hay viaje (o una estación no existe o está cerrada)
"""

from .viajes import IndiceViajes, _buscar


def ejecutar_r5(rutas, estaciones, cerradas, origen, destino):
    """
    Busca el recorrido con menos paradas y máximo un transbordo.
    """

    # Construimos el índice con los datos actuales de la red.
    indice = IndiceViajes(rutas, estaciones)

    # Ejecutamos nuestro algoritmo R5; además del resumen, devuelve los tramos
    # como [indice_ruta, posicion_subida, posicion_bajada].
    resultado, tramos = _buscar(rutas, estaciones, cerradas, origen, destino, indice, "paradas")

    # Sin viaje, estación inexistente o cerrada: None.
    if resultado is None or resultado[0] == "ERROR":
        return None

    # Misma estación: no hay que tomar ningún bus.
    if resultado[0] == "MISMO DESTINO":
        return []

    # Cada tramo: (ruta, estación donde se sube, estación donde se baja).
    viaje = []
    for r, desde, hasta in tramos:
        viaje.append((rutas[r][0], rutas[r][1][desde][1], rutas[r][1][hasta][1]))
    return viaje
