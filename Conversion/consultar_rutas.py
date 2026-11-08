# Importamos csv para poder leer los archivos de datos.
import csv

# Importamos Path para localizar las carpetas del proyecto.
from pathlib import Path

# Buscamos la carpeta principal Planeador_TransMilenio.
carpeta_proyecto = Path(__file__).resolve().parent.parent

# Construimos la ubicación del archivo rutas.csv.
archivo = carpeta_proyecto / "Datos" / "rutas.csv"

# Guardamos el nombre de la ruta que queremos consultar.
ruta_buscada = "1-1"

# Creamos una lista vacía donde guardaremos las estaciones encontradas.
estaciones_ruta = []

# Abrimos el archivo rutas.csv para consultar su información.
with open(archivo, "r", encoding="utf-8-sig", newline="") as f:

    # Leemos el archivo utilizando los nombres de las columnas.
    lector = csv.DictReader(f)

    # Recorremos cada fila del archivo rutas.csv.
    for fila in lector:

        # Comprobamos si la ruta de esta fila es la que estamos buscando.
        if fila["ruta"] == ruta_buscada:

            # Guardamos el orden de la parada como un número entero.
            orden = int(fila["orden"])

            # Guardamos el nombre de la estación.
            estacion = fila["estacion"]

            # Agregamos el orden y el nombre de la estación a nuestra lista.
            estaciones_ruta.append((orden, estacion))

# Ordenamos las paradas utilizando su posición dentro del recorrido.
# Esta prueba está fuera de motor/, donde el profesor sí permite usar sort().
estaciones_ruta.sort()

# Mostramos un título para identificar la ruta consultada.
print("RECORRIDO DE LA RUTA:", ruta_buscada)

# Recorremos las estaciones que encontramos.
for orden, estacion in estaciones_ruta:

    # Mostramos el número de parada y su nombre.
    print(orden, "-", estacion)