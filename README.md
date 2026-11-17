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

### R1 – R3 · Estado, autocompletar y rango (Integrante 1) — `motor/__init__.py`, `motor/tabla_hash.py`, `motor/orden.py`

| Req | Estructura y algoritmo | O grande |
|---|---|---|
| R1 `estado` | **Tabla hash propia** (`TablaHash`): nombre de estación → lista de rutas que paran en ella. Encadenamiento separado, hash polinomial (`h·33 + ord(c)`) módulo un primo, y duplica las cubetas cuando hay más elementos que cubetas. Se arma la primera vez que se consulta, en O(S + P), y solo se rearma si R7/R9 cambiaron las rutas (se compara `_version`, O(1)). | **O(1)** esperado + O(c) para saber si está cerrada |
| R2 `autocompletar` | **Arreglo ordenado** de estaciones, ordenado **una sola vez** al cargar con merge sort propio (O(S log S)). **Búsqueda binaria** (`limite_inferior`) del primer nombre ≥ prefijo y avance mientras empiece por el prefijo, saltando las cerradas. | **O(log S + k)** (× c por revisar cierres) |
| R3 `rango` | El mismo arreglo ordenado: búsqueda binaria de `desde` y avance hasta pasar `hasta`, saltando las cerradas. | **O(log S + m)**, m = estaciones en el rango |

- **Devuelve:** `estado(nombre)` → `"ABIERTA"`, `"CERRADA"` o `"NO EXISTE"`. `autocompletar` y `rango` → lista de nombres. (Las rutas de una estación, que usa la app, salen de `red.rutas_de(nombre)`, un extra fuera del contrato).
- **Por qué:** R1 solo pregunta por un nombre exacto, así que la tabla hash da O(1) sin pagar un orden que no usa. R2 y R3 necesitan orden alfabético: en un arreglo ordenado, todos los nombres con un mismo prefijo o dentro de un rango quedan seguidos, y la búsqueda binaria encuentra el inicio en log S. Las estaciones no cambian durante la ejecución, así que basta con ordenar una vez.
- **Alternativas descartadas:**
  - Recorrer la lista en cada consulta: O(S) en R1 y R3. Era la primera versión, y el panel mostraba que el tiempo se duplicaba al duplicar la red.
  - Reordenar en cada llamada: O(S log S) por consulta.
  - Un trie para R2: mismo costo para prefijos, pero no sirve para rangos y usa mucha más memoria.
  - Un árbol AVL: sirve si se insertan estaciones seguido; aquí no hace falta.
- **Bordes:** el nombre se normaliza (espacios y MAYÚSCULAS); `k <= 0` → `[]`; `desde > hasta` → `[]`; las estaciones cerradas no salen en R2 ni en R3, y R1 las reporta como `CERRADA`.
- **Medición (R11):** al duplicar la red, R1 crece ×1,08 y R2 ×1,07 (casi planas, como O(1) y O(log S + k)). R3 crece con m porque las copias de la red caen dentro del rango.

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

- **Devuelve:** lista de tramos `(ruta, sube_en, baja_en)`. Directo: `[("8-3", "PORTAL NORTE", "TOBERIN")]`; con transbordo: `[("1-1", "UNIVERSIDADES", "RECINTO FERIAL"), ("K43-2", "RECINTO FERIAL", "PORTAL ELDORADO")]`. `None` si no hay viaje o si el origen o el destino no existe o está cerrado; `[]` si origen y destino son la misma estación. La conversión del resultado interno a tramos está en `motor/integracion_r5.py`.

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
| R7 | La lista `rutas` del contrato, modificada en sitio. La ruta se ubica con una **tabla hash propia** (id → ruta) que se arma una sola vez; dentro de la ruta, `insert`/`pop` y renumeración | `agregar_parada`/`quitar_parada` **O(n)**, con n = paradas de la ruta (ubicar la ruta es O(1)); `recorrido` O(n) |
| R8 | La lista `cerradas` del contrato. La existencia de la estación se valida con una **tabla hash propia** de nombres, armada una sola vez | `cerrar`/`reabrir` **O(1)** para validar + O(c), con c = estaciones cerradas |
| R9 | Patrón Comando con dos pilas (deshacer y rehacer). Un cambio nuevo vacía la pila de rehacer | apilar y desapilar O(1), más el costo del comando |

Detalle, alternativas y casos borde en `INTEGRANTE_4_R7_R9.md`. `Red` hereda estos métodos de `OperarRed`.

### R10 · `simular_fila(llegadas, frecuencia, capacidad)` (Integrante 1) — `motor/fila.py`

