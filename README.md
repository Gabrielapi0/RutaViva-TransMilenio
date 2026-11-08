# 🚌 RutaViva — Planificador de recorridos de TransMilenio

## Descripción

RutaViva es una aplicación académica desarrollada en Python que permite consultar recorridos entre estaciones de TransMilenio.

El sistema identifica viajes directos y alternativas con máximo un transbordo. También permite seleccionar recorridos según la cantidad de tramos o de cambios de servicio.

Incluye una interfaz desarrollada con Streamlit, un diagrama de estaciones y un mapa geográfico interactivo.

## Requisitos

- Python 3.14 o una versión compatible con las dependencias.
- Conexión a internet para cargar los mapas base, cuando sea necesario.
- Streamlit 1.66.1.

## Instalación

Abrir una terminal dentro de la carpeta principal del proyecto.

Instalar las dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Ejecución

Desde la carpeta principal del proyecto, ejecutar:

```powershell
python -m streamlit run Front/app.py
```

La aplicación se abrirá en el navegador.

Si no se abre automáticamente, visitar:

http://localhost:8501

## Fuentes de información

RutaViva permite trabajar con dos conjuntos de datos:

**Datos académicos del profesor:** archivos CSV proporcionados para el desarrollo del proyecto.

**Datos GTFS convertidos:** archivos generados a partir de un conjunto GTFS descargado en 2026.

Los datos convertidos se encuentran en `Datos_corregidos`.

La información se utiliza con fines académicos y no garantiza la disponibilidad actual de los servicios.

## Estructura del proyecto

- `Assets/`: recursos visuales.
- `Conversion/`: conversor GTFS y programas de validación.
- `Datos/`: archivos académicos originales.
- `Datos_corregidos/`: archivos convertidos desde GTFS.
- `Front/`: interfaz y visualización geográfica.
- `Motor/`: algoritmo de búsqueda de recorridos.
- `requirements.txt`: dependencias necesarias.
- `README.md`: instrucciones del proyecto.

## Funcionalidades principales

- Consulta de estaciones de origen y destino.
- Búsqueda de recorridos directos.
- Búsqueda de recorridos con máximo un transbordo.
- Selección entre menos tramos y menos transbordos.
- Simulación de estaciones cerradas.
- Visualización del itinerario.
- Mapa geográfico interactivo.
- Selección entre los conjuntos de datos académicos y GTFS.

## Conversión GTFS

El conversor se encuentra en `Conversion/convertir.py`.

Para generar nuevamente los archivos convertidos se necesita disponer de un archivo GTFS de entrada.

Ejemplo:

```powershell
python Conversion/convertir.py --entrada GTFS/GTFS-2026-04-29.zip --salida Datos_corregidos
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