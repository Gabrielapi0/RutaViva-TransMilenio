# Integración de R4 y R6 (Integrante 2) en la clase `Red`

Archivos nuevos de Integrante 2 (no modifican nada existente):

| Archivo | Contenido |
|---|---|
| `motor/horarios.py` | `IndiceHorarios` (R4), merge sort y búsqueda binaria propios |
| `motor/ranking.py` | `IndiceRanking` (R6) |
| `Front/panel_rendimiento.py` | R11 (fuera del motor, puede usar matplotlib) |
| `Pruebas/test_p2.py` | Pruebas de R4 y R6 |

No se crea una segunda `Red`. Integrante 1 pega estas líneas en su clase.

## 1. Imports (arriba del archivo donde vive `Red`)

```python
from .horarios import IndiceHorarios
from .ranking import IndiceRanking
```

## 2. Al final de `Red.__init__(self, carpeta)`

Después de que existan `self.estaciones`, `self.rutas` y `self.cerradas`:

```python
        # --- Integrante 2 (R4, R6). Atributos privados de P2. ---
        self._horarios = IndiceHorarios(carpeta.rstrip("/\\") + "/horarios.csv")
        self._ranking = IndiceRanking(self._horarios)
```

## 3. Métodos públicos

```python
    def proximo_bus(self, estacion, ruta, hora):
        return self._horarios.proximo(estacion, ruta, hora, self.rutas, self.cerradas)

    def ranking(self, k):
        return self._ranking.top(k, self.estaciones, self.rutas, self.cerradas)

    def _invalidar_p2(self, rutas_cambiaron=True):
        """Llamar después de cualquier cambio de la red."""
        if rutas_cambiaron:
            self._horarios.invalidar()
            self._ranking.invalidar()
        else:
            self._ranking.invalidar_cierres()
```

## 4. Lo que necesito de Integrante 4 (una línea por método)

| Método | Línea al final del método (solo si el cambio se hizo) |
|---|---|
| `cerrar(nombre)` | `self._invalidar_p2(rutas_cambiaron=False)` |
| `reabrir(nombre)` | `self._invalidar_p2(rutas_cambiaron=False)` |
| `agregar_parada(...)` | `self._invalidar_p2()` |
| `quitar_parada(...)` | `self._invalidar_p2()` |
| `deshacer()` | `self._invalidar_p2()` |
| `rehacer()` | `self._invalidar_p2()` |

En `deshacer`/`rehacer` uso la versión completa porque no sé qué tipo de cambio se revierte; cuesta lo mismo que una edición.

Si se olvida esta línea, `ranking()` seguiría mostrando el estado anterior. La prueba `test_integracion_con_red` lo detecta.

## Atributos compartidos que uso (solo lectura)

- `self.estaciones` (list de str)
- `self.rutas` (`[[id, [[orden, estacion], ...]], ...]`)
- `self.cerradas` (list de str)

No los copio ni los modifico. Si Integrante 1 cambia sus nombres, solo hay que cambiar las tres líneas del punto 3.
