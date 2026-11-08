"""Convierte un GTFS estándar (carpeta o ZIP) a los CSV académicos de RutaViva.

Ejemplo desde la carpeta principal del proyecto:
    python Conversion/convertir.py --entrada GTFS/archivo.zip --salida Datos_convertidos

Los tres CSV existentes en Datos/ NO se sobrescriben por defecto.
"""

# argparse permite recibir la ubicación del GTFS y la carpeta de salida.
import argparse
# csv lee y escribe las tablas separadas por comas.
import csv
# io permite leer texto almacenado dentro de un ZIP.
import io
# unicodedata permite quitar tildes de nombres de estaciones.
import unicodedata
# zipfile permite abrir un GTFS descargado en formato ZIP.
import zipfile
# Path facilita trabajar con carpetas tanto en Windows como en otros sistemas.
from pathlib import Path


# Esta función convierte nombres a MAYÚSCULAS, sin tildes y con espacios limpios.
def normalizar_nombre(texto):
    # Convertimos el valor a texto, quitamos espacios y ponemos todo en mayúsculas.
    texto = str(texto or "").strip().upper()
    # Separaremos letras y marcas de acento usando la normalización de Unicode.
    texto = unicodedata.normalize("NFD", texto)
    # Reconstruimos el nombre descartando solamente los acentos combinados.
    texto = "".join(letra for letra in texto if unicodedata.category(letra) != "Mn")
    # Reemplazamos varios espacios consecutivos por uno solo.
    return " ".join(texto.split())


# Convertimos horarios GTFS HH:MM:SS a HH:MM sin exceder las 24 horas.
def convertir_hora(valor):
    # Dividimos la hora recibida por sus dos puntos.
    partes = str(valor or "").strip().split(":")
    # Si no tiene al menos hora y minuto, no se puede interpretar.
    if len(partes) < 2:
        return None
    # Comprobamos que las partes de la hora sean números.
    if not partes[0].isdigit() or not partes[1].isdigit():
        return None
    # Convertimos la hora y el minuto a números enteros.
    hora, minuto = int(partes[0]), int(partes[1])
    # Una cantidad de minutos fuera de rango indica un dato inválido.
    if minuto > 59:
        return None
    # GTFS admite 25:10 para indicar la 1:10 del día siguiente.
    # Aplicamos módulo 24 para ajustarnos al CSV académico de HH:MM.
    # ADVERTENCIA: con ello se pierde la información sobre el día siguiente.
    return f"{hora % 24:02d}:{minuto:02d}"


# Esta clase permite leer archivos GTFS de una carpeta o de un ZIP.
class FuenteGTFS:
    # Guardamos la ubicación original y preparamos una posible conexión ZIP.
    def __init__(self, entrada):
        # Convertimos la dirección recibida en un objeto Path.
        self.entrada = Path(entrada)
        # Abrimos el ZIP solamente cuando el usuario proporciona uno.
        self.zip = zipfile.ZipFile(self.entrada) if self.entrada.is_file() else None
        # Creamos un listado de rutas internas para localizar archivos en subcarpetas del ZIP.
        self.nombres = self.zip.namelist() if self.zip else []

    # Esta función entrega las filas de un archivo GTFS como registros de texto.
    def leer(self, nombre):
        # Si el GTFS es un ZIP, buscamos un archivo cuyo último componente coincida.
        if self.zip:
            # Buscamos el archivo sin importar la carpeta interna o las mayúsculas.
            coincidencias = [n for n in self.nombres if n.rsplit("/", 1)[-1].lower() == nombre.lower()]
            # Avisamos cuando falta un archivo necesario.
            if not coincidencias:
                raise FileNotFoundError(f"No encontré {nombre} dentro del ZIP GTFS")
            # Abrimos el archivo interno y lo interpretamos como texto CSV con BOM opcional.
            with self.zip.open(coincidencias[0]) as bruto:
                with io.TextIOWrapper(bruto, encoding="utf-8-sig", newline="") as archivo:
                    # DictReader usa los encabezados de cada columna como claves.
                    yield from csv.DictReader(archivo)
        # Si es una carpeta, buscamos el archivo directamente allí.
        else:
            # Probamos la carpeta principal o una única subcarpeta GTFS.
            posibles = [self.entrada / nombre] + list(self.entrada.glob(f"*/{nombre}"))
            # Seleccionamos el primer archivo que realmente exista.
            archivo_local = next((p for p in posibles if p.is_file()), None)
            # Avisamos si falta algún componente obligatorio.
            if archivo_local is None:
                raise FileNotFoundError(f"No encontré {nombre} dentro de {self.entrada}")
            # Abrimos el CSV original con codificación UTF-8.
            with archivo_local.open("r", encoding="utf-8-sig", newline="") as archivo:
                # Entregamos las filas una por una.
                yield from csv.DictReader(archivo)

    # Cerramos el ZIP cuando terminamos de utilizarlo.
    def cerrar(self):
        # Solo hay algo que cerrar si la entrada era un ZIP.
        if self.zip:
            self.zip.close()


