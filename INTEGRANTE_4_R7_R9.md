# Integrante 4 — Operar la red (R7, R8, R9)

Archivos: `motor/_comun.py`, `motor/edicion_rutas.py`, `motor/cierres.py`,
`motor/historial.py`, `motor/operar.py`. Pantalla: `Front/operar_red.py`.
Pruebas: `Pruebas/test_r7_rutas.py`, `test_r8_cierres.py`, `test_r9_historial.py`, `test_front_operar.py`.

n = paradas de la ruta · R = número de rutas · c = estaciones cerradas · E = estaciones · h = comandos en el historial.

## R7 — Editar rutas
- **Estructura:** la lista `rutas` del contrato (`[id, [[orden, nombre], ...]]`), modificada **en sitio**, así R5 y R6 ven el cambio sin copias.
- **Algoritmo:** búsqueda lineal de la ruta y de la parada, `insert`/`pop` y renumeración del campo `orden` (1..n) para que la ruta quede coherente.
- **Alternativa descartada:** lista enlazada. Insertar sería O(1) tras encontrar la parada, pero encontrarla sigue siendo O(n), `recorrido` al revés exigiría lista doble, y R5 espera una lista de listas.
- **Complejidad:** `agregar_parada` y `quitar_parada` O(R + n + E) (la verificación de existencia es lineal por defecto y `Red` puede sustituirla); `recorrido` O(R + n).

## R8 — Cerrar y reabrir
- **Estructura:** la lista `cerradas` (contrato) y el auxiliar `_abierta(nombre)`.
- **Alternativa descartada:** marcar cada estación con un booleano o usar una tabla hash propia. Daría `_abierta` en O(1), pero obliga a cambiar la estructura de estaciones que es de otra integrante. Queda como mejora si R1 expone un índice por nombre.
- **Complejidad:** `cerrar` O(E + c); `reabrir` O(E + c); `_abierta` O(c).

## R9 — Deshacer y rehacer
- **Estructura:** patrón Comando + dos pilas (listas con `append`/`pop`). Cada comando (`CmdCerrar`, `CmdReabrir`, `CmdAgregarParada`, `CmdQuitarParada`) sabe `aplicar` y `revertir`; guarda la posición original para restaurar en el mismo sitio.
- **Regla:** un cambio nuevo vacía la pila de rehacer.
- **Alternativa descartada:** guardar una copia completa de `rutas` y `cerradas` en cada cambio. Es más simple, pero cuesta O(tamaño de la red) de memoria y tiempo por cambio; el comando solo guarda lo que cambió.
- **Complejidad:** apilar/desapilar O(1); el costo de cada `deshacer`/`rehacer` es el del comando (O(n) para rutas, O(c) para cierres).

## Decisiones de casos borde (el enunciado no los fija)
| Caso | Decisión |
|---|---|
| Operación inválida | Devuelve `False`, sin excepción, sin tocar la red ni el historial. Éxito → `True`. |
| `recorrido` de ruta inexistente | `[]` |
| `agregar_parada`: ruta inexistente / `despues_de` no está / `nueva` ya está / estación inexistente | Rechaza |
| `agregar_parada` con `nueva` cerrada | **Rechaza** |
| `cerrar` ya cerrada, `reabrir` abierta, nombre inexistente | `False` (no entra al historial) |
| `deshacer`/`rehacer` con pila vacía | `False`, no hace nada |
| Cerrar una estación | No la quita de las rutas; R4/R5 la evitan consultando `cerradas`. `recorrido` sigue mostrándola |
| Entradas | Se normalizan (mayúsculas, sin tildes, sin espacios sobrantes) |

## Cómo integrarlo en `Red` (para la Integrante 1)
```python
# motor/red.py (o donde esté Red)
from .operar import OperarRed

class Red(OperarRed):          # <- una sola línea nueva
    ...                        # Red debe tener self.estaciones, self.rutas, self.cerradas
```
- R2, R3, R6 y R1 deben ocultar/reportar con `self._abierta(nombre)`.
- R6 puede cachear el ranking y compararlo con `self._version` (sube en cada cambio, incluidos deshacer y rehacer).
- Si `Red` ya tiene un índice rápido de estaciones, puede sobrescribir `_existe_estacion`.
