# RUTAVIVA — DOCUMENTACIÓN TÉCNICA DEL REQUISITO R5

## Responsable

Integrante 3 — Planeación de viajes y conversión GTFS.

## 1. Objetivo del requisito R5

Desarrollar un algoritmo que permita encontrar un recorrido
entre dos estaciones, utilizando un servicio directo o un
máximo de un transbordo.

El algoritmo debe seleccionar el viaje que implique la menor
cantidad de tramos recorridos, respetando el sentido de las
rutas y evitando las estaciones cerradas.

## 2. Estructuras de datos utilizadas

### Listas de estaciones

Las estaciones se almacenan en listas de nombres.

Se eligió esta estructura porque el profesor permite utilizar
listas como arreglos y prohíbe diccionarios y conjuntos dentro
del motor.

### Listas de rutas

Cada servicio contiene su identificador y una lista de paradas
organizadas según el orden del recorrido.

Esto permite consultar las estaciones en el sentido en que
circula cada servicio.

### Índices ordenados

Se construyen índices que relacionan estaciones con servicios
y posiciones dentro de cada ruta.

Estos índices permiten localizar rutas candidatas sin tener
que recorrer necesariamente toda la red en cada consulta.

## 3. Algoritmos seleccionados

### 3.1 Merge Sort

Se implementó un algoritmo propio de ordenamiento por mezcla
para organizar los registros alfabéticamente.

Complejidad temporal: O(n log n).

Complejidad espacial adicional: O(n) para la combinación,
sin contar los detalles de las copias y llamadas recursivas.

Alternativa descartada: sorted() y list.sort().

Motivo: están prohibidas por las instrucciones del proyecto.

### 3.2 Búsqueda binaria

Se implementó una función que encuentra la primera posición
cuyo nombre es mayor o igual al nombre buscado.

Complejidad temporal: O(log n), suponiendo comparaciones
de nombres de costo constante.

Alternativa descartada: búsqueda secuencial de todas las
estaciones en cada consulta.

Motivo: recorrer todos los registros requiere O(n), mientras
que la búsqueda binaria aprovecha el ordenamiento previo.

### 3.3 Búsqueda de viajes directos

El algoritmo identifica los servicios que pasan por el origen
y verifica si también contienen el destino en una posición
posterior.

Solo acepta recorridos que respetan el sentido del servicio
y que no atraviesan estaciones cerradas.

### 3.4 Búsqueda con un transbordo

Si es necesario, el algoritmo evalúa conexiones entre un
primer servicio que pasa por el origen y un segundo servicio
que llega al destino.

El punto de transbordo debe encontrarse después del origen
en el primer servicio y antes del destino en el segundo.

El algoritmo compara las alternativas válidas y selecciona
la que tiene menor cantidad de tramos.

### 3.5 Estaciones cerradas

Se utiliza una estructura de sumas acumuladas por recorrido
para comprobar si un tramo contiene estaciones cerradas.

Una vez construida esa estructura, la consulta de cierre
de un tramo se realiza en O(1).

La preparación debe repetirse cuando cambie el estado
de cierre de la red.

## 4. Casos de prueba realizados

Se comprobaron los siguientes casos:

- Viaje directo.
- Viaje con un transbordo.
- Origen igual al destino.
- Estación inexistente.
- Estación cerrada.
- Modificación de una ruta y reconstrucción del índice.
- Selección del recorrido con menos tramos.
- Estaciones repetidas dentro de una misma ruta.

Las pruebas anteriores resultaron satisfactorias en las
redes de ejemplo utilizadas.

## 5. Pendientes de integración

- Conectar R5 con la clase Red del integrante 1.
- Confirmar el formato de retorno exigido por el profesor.
- Conectar cierres y reaperturas con R8.
- Actualizar el índice después de modificaciones de R7.
- Comprobar el funcionamiento de deshacer y rehacer de R9.
- Documentar la complejidad completa de la búsqueda R5.
- Integrar la documentación de R5 en el README del grupo.

---

# DOCUMENTACIÓN DEL CONVERSOR GTFS

## 6. Objetivo del conversor

El conversor GTFS permite transformar información de transporte
en los tres archivos CSV que utiliza el planeador RutaViva.

El programa se encuentra en:

Conversion/convertir.py

Los archivos generados son:

