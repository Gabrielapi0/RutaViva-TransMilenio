# Importamos sys para localizar los módulos del proyecto.
import sys

# Importamos Path para trabajar con las carpetas.
from pathlib import Path

# Identificamos la carpeta principal de RutaViva.
raiz = Path(__file__).resolve().parent.parent

# Agregamos la carpeta principal a las rutas de Python.
sys.path.insert(0, str(raiz))

# Importamos las funciones que ya construimos en el motor.
from Motor.viajes import (
    cargar_estaciones,
    cargar_rutas,
    buscar_mejor_viaje,
)

# Indicamos qué carpeta de datos queremos probar.
carpeta = "Datos_corregidos"

# Mostramos un mensaje de inicio.
print("INICIANDO PRUEBA DEL MOTOR", flush=True)

# Cargamos las estaciones utilizando nuestro motor.
estaciones = cargar_estaciones(carpeta)

# Mostramos cuántas estaciones se cargaron.
print("Estaciones cargadas:", len(estaciones), flush=True)

# Cargamos los recorridos utilizando nuestro motor.
rutas = cargar_rutas(carpeta)

# Mostramos cuántos recorridos se cargaron.
print("Recorridos cargados:", len(rutas), flush=True)

# Informamos que terminó la prueba.
print("PRUEBA DE CARGA FINALIZADA")

# Mostramos que comenzará la prueba de búsqueda.
print("\nINICIANDO PRUEBA DE BÚSQUEDA", flush=True)

# Seleccionamos una ruta que tenga al menos dos estaciones diferentes.
ruta_prueba = None

for ruta in rutas:

    # Cada ruta contiene su identificador y una lista de paradas.
    paradas = ruta[1]

    # Comprobamos que tenga al menos dos paradas.
    if len(paradas) >= 2:

        # Obtenemos la primera y la última estación.
        primera = paradas[0][1]
        ultima = paradas[-1][1]

        # Nos aseguramos de que sean estaciones diferentes.
        if primera != ultima:
            ruta_prueba = ruta
            break

# Comprobamos que encontramos una ruta adecuada.
if ruta_prueba is not None:

    # Elegimos el origen y destino de nuestra prueba.
    origen = ruta_prueba[1][0][1]
    destino = ruta_prueba[1][-1][1]

    # Mostramos las estaciones seleccionadas.
    print("Origen:", origen)
    print("Destino:", destino)

    # No cerramos ninguna estación durante la prueba.
    cerradas = []

    # Ejecutamos nuestro algoritmo R5.
    resultado = buscar_mejor_viaje(
        rutas,
        estaciones,
        cerradas,
        origen,
        destino,
        criterio="paradas"
    )

    # Mostramos el resultado obtenido.
    print("Resultado:", resultado)

else:

    # Informamos si no encontramos una ruta adecuada.
    print("No encontramos una ruta para realizar la prueba.")
    # Avisamos que comienza la prueba.
print("\nINICIANDO PRUEBA DE BÚSQUEDA", flush=True)

# Buscamos un recorrido con al menos dos estaciones diferentes.
ruta_prueba = None

for ruta in rutas:

    paradas = ruta[1]

    if len(paradas) >= 2:

        primera = paradas[0][1]
        ultima = paradas[-1][1]

        if primera != ultima:
            ruta_prueba = ruta
            break

# Si encontramos un recorrido, probamos el algoritmo.
if ruta_prueba is not None:

    origen = ruta_prueba[1][0][1]
    destino = ruta_prueba[1][-1][1]

    print("Origen:", origen)
    print("Destino:", destino)

    # Ejecutamos R5 sin estaciones cerradas.
    resultado = buscar_mejor_viaje(
        rutas,
        estaciones,
        [],
        origen,
        destino,
        criterio="paradas"
    )

    print("Resultado:", resultado)

else:
    print("No encontramos un recorrido adecuado.")

    # ---------------------------------------------
# PRUEBA DE UN VIAJE CON TRANSBORDO
# ---------------------------------------------

# Avisamos que comienza la prueba.
print("\nBUSCANDO UN VIAJE CON TRANSBORDO", flush=True)

# Guardamos las estaciones que ya hemos revisado.
revisadas = set()

# Indicamos si encontramos un viaje con transbordo.
encontrado = False

# Recorremos los servicios disponibles.
for ruta in rutas:

    # Obtenemos las paradas del servicio.
    paradas = ruta[1]

    # Tomamos la primera estación como posible origen.
    if len(paradas) < 2:
        continue

    origen_prueba = paradas[0][1]

    # Evitamos repetir el mismo origen.
    if origen_prueba in revisadas:
        continue

    revisadas.add(origen_prueba)

    # Probamos varios destinos de otros recorridos.
    for otra_ruta in rutas[:30]:

        # Comprobamos que tenga paradas.
        if len(otra_ruta[1]) < 2:
            continue

        # Elegimos su última estación como destino.
        destino_prueba = otra_ruta[1][-1][1]

        # Evitamos buscar un viaje al mismo lugar.
        if origen_prueba == destino_prueba:
            continue

        # Ejecutamos el algoritmo R5.
        resultado = buscar_mejor_viaje(
            rutas,
            estaciones,
            [],
            origen_prueba,
            destino_prueba,
            criterio="paradas"
        )

        # Revisamos si encontró un transbordo.
        if resultado[0] == "TRANSBORDO":

            # Mostramos las estaciones elegidas.
            print("Origen:", origen_prueba)
            print("Destino:", destino_prueba)

            # Mostramos el itinerario.
            print("Resultado:", resultado)

            # Indicamos que encontramos el caso.
            encontrado = True
            break

    # Terminamos cuando encontramos un transbordo.
    if encontrado:
        break

# Si no encontramos el caso, informamos el resultado.
if not encontrado:
    print("No se encontró un transbordo en las combinaciones probadas.")