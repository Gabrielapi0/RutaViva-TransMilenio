"""Convierte el GTFS de TransMilenio (carpeta o ZIP) a los tres CSV de RutaViva.

Ejemplo desde la carpeta principal del proyecto:
    python Conversion/convertir.py --entrada GTFS-2021-07-14.zip --salida Datos_convertidos

Con el GTFS del 14 de julio de 2021 produce las mismas 147 estaciones y
181 rutas de Datos/ (177 con el mismo nombre y recorrido exacto) y ~98 % de
los mismos horarios. Los CSV de Datos/ NO se sobrescriben.

Reglas de la conversión (explicadas en el README, sección "Conversión GTFS"):
  1. Solo rutas TRONCALES (route_desc = TRONCAL); con --todas se incluye todo el SITP.
  2. Un solo día de servicio: el de --fecha (por defecto miércoles 14/07/2021).
  3. Nombre de estación: MAYÚSCULAS, sin tildes ni símbolos (º), y sin el sufijo
     del vagón o la plataforma ("CALLE 19 B - 4 ó 6" -> "CALLE 19").
  4. Si un viaje pasa dos veces por la misma estación, se deja la primera.
  5. Cada patrón distinto de estaciones de una ruta comercial es una ruta del CSV
     en un solo sentido ("B10-1", "B10-2"...; si hay uno solo, "D51").
     - Se descartan los patrones con menos de 4 viajes al día.
     - Un patrón que es solo un pedazo de otro más largo (media vuelta) no es una
       ruta propia: sus viajes se suman a la variante que lo contiene.
     - Se numeran de la variante con más viajes a la de menos.
  6. Horas GTFS >= 24:00 (p. ej. 25:10) se pasan a la hora del reloj (01:10).
"""

# argparse permite recibir la ubicación del GTFS y la carpeta de salida.
import argparse
# csv lee y escribe las tablas separadas por comas.
import csv
# datetime permite saber qué día de la semana es la fecha elegida.
import datetime
# io permite leer texto almacenado dentro de un ZIP.
import io
# re permite quitar el sufijo del vagón en los nombres de las paradas.
import re
# unicodedata permite quitar tildes de nombres de estaciones.
import unicodedata
# zipfile permite abrir un GTFS descargado en formato ZIP.
import zipfile
# Path facilita trabajar con carpetas tanto en Windows como en otros sistemas.
from pathlib import Path

# Mínimo de viajes al día para que un patrón cuente como ruta propia.
MIN_VIAJES = 4
# Sufijos de vagón o plataforma: " A - 4 ó 6", " B - 1", " C - 3"...
SUFIJO_VAGON = re.compile(r"\s+[A-Z]\s*-\s*\d.*$")
# Sufijos de plataforma en portales: " T6", " T-6B", " T2A"...
SUFIJO_PORTAL = re.compile(r"\s+T\s*-?\s*\d+\s*[A-Z]?$")


# Esta función convierte nombres a MAYÚSCULAS, sin tildes, sin símbolos y con espacios limpios.
def normalizar_nombre(texto):
    # Convertimos el valor a texto, quitamos espacios y ponemos todo en mayúsculas.
    texto = str(texto or "").strip().upper()
    # Separaremos letras y marcas de acento usando la normalización de Unicode.
    texto = unicodedata.normalize("NFD", texto)
    # Reconstruimos el nombre descartando los acentos y los ordinales (º, ª).
    texto = "".join(letra for letra in texto if unicodedata.category(letra) != "Mn" and letra not in "ºª")
    # Reemplazamos varios espacios consecutivos por uno solo.
    return " ".join(texto.split())


# Quita el vagón o la plataforma para quedarnos con el nombre de la estación.
def nombre_de_estacion(nombre_parada):
    # Normalizamos primero (mayúsculas y sin tildes).
    texto = normalizar_nombre(nombre_parada)
    # "CALLE 19 B - 4 O 6" -> "CALLE 19".
    texto = SUFIJO_VAGON.sub("", texto)
    # "PORTAL ELDORADO T-6B" -> "PORTAL ELDORADO".
    texto = SUFIJO_PORTAL.sub("", texto)
    # Limpiamos espacios sobrantes.
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


# ¿El patrón corto aparece seguido (sin saltos) dentro del largo?
def es_tramo_de(corto, largo):
    # Un patrón no es tramo de sí mismo ni de uno igual o más corto.
    if len(corto) >= len(largo):
        return False
    # Probamos cada posición de inicio posible dentro del patrón largo.
    for inicio in range(len(largo) - len(corto) + 1):
        if largo[inicio:inicio + len(corto)] == corto:
            return True
    return False


