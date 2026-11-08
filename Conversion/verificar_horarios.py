# Mostramos un mensaje para comprobar que el programa se ejecuta.
print("INICIANDO VALIDACIÓN DE HORARIOS")
# Importamos CSV para leer los horarios.
import csv

# Importamos Path para localizar el archivo.
from pathlib import Path

# Identificamos la carpeta principal del proyecto.
raiz = Path(__file__).resolve().parent.parent

# Construimos la ruta al archivo de horarios corregido.
archivo = raiz / "Datos_corregidos" / "horarios.csv"

# Contamos los registros revisados.
total = 0

# Contamos los horarios incorrectos.
errores = 0

# Abrimos el archivo sin cargarlo completamente en memoria.
with archivo.open("r", encoding="utf-8-sig", newline="") as f:

    # Leemos las columnas por su nombre.
    lector = csv.DictReader(f)

    # Revisamos cada registro del archivo.
    for fila in lector:

        # Aumentamos el contador de registros.
        total += 1

        # Recuperamos la hora registrada.
        hora = fila["hora"]

        # Separamos las horas y los minutos.
        partes = hora.split(":")

        # Verificamos que existan exactamente dos componentes numéricos.
        valido = len(partes) == 2 and all(
            parte.isdigit() and len(parte) == 2
            for parte in partes
        )

        # Si tiene dos componentes, verificamos sus límites.
        if valido:

            # Convertimos las horas y los minutos a números.
            horas = int(partes[0])
            minutos = int(partes[1])

            # Comprobamos que correspondan a una hora válida.
            valido = 0 <= horas <= 23 and 0 <= minutos <= 59

        # Si encontramos un horario incorrecto, lo contamos.
        if not valido:

            # Aumentamos la cantidad de errores.
            errores += 1

            # Mostramos únicamente los primeros cinco errores.
            if errores <= 5:
                print("Horario incorrecto:", fila)

# Mostramos la cantidad de registros revisados.
print("Registros revisados:", total)

# Mostramos cuántos horarios incorrectos encontramos.
print("Horarios incorrectos:", errores)

# Informamos si la validación fue satisfactoria.
if errores == 0:
    print("VALIDACIÓN SUPERADA")