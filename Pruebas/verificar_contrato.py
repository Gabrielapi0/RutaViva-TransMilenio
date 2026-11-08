# Verificación del contrato de integración de RutaViva.
# Este archivo solo consulta el código; no lo modifica.

import sys
from pathlib import Path
import importlib

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz))

print("VERIFICACIÓN DEL CONTRATO RUTAVIVA")
print("-" * 45)

# Comprobamos que el paquete motor exista.
motor = importlib.import_module("motor")

# El profesor exige estos dos nombres públicos.
tiene_red = hasattr(motor, "Red")
tiene_fila = hasattr(motor, "simular_fila")

print("Clase Red:", "DISPONIBLE" if tiene_red else "PENDIENTE")
print("Función simular_fila:", "DISPONIBLE" if tiene_fila else "PENDIENTE")

# Comprobamos que nuestro algoritmo R5 siga disponible.
viajes = importlib.import_module("motor.viajes")

tiene_r5 = hasattr(viajes, "buscar_mejor_viaje")
tiene_indice = hasattr(viajes, "IndiceViajes")

print("Algoritmo R5:", "DISPONIBLE" if tiene_r5 else "PENDIENTE")
print("Índice de viajes:", "DISPONIBLE" if tiene_indice else "PENDIENTE")

# Si el integrante 1 ya incorporó Red, revisamos sus métodos.
if tiene_red:
    metodos = [
        "estado",
        "autocompletar",
        "rango",
        "proximo_bus",
        "viaje",
        "ranking",
        "agregar_parada",
        "quitar_parada",
        "recorrido",
        "cerrar",
        "reabrir",
        "deshacer",
        "rehacer"
    ]

    for nombre in metodos:
        existe = callable(getattr(motor.Red, nombre, None))
        print(nombre + ":", "DISPONIBLE" if existe else "PENDIENTE")

print("-" * 45)
print("VERIFICACIÓN FINALIZADA")