# Esta clase permite leer archivos GTFS de una carpeta o de un ZIP.
class FuenteGTFS:
    # Guardamos la ubicación original y preparamos una posible conexión ZIP.
    def __init__(self, entrada):
        # Convertimos la dirección recibida en un objeto Path.
        self.entrada = Path(entrada)
        # Avisamos claramente si el archivo o carpeta no existe.
        if not self.entrada.exists():
            raise FileNotFoundError(f"No existe {self.entrada}. Revisa la ruta del GTFS.")
        # Abrimos el ZIP solamente cuando el usuario proporciona uno.
        self.zip = zipfile.ZipFile(self.entrada) if self.entrada.is_file() else None
        # Creamos un listado de rutas internas para localizar archivos en subcarpetas del ZIP.
        self.nombres = self.zip.namelist() if self.zip else []

    # ¿Existe este archivo dentro del GTFS? (calendar_dates.txt es opcional).
    def tiene(self, nombre):
        if self.zip:
            return any(n.rsplit("/", 1)[-1].lower() == nombre.lower() for n in self.nombres)
        return (self.entrada / nombre).is_file() or any(self.entrada.glob(f"*/{nombre}"))

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


# Servicios (service_id) que operan en la fecha elegida, según calendar y calendar_dates.
def servicios_del_dia(fuente, fecha):
    # Día de la semana en el formato de las columnas de calendar.txt.
    dia = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"][fecha.weekday()]
    # La fecha como texto AAAAMMDD, igual que en el GTFS.
    texto = fecha.strftime("%Y%m%d")
    activos = set()
    # calendar.txt: servicios que operan ese día de la semana dentro de su vigencia.
    if fuente.tiene("calendar.txt"):
        for fila in fuente.leer("calendar.txt"):
            if fila.get(dia) == "1" and fila.get("start_date", "") <= texto <= fila.get("end_date", ""):
                activos.add(fila["service_id"])
    # calendar_dates.txt: excepciones (1 = se agrega ese día, 2 = se quita).
    if fuente.tiene("calendar_dates.txt"):
        for fila in fuente.leer("calendar_dates.txt"):
            if fila.get("date") == texto:
                if fila.get("exception_type") == "1":
                    activos.add(fila["service_id"])
                elif fila.get("exception_type") == "2":
                    activos.discard(fila["service_id"])
    return activos