- **Entrada y salida:** `llegadas[i]` es el minuto en que llega el pasajero i. Devuelve una **lista** del mismo largo con el minuto en que sube cada uno, en el mismo orden. Ejemplo: `simular_fila([30, 5, 5, 70], 60, 2)` → `[120, 60, 60, 120]`.
- **Algoritmo:**
  1. Se ordenan los **índices** de los pasajeros por hora de llegada con **merge sort propio y estable** (`ordenar_indices`). Si dos llegan al mismo tiempo, sube primero el que aparece antes en la lista.
  2. Todos entran en ese orden a una **cola FIFO enlazada propia** (`Cola`: encolar y desencolar O(1)).
  3. Se desencola uno por uno. Si el bus actual todavía no ha salido para él (llegó antes o justo en el minuto de salida) y le queda cupo, sube. Si no, toma el siguiente bus: el primer múltiplo de la frecuencia que sea ≥ su llegada, y si ese bus ya salió lleno, el siguiente.
- **Decisiones:** el primer bus sale en `t = frecuencia`. Quien llega justo en el minuto de salida alcanza a subir. Con `frecuencia` o `capacidad` ≤ 0 se devuelve una lista de ceros.
- **O grande:** **O(p log p)** por el ordenamiento, más O(p) de la simulación, con p = pasajeros. Si las llegadas ya vienen ordenadas, la simulación en sí es lineal. Panel R11: ×2,35 al duplicar, frente a ×2,11 esperado.
- **Alternativas descartadas:**
  - Simular minuto a minuto: depende de cuánto dura la hora pico, no de los pasajeros.
  - Una lista con `pop(0)`: cada salida cuesta O(p), en total O(p²), inviable con cientos de miles de pasajeros.

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

El conversor está en `Conversion/convertir.py` y solo usa la librería estándar de Python.

Fuente: GTFS estático de TransMilenio del **14 de julio de 2021** (`GTFS-2021-07-14.zip`, unos 54 MB), publicado en el portal de datos de movilidad de Bogotá. El zip no se sube al repositorio.

```powershell
python Conversion/convertir.py --entrada GTFS-2021-07-14.zip --salida Datos_convertidos
```

Opciones: `--fecha AAAA-MM-DD` (día de servicio; por defecto 2021-07-14) y `--todas` (incluye todo el SITP, no solo troncales). Por seguridad, el script no escribe sobre `Datos/`.

### Reglas de la conversión

1. **Solo rutas troncales** (`route_desc = TRONCAL`). Alimentadores, zonales y demás servicios del SITP quedan fuera.
2. **Un solo día de servicio**: el miércoles 14/07/2021, según `calendar.txt` y `calendar_dates.txt`. Así "buses al día" (R6) cuenta un día real.
3. **Nombre de estación**: en MAYÚSCULAS, sin tildes ni símbolos (`º`) y sin el vagón o la plataforma. Por ejemplo, `Calle 19 B - 4 ó 6` queda como `CALLE 19`, y `Portal Eldorado T-6B` queda como `PORTAL ELDORADO`.
4. Si un viaje pasa dos veces por la misma estación, se conserva **la primera**, porque una ruta no repite estaciones.
5. **Cada patrón distinto de estaciones** de una ruta comercial es una ruta del CSV **en un solo sentido**. Si la ruta tiene una sola variante, conserva su nombre (`D51`); si tiene varias, se numeran (`B10-1`, `B10-2`).
   - Se descartan los patrones con **menos de 4 viajes al día**.
   - Un patrón que es solo **un pedazo de otro más largo** (una media vuelta, por ejemplo la K43 que termina en CAD) no es una ruta propia: sus horarios se suman a la variante que lo contiene.
   - Las variantes se numeran **de la que tiene más viajes a la que tiene menos**.
6. **Horas mayores a 24:00**: `25:10` se convierte en `01:10` (módulo 24), porque el usuario pregunta con la hora del reloj y el formato pedido es `HH:MM`. Se pierde la indicación de que el viaje es del día siguiente.

### Comparación con `Datos/`

Con el GTFS del 14/07/2021, el script genera las **mismas 147 estaciones** y **las 181 rutas con el mismo recorrido** (177 también con el mismo nombre; en 5-1/5-2 y G30-1/G30-2 el número se intercambia porque tienen casi la misma cantidad de viajes). El **97,8 %** de las filas de horarios coinciden exactamente.

## Uso académico

Proyecto desarrollado con fines educativos para aplicar conceptos de estructuras de datos, algoritmos de búsqueda, ordenamiento y procesamiento de información.
