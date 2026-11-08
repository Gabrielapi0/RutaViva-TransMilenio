# PRUEBA DE INTEGRACIÓN R5
# Este archivo no modifica el motor original.

import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))

from Motor.viajes import (
    cargar_estaciones,
    cargar_rutas,
    IndiceViajes,
    buscar_mejor_viaje,
)


class RedDePrueba:
    """
    Simula únicamente la parte de la clase Red
    que necesita nuestro algoritmo R5.

    No reemplaza la clase Red oficial del grupo.
    """

    def __init__(self, carpeta):
        self.estaciones = cargar_estaciones(carpeta)
        self.rutas = cargar_rutas(carpeta)
        self.cerradas = []
        self.indice_viajes = IndiceViajes(
            self.rutas,
            self.estaciones
        )

    def viaje(self, origen, destino):
        return buscar_mejor_viaje(
            self.rutas,
            self.estaciones,
            self.cerradas,
            origen,
            destino,
            indice=self.indice_viajes,
            criterio="paradas"
        )


# Creamos una red utilizando los CSV pequeños.
carpeta = str(raiz / "Pruebas" / "Red_pequena")
red = RedDePrueba(carpeta)

# Primera prueba: viaje directo.
resultado_directo = red.viaje("ALFA", "GAMMA")

print("PRUEBA 1: VIAJE DIRECTO")
print(resultado_directo)

assert resultado_directo == [
    "DIRECTO", "RUTA_A", None, None, 2
]

# Segunda prueba: viaje con transbordo.
resultado_transbordo = red.viaje("ALFA", "EPSILON")

print("\nPRUEBA 2: TRANSBORDO")
print(resultado_transbordo)

assert resultado_transbordo == [
    "TRANSBORDO", "RUTA_A", "RUTA_B", "GAMMA", 4
]

# Tercera prueba: estación cerrada.
red.cerradas.append("GAMMA")

resultado_cierre = red.viaje("ALFA", "EPSILON")

print("\nPRUEBA 3: ESTACIÓN CERRADA")
print(resultado_cierre)

assert resultado_cierre is None

print("\nLAS TRES PRUEBAS DE INTEGRACIÓN PASARON.")