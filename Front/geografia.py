"""Capa geográfica de RutaViva. SOLO se utiliza desde Front/, fuera del motor.

Obtiene ubicaciones y corredores del servicio ArcGIS público de TransMilenio;
los datos de clases siguen siendo los CSV históricos independientes.
"""

# Leemos información oficial y almacenamos una copia para trabajar sin red.
import json
# Normalizamos nombres de estaciones, quitando tildes y signos comunes.
import re
# Usamos la librería estándar, sin dependencias nuevas.
import unicodedata
# Gestionamos descargas HTTP y parámetros de consulta con Python.
from urllib.parse import urlencode
from urllib.request import Request, urlopen
# Localizamos las carpetas del proyecto.
from pathlib import Path

# URL oficial verificada en la documentación pública del FeatureServer.
SERVICIO = "https://gis.transmilenio.gov.co/arcgis/rest/services/ConsultaSubgerenciaPlanificacionSITP/Consulta_Planificacion_SITP/FeatureServer"

# Normalizamos nombre, sin convertir arbitrariamente estaciones distintas en iguales.
def normalizar(nombre):
    # Retiramos tildes y convertimos a mayúsculas.
    texto = unicodedata.normalize("NFKD", str(nombre or "").upper())
    # Conservamos solo letras, números y espacios tras la normalización.
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    # Unificamos guiones, puntos y espacios para comparar nombres.
    return " ".join(re.sub(r"[^A-Z0-9]+", " ", texto).split())

# Leemos propiedades de un GeoJSON sin asumir si el servidor escribe mayúsculas.
def propiedad(propiedades, clave, defecto=""):
    # Algunas capas de ArcGIS publican encabezados en mayúsculas.
    for k, v in propiedades.items():
        # Comparamos sin distinguir mayúsculas y minúsculas.
        if str(k).lower() == clave.lower():
            # Devolvemos el valor encontrado, o el valor alternativo.
            return defecto if v is None else v
    # Entregamos el valor alternativo si no existe la propiedad.
    return defecto

# Descargamos una capa oficial en formato GeoJSON y EPSG:4326.
def descargar_capa(numero, destino, campos):
    # Pedimos únicamente infraestructura existente y campos descriptivos necesarios.
    parametros = {
        "where": "esta_oper=1",
        "outFields": campos,
        "outSR": 4326,
        "returnGeometry": "true",
        "returnZ": "false",
        "returnM": "false",
        "f": "geojson",
    }
    # Construimos la consulta al servicio de datos geográficos.
    url = f"{SERVICIO}/{numero}/query?{urlencode(parametros)}"
    # Enviamos una solicitud con encabezado identificable.
    solicitud = Request(url, headers={"User-Agent":"RutaViva-Academico/1.0 (geojson public data)"})
    # Esperamos un tiempo limitado por si no hay internet.
    with urlopen(solicitud, timeout=12) as respuesta:
        # Procesamos los bytes recibidos como JSON.
        datos = json.loads(respuesta.read().decode("utf-8-sig"))
    # Rechazamos respuestas de error y estructuras ajenas a GeoJSON.
    if datos.get("type") != "FeatureCollection" or not isinstance(datos.get("features"), list):
        raise ValueError("El servicio no devolvió una colección GeoJSON válida")
    # Evitamos reemplazar un archivo válido por una colección vacía.
    if not datos["features"]:
        raise ValueError("La capa oficial llegó sin registros")
    # Creamos la carpeta que contendrá la copia local.
    destino.parent.mkdir(parents=True,exist_ok=True)
    # Guardamos la copia en UTF-8 para siguientes ejecuciones.
    destino.write_text(json.dumps(datos,ensure_ascii=False),encoding="utf-8")
    # Devolvemos la capa recién descargada.
    return datos

# Intentamos leer la copia existente antes de conectarnos a internet.
def cargar_geojson(destino, numero, campos, actualizar=False):
    # Cuando se pide refrescar, intentamos descargar un archivo nuevo.
    if actualizar or not destino.exists():
        try:
            # La consulta se ejecuta fuera del motor, exclusivamente para el mapa.
            return descargar_capa(numero, destino, campos)
        except Exception:
            # Si falla la conexión, mantenemos cualquier copia previamente guardada.
            pass
    # Si hay una copia guardada, la cargamos directamente desde disco.
    if destino.exists():
        try:
            # Interpretamos el archivo como una colección de objetos geográficos.
            datos = json.loads(destino.read_text(encoding="utf-8"))
            # Comprobamos que sea una colección que contenga entidades.
            if datos.get("type") == "FeatureCollection" and isinstance(datos.get("features"),list):
                return datos
        except (OSError, ValueError, TypeError):
            # En caso de un archivo local dañado, usamos una colección vacía.
            pass
    # Sin internet ni copia local, no inventamos puntos ni trazados.
    return {"type":"FeatureCollection","features":[]}

# Cargamos tanto estaciones como trazados oficiales, con copias locales.
def cargar_capas(carpeta_datos, actualizar=False):
    # Convertimos la ubicación dada a Path.
    datos = Path(carpeta_datos)
    # La capa 2 del servicio oficial contiene ubicaciones de estaciones.
    estaciones = cargar_geojson(datos/'geo_estaciones_oficial.geojson',2,'nom_est,num_est,ub_est,esta_oper,eta_oper,id_trazado',actualizar)
    # La capa 5 contiene las líneas de los corredores troncales.
    troncales = cargar_geojson(datos/'geo_troncales_oficial.geojson',5,'nom_tronc,nom_traz,id_trazado,esta_oper,eta_oper,tipo_tra',actualizar)
    # Entregamos ambas colecciones para que la interfaz las dibuje.
    return estaciones,troncales

# Relacionamos estaciones de 2021 con nombres oficiales 2026, sin coincidencias falsas.
def preparar_estaciones(geojson, estaciones_historicas):
    # Convertimos las estaciones académicas en un índice del frontend.
    nombres = {normalizar(nombre):nombre for nombre in estaciones_historicas}
    # Guardamos únicamente entidades que tengan coordenadas geográficas.
    salida = []
    # Revisamos todas las estaciones que devuelve el sistema oficial.
    for feature in geojson.get('features',[]):
        # Obtenemos los campos originales de la estación.
        propiedades = feature.get('properties') or {}
        # Identificamos el nombre tal como lo publica la entidad.
        nombre_oficial = str(propiedad(propiedades,'nom_est','')).strip()
        # Verificamos que la geometría sea un punto.
        geometria = feature.get('geometry') or {}
        coordenadas = geometria.get('coordinates') or []
        # Omitimos registros sin nombre o con coordenadas insuficientes.
        if not nombre_oficial or geometria.get('type') != 'Point' or len(coordenadas) < 2:
            continue
        # Extraemos primero longitud y después latitud, según GeoJSON.
        lon,lat = coordenadas[:2]
        # Comprobamos tipos y una ventana geográfica amplia de Bogotá.
        if not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)) or not (3.7<lat<5.0 and -75<lon<-73.2):
            continue
        # Vinculamos el nombre histórico solo ante una coincidencia normalizada exacta.
        historico = nombres.get(normalizar(nombre_oficial))
        # Guardamos ambos nombres separados para evitar confundir fechas.
        salida.append({'nombre':nombre_oficial,'historico':historico,'lat':lat,'lon':lon,
                       'ubicacion':str(propiedad(propiedades,'ub_est','')),
                       'identificador':str(propiedad(propiedades,'num_est',''))})
    # Entregamos los puntos listos para el mapa.
    return salida
