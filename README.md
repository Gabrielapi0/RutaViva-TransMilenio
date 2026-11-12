# 🚌 RutaViva — Planificador de recorridos de TransMilenio

## Descripción

RutaViva es una aplicación académica desarrollada en Python que permite consultar recorridos entre estaciones de TransMilenio.

El sistema identifica viajes directos y alternativas con máximo un transbordo. También permite seleccionar recorridos según la cantidad de tramos o de cambios de servicio.

Incluye una interfaz web con estilo TransMilenio: planeador de viajes, pantalla de llegadas por estación, ranking, centro de control, simulador de hora pico y panel de rendimiento.

## Requisitos

- Python 3.10 o superior. La app no necesita instalar nada: el servidor usa solo la librería estándar.

## Ejecución (un solo comando)

Desde la carpeta principal del proyecto:

    python app.py

La aplicación se abre sola en el navegador. Si no, visitar http://localhost:8000

Opciones: `python app.py --puerto 8080` · `python app.py --datos Pruebas/Red_pequena` · `--sin-navegador`

## Fuente de información

Los archivos de `Datos/` son la red de TransMilenio convertida desde el GTFS de julio de 2021, que es la fuente que pide el enunciado. La aplicación y el motor solo leen esos tres CSV.

La información se utiliza con fines académicos y no garantiza la disponibilidad actual de los servicios.

## Estructura del proyecto

- `Conversion/`: conversor GTFS y programas de validación.
- `Datos/`: estaciones.csv, rutas.csv y horarios.csv (GTFS julio 2021).
- `app.py`: servidor de la interfaz web (traduce peticiones a llamadas del motor).
- `web/`: interfaz (HTML, CSS y JavaScript).
- `Front/`: panel de rendimiento (R11) y pantalla de operación (R7–R9).
- `Motor/`: algoritmo de búsqueda de recorridos.
- `requirements.txt`: dependencias necesarias.
- `README.md`: instrucciones del proyecto.

## Funcionalidades principales

- Consulta de estaciones de origen y destino.
- Búsqueda de recorridos directos.
- Búsqueda de recorridos con máximo un transbordo.
- Selección entre menos tramos y menos transbordos.
- Simulación de estaciones cerradas.
- Visualización del itinerario con hora del próximo bus.
- Pantalla de llegadas por estación, ranking, centro de control, simulador de hora pico y panel de rendimiento.

## Conversión GTFS

El conversor se encuentra en `Conversion/convertir.py`.

Para generar nuevamente los archivos convertidos se necesita disponer de un archivo GTFS de entrada.

Ejemplo:

```powershell
python Conversion/convertir.py --entrada GTFS/gtfs_julio_2021.zip --salida Datos_corregidos
```

**Importante:** el archivo GTFS original no está incluido necesariamente en esta versión de entrega. Si se desea reproducir la conversión, debe colocarse en la ubicación indicada o modificar el argumento `--entrada`.

El conversor genera:

- `estaciones.csv`
- `rutas.csv`
- `horarios.csv`

### Limitaciones

La conversión de horarios utiliza un formato de reloj de 24 horas. En consecuencia, los horarios GTFS posteriores a las 24:00 pierden la indicación de que corresponden al día siguiente.

El sistema no calcula tiempos reales de espera ni garantiza la operación actual de los servicios.

## Uso académico

Proyecto desarrollado con fines educativos para aplicar conceptos de estructuras de datos, algoritmos de búsqueda, ordenamiento y procesamiento de información.

---

## Conversión de datos GTFS

RutaViva incluye un conversor desarrollado en Python que transforma
datos GTFS en los tres CSV utilizados por el motor:

- estaciones.csv
- rutas.csv
- horarios.csv

### Requisitos

- Python instalado.
- Archivo GTFS válido en formato ZIP o carpeta.
- Espacio suficiente para generar los archivos convertidos.

### Ejecutar el conversor

Desde la carpeta principal del proyecto:

python Conversion/convertir.py --entrada "ruta/al/archivo_gtfs.zip" --salida "Datos_corregidos"

Sustituir "ruta/al/archivo_gtfs.zip" por la ubicación real del GTFS.

### Archivos generados

El programa genera:

Datos_corregidos/estaciones.csv
Datos_corregidos/rutas.csv
Datos_corregidos/horarios.csv

### Tratamiento de horarios

GTFS permite horas posteriores a medianoche, como 25:10:00.

Para adaptarlas al formato académico HH:MM, el conversor
aplica módulo 24.

Ejemplo:

25:10:00 -> 01:10

Esta transformación pierde la información de que el evento
corresponde al día siguiente.

### Consideraciones

El archivo Datos_corregidos/horarios.csv puede superar los
375 MB dependiendo del GTFS utilizado.

Por esta razón, no se incluye directamente en el repositorio GitHub.

Para utilizar los datos convertidos, primero debe ejecutarse
el conversor con un archivo GTFS válido.

Los archivos de Datos/ corresponden al conjunto académico
utilizado durante el desarrollo y se conservan por separado.

La estructura y los identificadores de las rutas pueden variar
según la versión del GTFS utilizada.