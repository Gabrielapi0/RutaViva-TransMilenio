import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))

from motor.viajes import IndiceViajes, buscar_mejor_viaje

estaciones = ["ALFA", "BETA", "GAMMA", "DELTA"]

# La ruta visita BETA dos veces.
rutas = [
    [
        "RUTA_CIRCULAR",
        [
            [1, "ALFA"],
            [2, "BETA"],
            [3, "GAMMA"],
            [4, "BETA"],
            [5, "DELTA"]
        ]
    ]
]

indice = IndiceViajes(rutas, estaciones)

resultado = buscar_mejor_viaje(
    rutas,
    estaciones,
    [],
    "BETA",
    "DELTA",
    indice=indice,
    criterio="paradas"
)

print("RESULTADO:", resultado)

# Desde la segunda aparición de BETA
# hasta DELTA hay solamente un tramo.
esperado = [
    "DIRECTO",
    "RUTA_CIRCULAR",
    None,
    None,
    1
]

assert resultado == esperado, (
    "ERROR: No se seleccionó la aparición "
    "más conveniente de BETA."
)

print("PRUEBA DE ESTACIONES REPETIDAS SUPERADA.")