- estaciones.csv
- rutas.csv
- horarios.csv

## 7. Estructuras de datos utilizadas

El conversor utiliza listas, diccionarios y conjuntos para
procesar y organizar la información del GTFS.

Estas estructuras están permitidas porque el conversor se
encuentra fuera del paquete motor.

Los diccionarios permiten relacionar identificadores GTFS con
sus correspondientes estaciones, servicios y recorridos.

Los conjuntos permiten eliminar duplicados.

Las listas permiten almacenar secuencias de estaciones y
eventos de horarios.

## 8. Generación de estaciones.csv

El archivo contiene una columna:

nombre

El conversor selecciona las estaciones utilizadas en los
recorridos válidos, elimina duplicados y organiza los nombres
alfabéticamente.

Los nombres deben mantenerse normalizados en mayúsculas y
sin tildes, según el formato del proyecto.

## 9. Generación de rutas.csv

El archivo contiene las columnas:

ruta,orden,estacion

Cada variante de recorrido recibe un identificador propio.

Las paradas se registran según su orden de recorrido,
comenzando desde 1.

Se conservan las variantes de servicio en un único sentido
para que el algoritmo R5 pueda respetar la dirección del viaje.

## 10. Generación de horarios.csv

El archivo contiene las columnas:

ruta,estacion,hora

El conversor recorre los eventos de los viajes GTFS y escribe
la ruta, la estación y la hora de paso correspondiente.

Los eventos sin hora disponible se omiten.

## 11. Tratamiento de horarios superiores a 23:59

El formato GTFS permite representar horas posteriores
a medianoche mediante valores como 24:15 o 25:10.

El formato académico requerido utiliza horas HH:MM.

Por esta razón, se decidió aplicar módulo 24 a la hora.

Ejemplos:

23:45:00 -> 23:45
24:15:00 -> 00:15
25:10:00 -> 01:10
26:30:00 -> 02:30

La operación utilizada es:

hora_convertida = hora_original % 24

Esta decisión permite mantener las horas entre 00:00 y 23:59.

Limitación:

Se pierde la información que indica si un evento corresponde
al día siguiente.

Por tanto, el CSV generado no permite reconstruir por sí
solo la fecha operativa original de esos eventos.

## 12. Decisiones de diseño

Se utilizan identificadores diferentes para las variantes
de recorridos, evitando confundir servicios con trayectos
distintos.

Se generan archivos CSV con los encabezados exactos del
formato académico.

Se utilizan estructuras de datos permitidas fuera del motor
para procesar eficientemente la información GTFS.

## 13. Validaciones realizadas

Durante el desarrollo se verificaron los archivos GTFS
convertidos, incluyendo:

- Existencia de estaciones utilizadas por los recorridos.
- Relación entre servicios y estaciones.
- Relación entre horarios y recorridos.
- Formato válido HH:MM para los horarios.
- Identificadores de recorridos sin duplicados.

Estas validaciones se realizaron sobre los datos convertidos
utilizados durante el desarrollo.

No sustituyen las pruebas de integración del proyecto completo.

## 14. Limitaciones y pendientes

- Los resultados dependen del archivo GTFS utilizado.
- Los horarios superiores a 23:59 pierden el indicador de día.
- El archivo horarios.csv convertido puede superar los 375 MB.
- El archivo grande no se incluye directamente en GitHub.
- El README final deberá explicar cómo regenerar los CSV.
- La integración definitiva dependerá de la clase Red del grupo.

---

# ANÁLISIS DE COMPLEJIDAD DE R5

## 15. Variables utilizadas

Para expresar la complejidad computacional se definen:

- R: cantidad de rutas.
- P: cantidad total de apariciones de paradas en las rutas.
- C: cantidad de estaciones cerradas.
- n: cantidad de registros de un arreglo ordenado.

## 16. Ordenamiento de registros

La función ordenar_por_nombre utiliza Merge Sort.

Complejidad temporal: O(n log n).

El algoritmo divide los registros en mitades y posteriormente
combina los resultados ordenados.

## 17. Búsqueda binaria

La función limite_inferior utiliza búsqueda binaria.

Complejidad temporal: O(log n).

Su funcionamiento requiere que los registros estén ordenados.

## 18. Verificación de estaciones cerradas

La función esta_cerrada recorre una lista de estaciones cerradas.