# Construimos los tres CSV académicos a partir de las tablas estándar del GTFS.
def convertir(entrada, salida):
    # Creamos una carpeta independiente para proteger los CSV del planeador actual.
    carpeta_salida = Path(salida)
    # Evitamos sobrescribir la carpeta original Datos del proyecto accidentalmente.
    if carpeta_salida.resolve() == Path("Datos").resolve():
        raise ValueError("Por seguridad, utiliza una carpeta distinta de Datos, como Datos_convertidos")
    # Abrimos la fuente del GTFS.
    fuente = FuenteGTFS(entrada)
    try:
        # Relacionamos cada identificador de parada con su nombre y estación principal.
        paradas = {}
        # Leemos los registros de stops.txt.
        for fila in fuente.leer("stops.txt"):
            # El ID es el identificador técnico de cada plataforma o estación.
            identificador = (fila.get("stop_id") or "").strip()
            # Guardamos su nombre original normalizado.
            nombre = normalizar_nombre(fila.get("stop_name", ""))
            # Conservamos el ID de estación principal cuando exista parent_station.
            padre = (fila.get("parent_station") or "").strip()
            # Evitamos cargar filas incompletas.
            if identificador and nombre:
                paradas[identificador] = (nombre, padre)

        # Traducimos IDs de estaciones/plataformas en nombres de estaciones consolidadas.
        def nombre_estacion(identificador):
            # Consultamos si la parada existe en el archivo de origen.
            if identificador not in paradas:
                return None
            # Recuperamos su nombre y estación principal.
            nombre, padre = paradas[identificador]
            # Si hay estación principal conocida, usamos su nombre común.
            if padre in paradas:
                return paradas[padre][0]
            # Si no la hay, usamos el nombre de la propia parada.
            return nombre

        # Relacionamos ID técnico de ruta con el nombre público disponible.
        rutas_originales = {}
        # Leemos routes.txt.
        for fila in fuente.leer("routes.txt"):
            # Recuperamos el ID único del servicio original.
            identificador = (fila.get("route_id") or "").strip()
            # Elegimos nombre corto público, luego nombre largo y finalmente ID.
            etiqueta = (fila.get("route_short_name") or fila.get("route_long_name") or identificador).strip()
            # Guardamos los nombres para los viajes siguientes.
            if identificador:
                rutas_originales[identificador] = normalizar_nombre(etiqueta)

        # Guardamos la ruta y dirección de cada viaje programado.
        viajes = {}
        # Leemos trips.txt, que conecta los viajes con sus rutas.
        for fila in fuente.leer("trips.txt"):
            # Recuperamos el identificador único de cada viaje programado.
            viaje_id = (fila.get("trip_id") or "").strip()
            # Recuperamos la ruta original que sigue el viaje.
            ruta_id = (fila.get("route_id") or "").strip()
            # GTFS puede identificar dos sentidos con 0 y 1.
            sentido = (fila.get("direction_id") or "0").strip()
            # Solo guardamos viajes que tienen una ruta conocida.
            if viaje_id and ruta_id in rutas_originales:
                viajes[viaje_id] = (ruta_id, sentido)

        # Guardaremos para cada viaje la secuencia de sus paradas y horas.
        eventos = {}
        # Leemos stop_times.txt, que enlaza los viajes con estaciones y horarios.
        for fila in fuente.leer("stop_times.txt"):
            # Consultamos el ID de viaje al que pertenece el evento.
            viaje_id = (fila.get("trip_id") or "").strip()
            # Ignoramos filas de viajes no presentes en trips.txt.
            if viaje_id not in viajes:
                continue
            # Buscamos el nombre normalizado de la parada.
            estacion = nombre_estacion((fila.get("stop_id") or "").strip())
            # Recuperamos el orden de visita de la estación.
            posicion_texto = (fila.get("stop_sequence") or "").strip()
            # Usamos hora de llegada o salida si una de ellas no existe.
            hora = convertir_hora(fila.get("arrival_time") or fila.get("departure_time"))
            # Ignoramos filas sin estación o sin orden válido.
            if not estacion or not posicion_texto.isdigit():
                continue
            # Creamos una lista para el viaje cuando todavía no existe.
            if viaje_id not in eventos:
                eventos[viaje_id] = []
            # Añadimos orden, estación y hora a la lista.
            eventos[viaje_id].append((int(posicion_texto), estacion, hora))

        # Cada route_id original recibe un número estable y distinto.
        # Dos rutas GTFS pueden tener el mismo nombre público, pero NO son la misma ruta.
        # Incluimos R<número> en el identificador para evitar colisiones de nombres.
        codigos_ruta = {}
        for numero, ruta_id in enumerate(sorted(rutas_originales), start=1):
            codigos_ruta[ruta_id] = numero

        # Las diferentes variantes de recorrido deben tener distintos IDs académicos.
        patrones = {}
        # Contamos variantes por route_id y sentido, sin recorrer patrones repetidamente.
        conteo_variantes = {}
        # Relacionamos cada viaje con la variante de recorrido a la que pertenece.
        variantes_por_viaje = {}
        # Recorremos todos los viajes programados.
        for viaje_id, (ruta_id, sentido) in viajes.items():
            # Recuperamos los eventos de este viaje, si existen.
            lista = eventos.get(viaje_id, [])
            # No generamos rutas sin paradas suficientes.
            if not lista:
                continue
            # Ordenamos según stop_sequence (permitido en la conversión, fuera de Motor).
            lista.sort(key=lambda elemento: elemento[0])
            # Evitamos plataformas repetidas consecutivas al consolidar estaciones.
            secuencia = []
            # Revisamos todas las paradas de la ruta en orden.
            for _orden, estacion, _hora in lista:
                # Añadimos una estación solo si no repite inmediatamente la anterior.
                if not secuencia or secuencia[-1] != estacion:
                    secuencia.append(estacion)
            # No consideramos recorridos con menos de dos estaciones diferentes.
            if len(secuencia) < 2:
                continue
            # Identificamos una variante por ruta original, sentido y secuencia de estaciones.
            clave = (ruta_id, sentido, tuple(secuencia))
            # Asignamos un nombre consistente a cada variante de recorrido encontrada.
            if clave not in patrones:
                # Identificamos la pareja ruta GTFS y sentido de circulación.
                pareja = (ruta_id, sentido)
                # Numeramos solo las secuencias distintas de esta ruta y sentido.
                numero = conteo_variantes.get(pareja, 0) + 1
                conteo_variantes[pareja] = numero
                # R<número> diferencia rutas GTFS con la misma etiqueta comercial.
                # De este modo no mezclamos las paradas de dos route_id distintos.
                nombre = f"{rutas_originales[ruta_id]}-R{codigos_ruta[ruta_id]}-S{sentido}-V{numero}"
                # Guardamos la secuencia y el identificador académico.
                patrones[clave] = (nombre, secuencia)
            # Guardamos a qué variante pertenece este viaje.
            variantes_por_viaje[viaje_id] = patrones[clave][0]

        # Comprobamos que cada patrón tenga su propio identificador antes de escribir.
        nombres_patrones = [nombre for nombre, _secuencia in patrones.values()]
        if len(nombres_patrones) != len(set(nombres_patrones)):
            raise ValueError("Se generaron identificadores de recorridos repetidos")

        # Creamos la carpeta destino cuando todavía no existe.
        carpeta_salida.mkdir(parents=True, exist_ok=True)
        # Seleccionamos únicamente estaciones que aparecen en recorridos utilizables.
        estaciones = sorted({estacion for _nombre, secuencia in patrones.values() for estacion in secuencia})
        # Escribimos estaciones.csv con una sola columna.
        with (carpeta_salida / "estaciones.csv").open("w", encoding="utf-8", newline="") as archivo:
            # Preparamos un escritor de CSV.
            escritor = csv.writer(archivo)
            # Escribimos el encabezado exacto exigido por el proyecto.
            escritor.writerow(["nombre"])
            # Escribimos una fila por estación, sin duplicados.
            for estacion in estaciones:
                escritor.writerow([estacion])

        # Escribimos rutas.csv con el recorrido de cada variante en un único sentido.
        with (carpeta_salida / "rutas.csv").open("w", encoding="utf-8", newline="") as archivo:
            # Preparamos el escritor de rutas.
            escritor = csv.writer(archivo)
            # Escribimos las columnas del contrato académico.
            escritor.writerow(["ruta", "orden", "estacion"])
            # Ordenamos las variantes por identificador para resultados reproducibles.
            for nombre, secuencia in sorted(patrones.values(), key=lambda p: p[0]):
                # Numeramos las paradas empezando en uno.
                for orden, estacion in enumerate(secuencia, start=1):
                    escritor.writerow([nombre, orden, estacion])

        # Escribimos horarios.csv con las horas de paso de cada viaje GTFS.
        with (carpeta_salida / "horarios.csv").open("w", encoding="utf-8", newline="") as archivo:
            # Preparamos el escritor de horarios.
            escritor = csv.writer(archivo)
            # Escribimos el encabezado solicitado por el proyecto.
            escritor.writerow(["ruta", "estacion", "hora"])
            # Revisamos todos los viajes que tienen una variante válida.
            for viaje_id, nombre in variantes_por_viaje.items():
                # Recorremos los eventos cronológicamente dentro de ese viaje.
                for _orden, estacion, hora in eventos[viaje_id]:
                    # Solo escribimos eventos con horario disponible.
                    if hora is not None:
                        escritor.writerow([nombre, estacion, hora])

        # Mostramos un resumen final de archivos producidos.
        print("CONVERSIÓN GTFS TERMINADA")
        # Mostramos cuántas estaciones quedaron registradas.
        print("Estaciones:", len(estaciones))
        # Mostramos cuántas variantes de servicio se detectaron.
        print("Recorridos de un sentido:", len(patrones))
        # Indicamos cómo se construyeron los códigos únicos para las variantes.
        print("Identificadores únicos: nombre-R<número de route_id>-S<sentido>-V<variante>")
        # Mostramos la carpeta de salida para localizar los resultados.
        print("Archivos generados en:", carpeta_salida.resolve())
        # Recordamos que los resultados varían según el GTFS utilizado.
        print("Nota: no se garantiza coincidencia con los CSV del profesor de 2021.")
    finally:
        # Cerramos el ZIP aunque haya ocurrido un error.
        fuente.cerrar()


# Este bloque se ejecuta cuando abrimos convertir.py como programa principal.
if __name__ == "__main__":
    # Configuramos las opciones que podemos escribir en la terminal.
    parser = argparse.ArgumentParser(description="Convierte un GTFS a CSV académicos de TransMilenio")
    # La entrada debe indicar la carpeta GTFS o un archivo ZIP auténtico.
    parser.add_argument("--entrada", required=True, help="Ruta al ZIP o carpeta GTFS")
    # La salida queda separada de Datos para evitar sobrescribir archivos existentes.
    parser.add_argument("--salida", default="Datos_convertidos", help="Carpeta donde se crean los CSV")
    # Leemos los valores proporcionados por el usuario.
    argumentos = parser.parse_args()
    # Llamamos a la función que ejecuta toda la conversión.
    convertir(argumentos.entrada, argumentos.salida)
