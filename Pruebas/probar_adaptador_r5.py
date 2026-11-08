"""
Prueba del adaptador R5 con modificaciones de recorridos.

No modifica los archivos CSV ni el motor original.
"""

import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))

from motor.integracion_r5 import ejecutar_r5
from motor.viajes import cargar_estaciones, cargar_rutas

# Cargamos nuestra red pequeña de pruebas.
carpeta = str(raiz / "Pruebas" / "Red_pequena")

estaciones = cargar_estaciones(carpeta)
rutas = cargar_rutas(carpeta)

# PRUEBA 1: La conexión original debe funcionar.
resultado_1 = ejecutar_r5(
    rutas, estaciones, [], "ALFA", "EPSILON"
)

assert resultado_1 == [
    "TRANSBORDO", "RUTA_A", "RUTA_B", "GAMMA", 4
]

print("PRUEBA 1 SUPERADA: viaje original")

# PRUEBA 2: Eliminamos GAMMA de RUTA_A.
for ruta in rutas:
    if ruta[0] == "RUTA_A":
        ruta[1] = [
            parada for parada in ruta[1]
            if parada[1] != "GAMMA"
        ]

resultado_2 = ejecutar_r5(
    rutas, estaciones, [], "ALFA", "EPSILON"
)

assert resultado_2 is None

print("PRUEBA 2 SUPERADA: modificación de ruta")

# PRUEBA 3: Restauramos las rutas desde el CSV.
rutas = cargar_rutas(carpeta)

resultado_3 = ejecutar_r5(
    rutas, estaciones, [], "ALFA", "EPSILON"
)

assert resultado_3 == [
    "TRANSBORDO", "RUTA_A", "RUTA_B", "GAMMA", 4
]

print("PRUEBA 3 SUPERADA: restauración de ruta")

print("\nADAPTADOR R5: TODAS LAS PRUEBAS SUPERADAS")