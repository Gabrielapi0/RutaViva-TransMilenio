# Documentación técnica — Integrante 2 (R4, R6, R11)

Este texto va en el README final (R12), en las secciones R4 y R6.

---

## R4 · `proximo_bus(estacion, ruta, hora)`

**Archivo:** `motor/horarios.py` (clase `IndiceHorarios`)

**Entrada:** nombre de estación (str), id de ruta (str), hora `"HH:MM"` (str).
**Salida:** `"HH:MM"` del siguiente bus, o `None`.

### Estructura y algoritmo
Al cargar, cada fila de `horarios.csv` se convierte en un texto `ruta␟estacion␟HH:MM` y se ordenan todos con un **merge sort propio**. Luego, en una sola pasada, se agrupan en dos listas paralelas:

- `claves`: `"ruta␟estacion"` ordenadas alfabéticamente (G ≈ 1.927 parejas con los datos reales).
- `horas[i]`: minutos desde las 00:00 en que pasa un bus de esa pareja, ordenados (H buses).

Una consulta hace **dos búsquedas binarias**: primero ubica la pareja en `claves` y luego la primera hora mayor o igual a la consultada en `horas[i]`.

| Operación | Complejidad | n |
|---|---|---|
| Carga | O(E log E) | E = eventos de horarios.csv (≈140.500) |
| `proximo_bus` | O(log G + log H) | G = parejas ruta-estación, H = buses de esa pareja |
| Comprobar si está cerrada | O(c) | c = estaciones cerradas (pocas) |

### Alternativas descartadas
- **Recorrer todas las filas en cada consulta:** O(E) por consulta, unos 140.000 pasos. Se descartó porque la consulta se hace mucho y la carga solo una vez.
- **Una sola lista de eventos ordenada y una búsqueda binaria:** es igual de rápida, pero hay que manejar el caso en que la siguiente hora sea de otra pareja. Agrupar deja el código más simple y permite contar buses en O(log G) para R6.
- **Tabla hash (ruta, estación):** O(1) promedio, pero `dict` está prohibido. Implementarla a mano no mejora la búsqueda binaria de forma que se note.
- **Ordenar solo por hora con counting sort (1.440 minutos):** sigue haciendo falta ordenar por pareja, así que no se elimina el O(E log E).

### Decisiones de casos borde
| Caso | Decisión |
|---|---|
| La hora coincide con un bus | **Cuenta**: el bus está en la estación ese minuto. `"09:57"` → `"09:57"` |
| Después del último bus del día | **Se pasa al día siguiente** y se devuelve el primer bus, porque el servicio se repite a diario. Se cambia con `ENVOLVER_AL_DIA_SIGUIENTE = False` (en ese caso devuelve `None`). |
| Horas del GTFS ≥ 24:00 | Módulo 24: `25:10` → `01:10` (madrugada del día siguiente). |
| Ruta inexistente / estación inexistente / estación que no está en la ruta / ruta sin horarios / hora inválida / estación cerrada | `None`. `consultar()` devuelve también el motivo para mostrarlo en el front. |
| Parada quitada con R7 | `None`: ya no está en `self.rutas`. Si se deshace (R9), vuelve a responder. |
| Parada agregada con R7 | `None` (sin horarios): no se inventan horas. |
| Buses repetidos en el mismo minuto | Se conservan (son buses distintos del GTFS). |

**Ejemplo real:** `proximo_bus("UNIVERSIDADES", "1-1", "10:00")` → `"10:08"`; con `"23:30"` → `"09:57"` (primer bus del día siguiente).

---

## R6 · `ranking(k)`

**Archivo:** `motor/ranking.py` (clase `IndiceRanking`)

**Entrada:** k (int). **Salida:** lista con los nombres de las k estaciones abiertas con más buses al día.

### Qué se cuenta
Buses al día de una estación = suma, sobre las rutas que hoy paran en ella según `self.rutas`, de los eventos de horario de esa ruta en esa estación. Con los datos reales, RICAURTE tiene 4.446.

### Estructura y algoritmo: caché en dos niveles, recalculada solo cuando se invalida
1. `_orden_total`: todas las estaciones `[nombre, buses]` ordenadas por buses (de mayor a menor) y nombre (A→Z). Depende de las rutas.
2. `_abiertas`: la misma lista sin las cerradas. Depende de los cierres.

| Situación | Trabajo | Complejidad |
|---|---|---|
| `ranking(k)` con caché válida | copiar k elementos | **O(k)** |
| Tras `cerrar` / `reabrir` | rehacer solo el nivel 2 | O(S log c) |
| Tras `agregar_parada` / `quitar_parada` / `deshacer` / `rehacer` | rehacer los dos niveles | O(P log P + S log S) |

S = estaciones, P = total de paradas de todas las rutas, c = cerradas. El recálculo es **perezoso**: invalidar solo marca la caché y el trabajo se hace en la siguiente llamada a `ranking`.

### Alternativas descartadas
- **Ordenar en cada consulta:** O(S log S) por llamada, cuando la consulta es mucho más frecuente que los cambios.
- **Montículo (heap) propio con extracción de k:** O(S + k log S) por consulta. Sigue siendo peor que O(k) con la caché.
- **Selección parcial de k (k pasadas):** O(k·S). Es buena si k es pequeño y la red cambia todo el tiempo, que no es el caso.

### Decisiones
- **Empates:** mismo número de buses → orden alfabético.
- **k ≤ 0** o no entero → `[]`. **k mayor que las abiertas** → todas las abiertas.
- Las estaciones abiertas sin buses aparecen al final con 0.
- **Parada nueva (R7) sin horarios:** hereda los buses de la parada anterior de su ruta (el bus que pasa por `despues_de` sigue a la nueva). Si es la primera, hereda de la siguiente.
- Una estación repetida dentro de una ruta se cuenta una sola vez por ruta.

---

## R11 · Panel de rendimiento

**Archivo:** `Front/panel_rendimiento.py`. Está fuera del motor, así que usa matplotlib.

Fabrica redes de tamaño n, 2n y 4n copiando cada estación, ruta y evento con sufijo `X2`, `X3`, `X4`. Corre cada operación (menos R5) y grafica t(f·n)/t(n) junto a la curva de la O esperada.

### Explicación de desviaciones observadas
- **R4 y R6 (`ranking`) dan razones un poco menores que 1** (≈0,8–0,9): O(log n) crece apenas un 6 % al duplicar, y O(k) no crece. Esa diferencia es más pequeña que el ruido de medir microsegundos (caché de CPU, recolector de basura). El valor está en el rango esperado: no crece.
- **`cerrar + ranking + reabrir` crece ≈1,8× al duplicar:** el nivel 2 de la caché se refiltra recorriendo las S estaciones, así que es lineal en S.
- **R7 no muestra el costo del recálculo del ranking:** la invalidación es perezosa, y ese costo lo paga la siguiente llamada a `ranking`, que es la fila anterior.
- **Carga ≈ 2,0× y 4,6×:** coincide con O(E log E).