# Construimos los tres CSV académicos a partir de las tablas estándar del GTFS.
def convertir(entrada, salida, fecha="2021-07-14", todas=False):
    # Creamos una carpeta independiente para proteger los CSV del planeador actual.
    carpeta_salida = Path(salida)
    # Evitamos sobrescribir la carpeta original Datos del proyecto accidentalmente.
    if carpeta_salida.resolve() == Path("Datos").resolve():
        raise ValueError("Por seguridad, utiliza una carpeta distinta de Datos, como Datos_convertidos")
    # Abrimos la fuente del GTFS.
    fuente = FuenteGTFS(entrada)
    try:
        # 1) Día de servicio.
        dia = datetime.date.fromisoformat(fecha)
        servicios = servicios_del_dia(fuente, dia)
        if not servicios:
            raise ValueError(f"Ningún servicio opera el {fecha}. Prueba otra fecha con --fecha AAAA-MM-DD.")

        # 2) Nombre de estación de cada parada (sin vagón ni plataforma).
        paradas = {}
        for fila in fuente.leer("stops.txt"):
            identificador = (fila.get("stop_id") or "").strip()
            nombre = nombre_de_estacion(fila.get("stop_name", ""))
            if identificador and nombre:
                paradas[identificador] = nombre

        # 3) Rutas troncales (o todas con --todas) y su nombre comercial.
        nombre_comercial = {}
        for fila in fuente.leer("routes.txt"):
            if not todas and (fila.get("route_desc") or "").strip().upper() != "TRONCAL":
                continue
            identificador = (fila.get("route_id") or "").strip()
            etiqueta = (fila.get("route_short_name") or fila.get("route_long_name") or identificador).strip()
            if identificador:
                nombre_comercial[identificador] = normalizar_nombre(etiqueta)

        # 4) Viajes de esas rutas que operan ese día, en el orden de trips.txt.
        viajes = {}
        orden_viaje = {}
        for posicion, fila in enumerate(fuente.leer("trips.txt")):
            viaje_id = (fila.get("trip_id") or "").strip()
            ruta_id = (fila.get("route_id") or "").strip()
            if viaje_id and ruta_id in nombre_comercial and fila.get("service_id") in servicios:
                viajes[viaje_id] = nombre_comercial[ruta_id]
                orden_viaje[viaje_id] = posicion

        # 5) Paradas y horas de cada viaje.
        eventos = {}
        for fila in fuente.leer("stop_times.txt"):
            viaje_id = (fila.get("trip_id") or "").strip()
            if viaje_id not in viajes:
                continue
            estacion = paradas.get((fila.get("stop_id") or "").strip())
            posicion_texto = (fila.get("stop_sequence") or "").strip()
            hora = convertir_hora(fila.get("arrival_time") or fila.get("departure_time"))
            if not estacion or not posicion_texto.isdigit():
                continue
            eventos.setdefault(viaje_id, []).append((int(posicion_texto), estacion, hora))

        # 6) Patrón de estaciones de cada viaje (si repite estación, queda la primera vez).
        patron_de = {}
        for viaje_id, lista in eventos.items():
            lista.sort(key=lambda elemento: elemento[0])
            vistas = set()
            limpia = []
            for _orden, estacion, hora in lista:
                if estacion not in vistas:
                    vistas.add(estacion)
                    limpia.append((estacion, hora))
            eventos[viaje_id] = limpia
            if len(limpia) >= 2:
                patron_de[viaje_id] = tuple(estacion for estacion, _hora in limpia)

        # 7) Variantes de cada ruta comercial.
        viajes_por_ruta = {}
        for viaje_id in patron_de:
            viajes_por_ruta.setdefault(viajes[viaje_id], []).append(viaje_id)

        rutas_finales = {}        # nombre CSV -> tupla de estaciones
        ruta_de_viaje = {}        # viaje_id   -> nombre CSV
        for comercial in sorted(viajes_por_ruta):
            lista_viajes = viajes_por_ruta[comercial]
            # Cuántos viajes hace cada patrón.
            conteo = {}
            for viaje_id in lista_viajes:
                conteo[patron_de[viaje_id]] = conteo.get(patron_de[viaje_id], 0) + 1
            # Variantes propias: con suficientes viajes y que no sean un pedazo de otra.
            bases = [p for p, n in conteo.items()
                     if n >= MIN_VIAJES and not any(es_tramo_de(p, otro) for otro in conteo if otro != p)]
            if not bases:
                continue
            # Cada viaje va a su variante; las medias vueltas, a la variante que las contiene.
            asignado = {}
            total = {p: 0 for p in bases}
            primero = {}
            for viaje_id in lista_viajes:
                patron = patron_de[viaje_id]
                if patron in total:
                    destino = patron
                else:
                    contienen = [b for b in bases if es_tramo_de(patron, b)]
                    if not contienen:
                        continue  # patrón raro (< 4 viajes) que no es tramo de ninguna variante
                    destino = max(contienen, key=lambda b: conteo[b])
                asignado[viaje_id] = destino
                total[destino] += 1
                primero[destino] = min(primero.get(destino, orden_viaje[viaje_id]), orden_viaje[viaje_id])
            # Numeramos de la variante con más viajes a la de menos.
            ordenadas = sorted(bases, key=lambda b: (-total[b], primero.get(b, 0)))
            nombres = {}
            for i, b in enumerate(ordenadas, start=1):
                nombres[b] = comercial if len(ordenadas) == 1 else f"{comercial}-{i}"
                rutas_finales[nombres[b]] = b
            for viaje_id, destino in asignado.items():
                ruta_de_viaje[viaje_id] = nombres[destino]

        # 8) Escribir los tres CSV.
        carpeta_salida.mkdir(parents=True, exist_ok=True)
        estaciones = sorted({e for recorrido in rutas_finales.values() for e in recorrido})
        with (carpeta_salida / "estaciones.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["nombre"])
            for estacion in estaciones:
                escritor.writerow([estacion])

        with (carpeta_salida / "rutas.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["ruta", "orden", "estacion"])
            for nombre in sorted(rutas_finales):
                for orden, estacion in enumerate(rutas_finales[nombre], start=1):
                    escritor.writerow([nombre, orden, estacion])

        filas_horario = 0
        with (carpeta_salida / "horarios.csv").open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["ruta", "estacion", "hora"])
            for viaje_id in sorted(ruta_de_viaje, key=lambda v: orden_viaje[v]):
                for estacion, hora in eventos[viaje_id]:
                    if hora is not None:
                        escritor.writerow([ruta_de_viaje[viaje_id], estacion, hora])
                        filas_horario += 1

        print("CONVERSIÓN GTFS TERMINADA")
        print("Día de servicio:", fecha, "| Rutas:", "todas" if todas else "solo troncales")
        print("Estaciones:", len(estaciones))
        print("Rutas (un sentido):", len(rutas_finales))
        print("Horarios:", filas_horario)
        print("Archivos generados en:", carpeta_salida.resolve())
    finally:
        # Cerramos el ZIP aunque haya ocurrido un error.
        fuente.cerrar()


# Este bloque se ejecuta cuando abrimos convertir.py como programa principal.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convierte el GTFS de TransMilenio a los CSV de RutaViva")
    parser.add_argument("--entrada", required=True, help="Ruta al ZIP o carpeta GTFS")
    parser.add_argument("--salida", default="Datos_convertidos", help="Carpeta donde se crean los CSV")
    parser.add_argument("--fecha", default="2021-07-14", help="Día de servicio a convertir (AAAA-MM-DD)")
    parser.add_argument("--todas", action="store_true", help="Incluir todo el SITP, no solo troncales")
    argumentos = parser.parse_args()
    convertir(argumentos.entrada, argumentos.salida, argumentos.fecha, argumentos.todas)