Complejidad temporal: O(C).

En el peor caso debe comparar todos los nombres registrados
en esa lista.

## 19. Preparación de prefijos acumulados

La función preparar_prefijos_cierres recorre las P apariciones
de paradas de la red.

Por cada parada ejecuta esta_cerrada.

Complejidad temporal: O(P x C), como cota superior.

Cuando no existen estaciones cerradas, el recorrido de las
paradas mantiene un costo O(P).

Complejidad espacial adicional: O(P + R), correspondiente
a los arreglos de prefijos de las rutas.

## 20. Consulta de disponibilidad de un tramo

La función tramo_disponible consulta dos posiciones del arreglo
de prefijos y calcula su diferencia.

Complejidad temporal: O(1).

Esta decisión evita recorrer todas las estaciones del tramo
cada vez que se evalúa un posible viaje.

## 21. Comparación de recorridos candidatos

La función elegir_mejor compara un número fijo de valores
entre dos alternativas.

Complejidad temporal: O(1).

El algoritmo prioriza la menor cantidad de tramos cuando
se utiliza el criterio "paradas".

En caso de empate entre un recorrido directo y uno con
transbordo, favorece el directo.

## 22. Búsqueda completa de R5

## 22. Complejidad completa de la búsqueda R5

El algoritmo R5 identifica recorridos directos o con un máximo de un transbordo, seleccionando la alternativa con menor cantidad de tramos.

Para analizar su complejidad se definen las siguientes variables:

- P: número total de apariciones de paradas en todas las rutas.
- C: número de estaciones cerradas.
- A: número de apariciones de la estación de origen.
- B: número de apariciones de la estación de destino.
- L: número máximo de paradas de una ruta.
- M: número máximo de apariciones de una misma estación dentro de una ruta.

### 22.1. Búsqueda de recorridos directos

El algoritmo examina las apariciones del origen y busca las posiciones del destino en cada servicio correspondiente.

La búsqueda de posiciones utiliza índices ordenados y búsqueda binaria.

La complejidad temporal de esta fase está acotada por:

**O(A × (log L + M))**

### 22.2. Búsqueda de recorridos con transbordo

El algoritmo evalúa combinaciones de servicios que pasan por el origen y servicios que llegan al destino.

Para cada combinación examina posibles estaciones de cambio y utiliza búsqueda binaria para encontrar sus posiciones en el segundo servicio.

La complejidad temporal de esta fase está acotada por:

**O(A × B × L × (log L + M))**

Esta cota corresponde al peor caso y puede disminuir cuando se descartan recorridos o se encuentran estaciones cerradas.

### 22.3. Preparación de estaciones cerradas

Antes de examinar los recorridos, el algoritmo construye arreglos de prefijos acumulados.

Su complejidad temporal es:

**O(P × (C + 1))**

Después de esta preparación, comprobar si un tramo atraviesa una estación cerrada requiere O(1).

### 22.4. Complejidad temporal total

Considerando las búsquedas iniciales de origen y destino, la preparación de prefijos y la evaluación de recorridos, se obtiene la siguiente cota superior:

**O(P × (C + 1) + log P + A + B + A × B × L × (log L + M))**

Esta expresión supone que los índices de viajes ya fueron construidos y se reutilizan.

Si se construye un índice nuevo, debe añadirse su costo de preparación.

### 22.5. Justificación de la solución

Se eligió utilizar índices ordenados y búsqueda binaria para reducir las consultas innecesarias sobre las rutas.

Los prefijos acumulados permiten verificar rápidamente la disponibilidad de los recorridos.

La búsqueda se limita a viajes directos o con un máximo de un transbordo, respetando el alcance del requisito R5.

Aunque la búsqueda con transbordo puede presentar un costo elevado en el peor caso, evita examinar combinaciones que no tengan relación con el origen o el destino.

La implementación prioriza la corrección de los resultados y el cumplimiento de las restricciones de estructuras de datos establecidas por el profesor.

## 23. Alternativas consideradas

Para comprobar cierres en los recorridos se consideró
recorrer todas las estaciones de cada tramo.

Se eligieron prefijos acumulados porque permiten consultar
posteriormente la disponibilidad de un tramo en O(1).

Esta alternativa requiere preparación previa y memoria
adicional, pero evita repetir recorridos completos al
evaluar distintas opciones de viaje.