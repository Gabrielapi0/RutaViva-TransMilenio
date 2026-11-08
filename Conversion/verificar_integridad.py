# Importamos CSV para leer los archivos.
import csv

# Importamos Path para localizar las carpetas.
from pathlib import Path

# Encontramos la carpeta principal del proyecto.
raiz = Path(__file__).resolve().parent.parent

# Ubicamos los archivos convertidos.
carpeta = raiz / "Datos_corregidos"

# Creamos un diccionario para guardar las estaciones de cada ruta.
rutas = {}

# Mostramos que comenzó la validación.
print("INICIANDO VALIDACIÓN DE INTEGRIDAD", flush=True)

# Abrimos el archivo de rutas.
with (carpeta / "rutas.csv").open(
    "r", encoding="utf-8-sig", newline=""
) as archivo:

    # Leemos cada fila del archivo.
    lector = csv.DictReader(archivo)

    # Recorremos las paradas de las rutas.
    for fila in lector:

        # Obtenemos el identificador de la ruta.
        ruta = fila["ruta"]

        # Obtenemos el nombre de la estación.
        estacion = fila["estacion"]

        # Si la ruta todavía no existe en el diccionario,
        # creamos un conjunto vacío para sus estaciones.
        if ruta not in rutas:
            rutas[ruta] = set()

        # Agregamos la estación a la ruta correspondiente.
        rutas[ruta].add(estacion)

# Creamos contadores para revisar los horarios.
total = 0
errores = 0

# Abrimos el archivo de horarios.
with (carpeta / "horarios.csv").open(
    "r", encoding="utf-8-sig", newline=""
) as archivo:

    # Leemos los horarios fila por fila.
    lector = csv.DictReader(archivo)

    # Recorremos todos los registros.
    for fila in lector:

        # Aumentamos el número de horarios revisados.
        total += 1

        # Obtenemos la ruta y la estación del horario.
        ruta = fila["ruta"]
        estacion = fila["estacion"]

        # Comprobamos que la ruta exista y que la estación
        # pertenezca a esa ruta.
        if ruta not in rutas or estacion not in rutas[ruta]:

            # Contamos la relación incorrecta.
            errores += 1

            # Mostramos únicamente los primeros cinco errores.
            if errores <= 5:
                print("Relación incorrecta:", fila)

# Mostramos los resultados.
print("Horarios revisados:", total)
print("Relaciones incorrectas:", errores)

# Informamos si la validación fue superada.
if errores == 0:
    print("VALIDACIÓN DE INTEGRIDAD SUPERADA")
else:
    print("VALIDACIÓN DE INTEGRIDAD NO SUPERADA")