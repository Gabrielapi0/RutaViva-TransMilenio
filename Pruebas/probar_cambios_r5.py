import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))

from Motor.viajes import (
    cargar_estaciones,
    cargar_rutas,
    IndiceViajes,
    buscar_mejor_viaje
)

carpeta = str(raiz / "Pruebas" / "Red_pequena")

estaciones = cargar_estaciones(carpeta)
rutas = cargar_rutas(carpeta)

# Estado inicial de la red.
indice = IndiceViajes(rutas, estaciones)

antes = buscar_mejor_viaje(
    rutas, estaciones, [],
    "ALFA", "EPSILON",
    indice=indice,
    criterio="paradas"
)

print("ANTES DEL CAMBIO:", antes)

# Simulamos que el integrante 4 modifica RUTA_A,
# eliminando GAMMA de su recorrido.
for ruta in rutas:
    if ruta[0] == "RUTA_A":
        ruta[1] = [
            parada for parada in ruta[1]
            if parada[1] != "GAMMA"
        ]

# Reconstruimos el índice después de la modificación.
indice = IndiceViajes(rutas, estaciones)

despues = buscar_mejor_viaje(
    rutas, estaciones, [],
    "ALFA", "EPSILON",
    indice=indice,
    criterio="paradas"
)

print("DESPUÉS DEL CAMBIO:", despues)

assert antes == [
    "TRANSBORDO", "RUTA_A", "RUTA_B", "GAMMA", 4
]

assert despues is None

print("\nPRUEBA DE MODIFICACIÓN DE RUTA SUPERADA.")