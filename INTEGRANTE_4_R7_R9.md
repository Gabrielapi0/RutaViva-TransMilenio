# Integrante 4 — Operar la red (R7, R8, R9)

Archivos: `motor/operar.py` (clase `OperarRed`, de la que hereda `Red`), `motor/indices.py`,
`motor/edicion_rutas.py`, `motor/cierres.py`, `motor/historial.py`, `motor/_comun.py`.
Pantalla: `Front/operar_red.py`. Medición: `Pruebas/medir_rendimiento_int4.py`.
Pruebas: `test_r7_rutas.py`, `test_r8_cierres.py`, `test_r9_historial.py`, `test_contrato_red.py`,
`test_indices_y_contrato.py`, `test_front_operar.py`.

**n** de cada operación: R = número de rutas · p = paradas de la ruta editada · E = estaciones · c = estaciones cerradas.

## R7 — Editar rutas
- **Estructura:** la lista `rutas` del contrato (`[id, [[orden, nombre], ...]]`), modificada **en sitio**, así R5, R6 y R4 ven el cambio sin copias. Para ubicar una ruta por su id se arma **una vez** una `TablaHash` (la del equipo, `motor/tabla_hash.py`): id normalizado → el *mismo objeto* ruta de `Red.rutas`. Por eso los cambios en sitio se siguen viendo. Se rearma sola si `rutas` cambia de objeto o de tamaño.
- **Algoritmo:** buscar la ruta en la tabla → buscar la parada dentro de la ruta (lineal) → `insert`/`pop` y renumeración de `orden` solo desde la posición tocada.
- **Alternativas descartadas:** recorrer `rutas` comparando ids (O(R), duplicaba el tiempo al duplicar la red) y una lista ordenada con búsqueda binaria (O(log R), también plana pero más lenta que el hash).
- **Alternativa descartada (paradas):** lista enlazada. Encontrar la parada sigue siendo O(p), el recorrido al revés exigiría lista doble y R5 espera una lista de listas.
- **Complejidad:** `agregar_parada` O(1) (ruta) + O(p) (parada) + O(1) (validar estación) · `quitar_parada` O(1) + O(p) · `recorrido` O(1) + O(p), con p = tamaño de la respuesta. La tabla se arma una vez: O(R) (peor caso O(R) por consulta solo si todas las claves colisionan, improbable con `2R + 16` cubetas).

## R8 — Cerrar y reabrir
- **Estructura:** `cerradas` (contrato), mantenida **ordenada**, y `_abierta(nombre)`. Para validar que la estación existe se usa otra `TablaHash` (nombre → True), armada una vez; las estaciones no cambian al operar.
- **Algoritmo:** validar con la tabla, y búsqueda binaria + inserción/borrado en su sitio ordenado dentro de `cerradas`.
- **Alternativa descartada:** `cerradas` sin orden con búsqueda lineal (O(c) en cada consulta de R1–R6) y validar la estación recorriendo `estaciones` (O(E)).
- **Complejidad:** `_abierta` O(log c) · `cerrar`/`reabrir` O(1) validar + O(log c) buscar + desplazamiento de la lista al insertar/borrar (`insert`/`pop`, constante muy pequeña; O(c) en teoría).

## R9 — Deshacer y rehacer
- **Estructura:** patrón Comando con dos pilas (listas con `append`/`pop`). Cada comando (`CmdCerrar`, `CmdReabrir`, `CmdAgregarParada`, `CmdQuitarParada`) sabe `aplicar` y `revertir`; los de rutas guardan el objeto ruta y la posición, así no la buscan de nuevo.
- **Regla:** un cambio nuevo vacía la pila de rehacer; lo rechazado no entra al historial; deshacer/rehacer sin nada devuelven `False`.
- **Alternativa descartada:** guardar copias completas de `rutas` y `cerradas` en cada cambio: O(tamaño de la red) por paso.
- **Complejidad:** `deshacer`/`rehacer` O(p) para rutas y O(log c) para cierres (apilar/desapilar es O(1)).

## Medición (mediana de 201 repeticiones; pendiente 0 = constante, 1 = lineal)
Redes sintéticas de 10.000 a 80.000 estaciones, `E/10` rutas de 25 paradas: `python Pruebas/medir_rendimiento_int4.py`.

| operación | 10.000 | 80.000 | pendiente antes | pendiente ahora |
|---|---|---|---|---|
| recorrido | 160 µs → 4.8 µs | 1323 µs → 6.1 µs | 1.01 | 0.12 |
| cerrar | 71 µs → 3.2 µs | 743 µs → 3.6 µs | 1.13 | 0.06 |
| reabrir | 74 µs → 2.8 µs | 754 µs → 2.6 µs | 1.12 | −0.05 |
| agregar_parada | 506 µs → 6.5 µs | 4439 µs → 7.3 µs | 1.04 | 0.05 |
| quitar_parada | 340 µs → 4.1 µs | 2692 µs → 3.9 µs | 1.00 | −0.03 |
| deshacer | 154 µs → 1.0 µs | 1392 µs → 1.0 µs | 1.06 | −0.02 |
| rehacer | 154 µs → 1.2 µs | 1273 µs → 1.1 µs | 1.02 | −0.02 |

(Si el profesor usa rutas cuyo largo p crece con la red, `agregar`/`quitar`/`recorrido` crecen con p, lo mínimo con una lista. Las tablas se arman en la primera operación; para armarlas al cargar, agregar `self._preparar_operaciones()` al final de `Red.__init__`.)

## Decisiones de casos borde (el enunciado oficial solo fija los retornos)
| Caso | Decisión |
|---|---|
| Retornos | `agregar_parada`, `quitar_parada`, `cerrar`, `reabrir`, `deshacer`, `rehacer`: `True` si cambió algo, `False` si no (sin excepción, sin tocar red ni historial). `recorrido`: lista, `[]` si la ruta no existe. |
| `agregar_parada`: ruta inexistente / `despues_de` no está / `nueva` ya está / estación inexistente | `False` |
| `agregar_parada` con `nueva` cerrada | `False` (decisión del equipo) |
| `cerrar` ya cerrada, `reabrir` abierta, nombre inexistente | `False` (no entra al historial) |
| `deshacer`/`rehacer` con pila vacía | `False` |
| Cerrar una estación | No la quita de las rutas; R4/R5 la evitan consultando `cerradas`. `recorrido` sigue mostrándola |
| Entradas | Se normalizan (mayúsculas, sin tildes, sin espacios sobrantes); la Ñ no se toca |

## Cómo conectarlo y qué deben respetar los demás
- `Red` hereda de `OperarRed` y **no debe redefinir** `agregar_parada`, `quitar_parada`, `recorrido`, `cerrar`, `reabrir`, `deshacer` ni `rehacer` (un método definido en `Red` pisa al heredado). Como seguro, `instalar_operaciones(Red)` los copia sobre la clase.
- **Todos** deben leer los cierres con `self._abierta(nombre)` o `self.cerradas`; nadie debe modificar `self.rutas` ni `self.cerradas` por fuera de estos métodos (el historial se desincronizaría). `cerradas` se mantiene ordenada.
- Cada cambio real sube `self._version` (también deshacer/rehacer): R4/R6 y R1 comparan ese entero para invalidar su caché.
- Comprobar: `python Pruebas/test_contrato_red.py` (revisa la clase `Red` real).
