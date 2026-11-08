# RUTAVIVA — INTEGRACIÓN R5

## Responsable
Integrante 3 — Planeación de viajes y conversión GTFS.

## Estado actual
El algoritmo R5 está implementado en Motor/viajes.py.

Se han ejecutado correctamente cinco pruebas con una red
independiente de los datos de TransMilenio.

## 1. Entrada de estaciones

R5 espera una lista de nombres:

estaciones = ["ALFA", "BETA", "GAMMA"]

## 2. Entrada de rutas

R5 espera una lista de servicios con sus paradas ordenadas:

rutas = [
    ["RUTA_A", [[1, "ALFA"], [2, "BETA"], [3, "GAMMA"]]]
]

Cada ruta debe conservar el sentido del recorrido.

## 3. Estaciones cerradas

R5 recibe una lista con los nombres de estaciones cerradas.

Ejemplo:

cerradas = ["GAMMA"]

Esta información deberá provenir del estado compartido
que gestione la clase Red.

## 4. Índice de viajes

Se construye mediante:

indice = IndiceViajes(rutas, estaciones)

Cuando se agregue o elimine una parada, el índice deberá
actualizarse o reconstruirse antes de la siguiente búsqueda.

## 5. Algoritmo de búsqueda

La función actual es:

buscar_mejor_viaje(
    rutas,
    estaciones,
    cerradas,
    origen,
    destino,
    indice=None,
    criterio="paradas"
)

Para el requisito oficial R5 debe utilizarse el criterio
de menor cantidad de paradas.

## 6. Conexión con la clase Red

El profesor exige el método:

red.viaje(origen, destino)

La implementación definitiva debe llamar al algoritmo R5
utilizando los datos compartidos de la clase Red.

Los atributos concretos se acordarán con el integrante 1.

## 7. Resultado actual

El algoritmo devuelve una lista con cinco posiciones:

[tipo, ruta_1, ruta_2, transbordo, cantidad_tramos]

Ejemplos:

["DIRECTO", "RUTA_A", None, None, 2]

["TRANSBORDO", "RUTA_A", "RUTA_B", "GAMMA", 4]

["MISMO DESTINO", None, None, None, 0]

También puede devolver None cuando no existe un recorrido.

IMPORTANTE:
El formato definitivo debe contrastarse con el enunciado
oficial antes de considerarlo compatible con el evaluador.

## 8. Dependencias con otros integrantes

Integrante 1:
Debe proporcionar las estaciones y rutas cargadas.

Integrante 2:
Debe proporcionar los horarios para consultar el próximo bus.

Integrante 4:
Debe gestionar estaciones cerradas, reaperturas y
modificaciones de recorridos.

## 9. Pruebas realizadas

ALFA -> GAMMA:
Directo por RUTA_A, 2 tramos.

ALFA -> EPSILON:
Transbordo en GAMMA, 4 tramos.

ALFA -> ALFA:
Mismo destino, 0 tramos.

ALFA -> ESTACION INVENTADA:
Error por estación inexistente.

ALFA -> EPSILON con GAMMA cerrada:
No existe un recorrido disponible.

## 10. Pendientes

- Integrar R5 con la clase Red.
- Confirmar el formato de retorno exigido por el profesor.
- Comprobar cambios de rutas realizados por R7.
- Comprobar cierres y reaperturas mediante R8.
- Comprobar deshacer y rehacer mediante R9.
- Realizar pruebas de integración con los demás módulos.

---

## 11. Adaptador disponible para la integración

Se creó el módulo:

motor/integracion_r5.py

Este módulo contiene la función:

ejecutar_r5(rutas, estaciones, cerradas, origen, destino)

La función recibe los datos compartidos del motor y ejecuta
el algoritmo R5 utilizando el criterio de menor cantidad
de paradas.

Ejemplo de integración futura con la clase Red:

    def viaje(self, origen, destino):
        return ejecutar_r5(
            self.rutas,
            self.estaciones,
            self.cerradas,
            origen,
            destino
        )

Los atributos de este ejemplo deberán adaptarse a la
estructura definitiva que implemente el integrante 1.

El adaptador reconstruye actualmente el índice de viajes
en cada llamada para trabajar con los recorridos actualizados.

Se realizó una prueba satisfactoria con la red pequeña,
obteniendo un viaje con transbordo entre ALFA y EPSILON.

Pendientes:

- Confirmar el formato de retorno oficial.
- Conectar el estado compartido de estaciones cerradas.
- Verificar modificaciones reales de rutas realizadas por R7.
- Integrar el método viaje en la clase Red definitiva.