print("INICIANDO VALIDACIÓN DE SERVICIOS")
# Importamos la biblioteca para leer archivos CSV.
import csv

# Importamos Path para localizar nuestros archivos.
from pathlib import Path

# Ubicamos la carpeta principal del proyecto.
raiz = Path(__file__).resolve().parent.parent

# Ubicamos los archivos convertidos.
carpeta = raiz / "Datos_corregidos"

# Guardaremos aquí los identificadores de las rutas.
rutas = set()

# Abrimos el archivo de rutas.
with (carpeta / "rutas.csv").open(
    "r", encoding="utf-8-sig", newline=""
) as archivo:

    # Leemos el archivo por columnas.
    lector = csv.DictReader(archivo)

    # Recorremos cada parada.
    for fila in lector:

        # Guardamos el identificador de su ruta.
        rutas.add(fila["ruta"])

# Contadores para nuestra validación.
total = 0
errores = 0

# Abrimos el archivo de horarios.
with (carpeta / "horarios.csv").open(
    "r", encoding="utf-8-sig", newline=""
) as archivo:

    # Leemos cada registro de horarios.
    lector = csv.DictReader(archivo)

    # Recorremos todos los horarios.
    for fila in lector:

        # Contamos cada registro revisado.
        total += 1

        # Comprobamos si la ruta existe.
        if fila["ruta"] not in rutas:

            # Contamos los errores encontrados.
            errores += 1

            # Mostramos solamente los primeros cinco errores.
            if errores <= 5:
                print("Ruta no registrada:", fila)

# Mostramos los resultados.
print("Horarios revisados:", total)
print("Rutas no registradas:", errores)

# Informamos si la prueba fue superada.
if errores == 0:
    print("VALIDACIÓN DE SERVICIOS SUPERADA")
else:
    print("VALIDACIÓN NO SUPERADA")