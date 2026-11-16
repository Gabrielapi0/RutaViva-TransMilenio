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

## Decisiones técnicas por requisito (R12)

Convenciones: **S** = estaciones, **R** = rutas, **P** = total de paradas de todas las rutas, **E** = eventos de `horarios.csv`, **c** = estaciones cerradas, **k** = tamaño pedido. Cada sección dice qué es *n*.

### R1 – R3 · Estado, autocompletar y rango (Integrante 1)

> **PENDIENTE (Integrante 1):** estructura que guarda las estaciones, por qué sirve para buscar, autocompletar y listar rangos, alternativa descartada y O grande de cada operación.
>
> Estado actual del código, según el panel R11: `estado` recorre las estaciones y las rutas (O(S + P)); `autocompletar` reordena las estaciones en cada llamada (O(S log S)); `rango` recorre todas (O(S)).

### R4 · `proximo_bus(estacion, ruta, hora)` (Integrante 2) — `motor/horarios.py`

- **Devuelve:** `"HH:MM"` del siguiente bus de esa ruta en esa estación, o `None`.
- **Estructura:** dos listas paralelas que se arman al cargar.
  - `claves`: los textos `"ruta␟estacion"`, ordenados.
  - `horas[i]`: los minutos (desde las 00:00) en que pasa cada bus de esa pareja, ordenados.
- **Algoritmo:**
  - Al cargar, los E eventos se ordenan con un **merge sort propio** y se agrupan en una sola pasada.
  - Cada consulta hace **dos búsquedas binarias**: primero ubica la pareja ruta-estación y luego la primera hora mayor o igual a la pedida.
- **O grande:**
  - Carga: O(E log E), con n = E (≈140.500 eventos).
  - Consulta: **O(log G + log H)**, con G = parejas ruta-estación y H = buses de esa pareja.
  - Revisar si la estación está cerrada: O(c).
- **Alternativas descartadas:**
  - Recorrer todos los horarios en cada consulta: O(E).
  - Tabla hash: `dict` está prohibido.
  - Una sola lista de eventos sin agrupar: igual de rápida, pero complica los límites entre parejas e impide contar buses en O(log G), que usa R6.
- **Casos borde:**

| Caso | Decisión |
|---|---|
| La hora coincide con un bus | Ese bus cuenta (`"09:57"` → `"09:57"`) |
| Después del último bus | `None` (contrato: "no hay más ese día") |
| Horas del GTFS ≥ 24:00 | Módulo 24 (`25:10` → `01:10`) |
| Ruta inexistente, estación inexistente, estación fuera de la ruta, ruta sin horarios, hora inválida, estación cerrada | `None` |
| Parada quitada con R7 | `None`; vuelve a responder si se deshace (R9) |
| Parada agregada con R7 | `None`: no tiene horarios propios y no se inventan |

### R5 · `viaje(origen, destino)` (Integrante 3) — `motor/viajes.py`

Viaje directo o con un transbordo que recorre menos paradas, respetando el sentido de las rutas y evitando las estaciones cerradas. Usa:
- merge sort propio para ordenar los registros (O(n log n));
- búsqueda binaria para ubicar estaciones (O(log n));
- prefijos acumulados por ruta que dicen en O(1) si un tramo pasa por una estación cerrada. Prepararlos cuesta O(P · c).

Detalle completo en `DOCUMENTACION_R5.md`. No se mide en rendimiento (diap. 11).

### R6 · `ranking(k)` (Integrante 2) — `motor/ranking.py`

- **Devuelve:** lista de tuplas `(nombre, buses_por_dia)` de las k estaciones abiertas con más buses, de mayor a menor.
- **Qué cuenta:** para cada ruta que hoy para en la estación (según `self.rutas`), los buses diarios de esa ruta en esa estación. Con los datos reales, RICAURTE tiene 4.446.
- **Estructura:** caché en dos niveles.
  1. Todas las estaciones `[nombre, buses]`, ordenadas por buses (de mayor a menor) y luego por nombre.
  2. La misma lista sin las cerradas.
