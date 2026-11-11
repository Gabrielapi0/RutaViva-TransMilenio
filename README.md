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
- `motor/`: algoritmo de búsqueda de recorridos.
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

## R12 — Decisiones de diseño

Cada integrante documenta aquí sus requisitos: estructura, algoritmo,
alternativa descartada y la O grande de cada operación, diciendo qué es n.

### R5 · Planear un viaje (Integrante 3)

**Qué resuelve:** entre dos estaciones, el viaje directo o con un solo
transbordo que pase por menos paradas: qué ruta tomar, dónde bajarse y
dónde cambiar. El código está en `motor/viajes.py`.

**Estructuras**

| Estructura | Qué guarda | Para qué |
|---|---|---|
| Rutas | Lista de `[servicio, [[orden, estación], ...]]`, con las paradas en el orden real del recorrido | Respetar el sentido de cada servicio |
| Catálogo de estaciones | Arreglo de nombres ordenado alfabéticamente | Saber si una estación existe con búsqueda binaria |
| Índice global | Arreglo ordenado de `[estación, ruta, posición]` | Encontrar solo los servicios que pasan por el origen o el destino |
| Índice por ruta | Por cada ruta, arreglo ordenado de `[estación, posición]` | Saber en qué posición pasa una ruta por una estación |
| Prefijos de cierres | Por cada ruta, cuántas estaciones cerradas hay hasta cada parada | Saber si un tramo tiene cierres en O(1) |

Todo son listas usadas como arreglos: dentro de `motor/` no se usan
`dict`, `set`, `sorted`, `.sort()`, `min`, `max`, `x in lista`, `.index()`
ni `.count()`.

**Algoritmo**

1. Se valida que origen y destino existan y estén abiertos. Si son la
   misma estación, el viaje tiene 0 paradas.
2. *Directos:* para cada servicio que pasa por el origen se busca el
   destino en una posición posterior y se revisa que el tramo no tenga
   estaciones cerradas.
3. Si hay un directo de 1 tramo, no se busca más: no existe algo más corto.
4. *Un transbordo:* para cada par (servicio que sale del origen, servicio
   que llega al destino) se recorren las paradas del primero después del
   origen. En cada una se busca, con búsqueda binaria, si el segundo
   servicio pasa por ahí antes del destino. Si el primer tramo ya tiene un
   cierre, se corta, porque alargarlo no lo vuelve a abrir.
5. Se queda el viaje con menos tramos. En empate gana el directo, y si
   todo empata, el primero encontrado.

Una estación cerrada no sirve ni de paso ni como punto de transbordo,
porque los prefijos la detectan en cualquier tramo.

**Respuestas definidas**

| Caso | Respuesta |
|---|---|
| Viaje directo | `["DIRECTO", servicio, None, None, tramos]` |
| Un transbordo | `["TRANSBORDO", servicio_1, servicio_2, estación_de_cambio, tramos]` |
| Origen igual a destino | `["MISMO DESTINO", None, None, None, 0]` |
| Estación inexistente o cerrada | `["ERROR", mensaje, None, None, 0]` |
| Sin viaje con máximo un transbordo | `None` |

**Alternativas descartadas**

- *Recorrer todas las rutas en cada consulta:* cuesta O(P) por búsqueda
  aunque el origen aparezca en pocas rutas. El índice ordenado limita la
  búsqueda a los servicios que pasan por el origen y el destino.
- *Un diccionario estación → rutas:* daría búsquedas en O(1), pero `dict`
  está prohibido en `motor/`. Los arreglos ordenados con búsqueda binaria
  dan O(log P), que es lo mejor posible sin diccionarios.
- *BFS sobre un grafo de estaciones:* encuentra el camino con menos
  paradas, pero no controla cuántas veces se cambia de bus. Limitarlo a un
  transbordo exige guardar el servicio en cada estado, y la búsqueda por
  fases es más simple y fácil de explicar.
- *Revisar cada estación del tramo para ver si está cerrada:* cuesta O(L)
  por tramo y se repite miles de veces por consulta. Los prefijos cuestan
  O(P) una vez por consulta y luego O(1) por tramo.

**Complejidad**

Variables: **P** = apariciones de paradas en todas las rutas (filas de
`rutas.csv`), **L** = paradas de la ruta más larga, **A** y **B** =
apariciones del origen y del destino en la red, **M** = máximo de veces
que una estación se repite en una misma ruta, **C** = estaciones cerradas.

| Operación | Complejidad |
|---|---|
| Construir el índice (una vez por red) | O(P log P) |
| Saber si una estación existe | O(log P) |
| Preparar los prefijos de cierres | O(P × (C + 1)) |
| Fase de directos | O(A × (log L + M)) |
| Fase de un transbordo (peor caso) | O(A × B × L × (log L + M)) |

En la práctica A y B son pequeños comparados con P: en `Datos/` una
estación aparece en promedio en 13 rutas (máximo 45) de 1.927 paradas, y
L = 33. En la red GTFS el promedio es 16 (máximo 166) de 58.132, y L = 176.
R5 no se mide en rendimiento (diap. 11). El detalle completo está en
`DOCUMENTACION_R5.md`.

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

Por esta razón, no se incluye directamente en el repositorio GitHub:
GitHub rechaza archivos de más de 100 MB. Sí se incluyen
`Datos_corregidos/estaciones.csv` y `Datos_corregidos/rutas.csv`.

Para utilizar los datos convertidos, primero debe ejecutarse
el conversor con un archivo GTFS válido.

Los archivos de Datos/ corresponden al conjunto académico
utilizado durante el desarrollo y se conservan por separado.

La estructura y los identificadores de las rutas pueden variar
según la versión del GTFS utilizada.