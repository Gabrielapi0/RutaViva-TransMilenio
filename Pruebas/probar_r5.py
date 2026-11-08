# Importamos sys para localizar el motor del proyecto.
import sys

# Importamos Path para trabajar con las carpetas.
from pathlib import Path

# Encontramos la carpeta principal de RutaViva.
raiz = Path(__file__).resolve().parent.parent

# Permitimos que Python encuentre el módulo Motor.
sys.path.insert(0, str(raiz))

# Importamos las funciones que ya desarrollamos.
from motor.viajes import (
    cargar_estaciones,
    cargar_rutas,
    buscar_mejor_viaje,
    IndiceViajes
)

# Ubicamos nuestra red pequeña.
carpeta = str(raiz / "Pruebas" / "Red_pequena")

# Cargamos las estaciones y los recorridos.
estaciones = cargar_estaciones(carpeta)
rutas = cargar_rutas(carpeta)

# Construimos el índice para facilitar las búsquedas.
indice = IndiceViajes(rutas, estaciones)

# Mostramos que comenzó la prueba.
print("INICIANDO PRUEBAS DE R5")

# Definimos los casos que vamos a comprobar.
pruebas = [
    ("ALFA", "GAMMA", []),
    ("ALFA", "EPSILON", []),
    ("ALFA", "ALFA", []),
    ("ALFA", "ESTACION INVENTADA", []),
    ("ALFA", "EPSILON", ["GAMMA"])
]

# Recorremos los casos de prueba.
for origen, destino, cerradas in pruebas:

    # Mostramos el viaje que queremos consultar.
    print("\nOrigen:", origen)
    print("Destino:", destino)
    print("Estaciones cerradas:", cerradas)

    # Ejecutamos el algoritmo R5.
    resultado = buscar_mejor_viaje(
        rutas,
        estaciones,
        cerradas,
        origen,
        destino,
        indice=indice,
        criterio="paradas"
    )

    # Mostramos la respuesta.
    print("Resultado:", resultado)

# Avisamos que terminaron las pruebas.
print("\nPRUEBAS FINALIZADAS")