- **Cómo se mantiene al día con R7, R8 y R9:** `OperarRed` sube `self._version` en cada cambio, incluidos `deshacer` y `rehacer`. `ranking` y `proximo_bus` comparan ese número con el último que vieron, lo que cuesta O(1). Si cambió, invalidan la caché, y el recálculo se hace en la siguiente consulta (de forma perezosa). Por eso una estación cerrada sale del ranking y vuelve al reabrirla sin que R8 tenga que avisarle a R6.
- **O grande:**

| Situación | Trabajo | O grande |
|---|---|---|
| `ranking(k)` sin cambios | copiar los k primeros | **O(k)** |
| Después de un cambio | recalcular | O(P log P + S log S) |

- **Alternativas descartadas:**
  - Ordenar en cada consulta: O(S log S) por llamada, cuando la consulta es mucho más frecuente que los cambios.
  - Montículo propio: O(S + k log S) por consulta, peor que O(k).
  - Selección de k (k pasadas sobre la lista): O(k · S).
  - `heapq` y `sorted`: prohibidos.
- **Decisiones:**
  - Empates en buses: orden alfabético.
  - `k ≤ 0` → `[]`.
  - k mayor que las estaciones abiertas → todas las abiertas.
  - Parada agregada con R7 sin horarios: hereda los buses de la parada anterior de su ruta, porque el bus que pasa por `despues_de` sigue a la nueva.
  - Estación repetida dentro de una ruta: se cuenta una sola vez por ruta.

### R7 – R9 · Editar rutas, cerrar/reabrir, deshacer/rehacer (Integrante 4) — `motor/operar.py`

| Req | Estructura y algoritmo | O grande |
|---|---|---|
| R7 | La lista `rutas` del contrato, modificada en sitio (búsqueda lineal de la ruta y de la parada, `insert`/`pop` y renumeración) | `agregar_parada`/`quitar_parada` O(R + n + S), con n = paradas de la ruta; `recorrido` O(R + n) |
| R8 | La lista `cerradas` del contrato | `cerrar`/`reabrir` O(S + c) |
| R9 | Patrón Comando con dos pilas (deshacer y rehacer). Un cambio nuevo vacía la pila de rehacer | apilar y desapilar O(1), más el costo del comando |

Detalle, alternativas y casos borde en `INTEGRANTE_4_R7_R9.md`. `Red` hereda estos métodos de `OperarRed`.

### R10 · `simular_fila(llegadas, frecuencia, capacidad)` (Integrante 1)

> **PENDIENTE (Integrante 1):** cómo se ordenan las llegadas, qué estructura es la fila y su O grande. Debe devolver una lista (por ejemplo, `simular_fila([30, 5, 5, 70], 60, 2)` → `[120, 60, 60, 120]`), no un diccionario.

### R11 · Panel de rendimiento (Integrante 2) — `Front/panel_rendimiento.py`

```powershell
python Front/panel_rendimiento.py
```

- **Cómo mide:**
  1. Copia toda la red (estaciones, rutas y horarios, con sufijos `X2`, `X3`, …) para obtener redes de tamaño n, 2n, 4n y 8n.
  2. Corre cada operación menos R5, toma el mejor de 5 lotes y calcula la **pendiente de log(tiempo) contra log(n)**: 0 es constante y 1 es lineal, el mismo método del profesor.
  3. Guarda `panel_rendimiento.png` con la curva medida junto a la esperada.
- **Explicación de desviaciones:**
  - R4 (pendiente ≈ 0,1) y `ranking` (≈ 0) son planas, como deben ser O(log n) y O(k).
  - `cerrar + ranking + reabrir` sale lineal (≈ 1,1) porque mide también el recálculo del ranking después del cambio.
  - R7, R8 y R9 salen por debajo de 1 aunque son lineales en S: el recorrido lineal es barato frente al costo fijo de cada operación, y esa parte fija pesa más en las redes pequeñas.
  - R1 y R2 crecen lineal aunque se esperaba O(log n). Ver la nota de R1–R3.


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