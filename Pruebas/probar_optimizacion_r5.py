import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))

from motor.viajes import IndiceViajes, buscar_mejor_viaje

estaciones = [
    "ALFA", "BETA", "GAMMA",
    "DELTA", "EPSILON"
]

rutas = [
    [
        "RUTA_LARGA",
        [
            [1, "ALFA"],
            [2, "BETA"],
            [3, "GAMMA"],
            [4, "DELTA"],
            [5, "EPSILON"]
        ]
    ],
    [
        "RUTA_CORTA_1",
        [
            [1, "ALFA"],
            [2, "GAMMA"]
        ]
    ],
    [
        "RUTA_CORTA_2",
        [
            [1, "GAMMA"],
            [2, "EPSILON"]
        ]
    ]
]

indice = IndiceViajes(rutas, estaciones)

resultado = buscar_mejor_viaje(
    rutas,
    estaciones,
    [],
    "ALFA",
    "EPSILON",
    indice=indice,
    criterio="paradas"
)

print("RESULTADO:", resultado)

esperado = [
    "TRANSBORDO",
    "RUTA_CORTA_1",
    "RUTA_CORTA_2",
    "GAMMA",
    2
]

assert resultado == esperado, (
    "ERROR: R5 no seleccionó el recorrido "
    "con la menor cantidad de tramos."
)

print("PRUEBA DE OPTIMIZACIÓN SUPERADA.")