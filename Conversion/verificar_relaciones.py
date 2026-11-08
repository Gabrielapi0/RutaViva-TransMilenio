# Importamos CSV para poder leer los archivos generados.
import csv

# Importamos Path para localizar las carpetas de nuestro proyecto.
from pathlib import Path

# Identificamos la carpeta principal del proyecto Planeador_TransMilenio.
raiz = Path(__file__).resolve().parent.parent

# Indicamos dónde están los tres archivos CSV corregidos.
carpeta = raiz / "Datos_corregidos"

# Creamos un conjunto para guardar los nombres de las estaciones.
estaciones = set()

# Abrimos el archivo estaciones.csv en modo lectura.
with (carpeta / "estaciones.csv").open("r", encoding="utf-8-sig", newline="") as archivo:

    # Leemos las filas utilizando los nombres de las columnas.
    lector = csv.DictReader(archivo)

    # Recorremos todas las estaciones registradas.
    for fila in lector:

        # Guardamos el nombre de cada estación.
        estaciones.add(fila["nombre"])

# Creamos un contador para saber cuántas filas de rutas revisamos.
total = 0

# Creamos un contador para registrar las relaciones incorrectas.
errores = 0

# Abrimos el archivo rutas.csv.
with (carpeta / "rutas.csv").open("r", encoding="utf-8-sig", newline="") as archivo:

    # Leemos las filas utilizando los nombres de las columnas.
    lector = csv.DictReader(archivo)

    # Recorremos todas las paradas registradas en las rutas.
    for fila in lector:

        # Sumamos uno al contador de registros revisados.
        total += 1

        # Comprobamos si la estación de esta ruta existe en estaciones.csv.
        if fila["estacion"] not in estaciones:

            # Si no existe, aumentamos el contador de errores.
            errores += 1

            # Mostramos únicamente los primeros cinco errores encontrados.
            if errores <= 5:

                # Imprimimos la información de la estación no registrada.
                print("Estación no registrada:", fila)

# Mostramos cuántos registros de rutas fueron revisados.
print("Registros de rutas revisados:", total)

# Mostramos cuántas relaciones incorrectas encontramos.
print("Estaciones no registradas:", errores)

# Comprobamos si la cantidad de errores es cero.
if errores == 0:

    # Informamos que todas las estaciones de rutas.csv existen en estaciones.csv.
    print("VALIDACIÓN DE RELACIONES SUPERADA")

# Si encontramos errores, mostramos un mensaje diferente.
else:

    # Informamos que debemos revisar las relaciones incorrectas.
    print("VALIDACIÓN NO SUPERADA")