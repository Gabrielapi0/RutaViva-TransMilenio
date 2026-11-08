"""Motor provisional R5: viajes dirigidos con cero o un transbordo.

Solo utiliza listas y el módulo csv, según las restricciones del profesor.
La integración final con Red(carpeta) dependerá del contrato del equipo.
"""

# Importamos el módulo permitido para leer archivos CSV.
import csv


# Comparamos dos registros por su primer elemento (nombre de estación).
def menor_igual(a, b):
    # Se conserva el orden de entrada si ambos nombres son iguales.
    return a[0] <= b[0]


# Ordenamos registros con merge sort propio: NO usamos sorted() ni .sort().
def ordenar_por_nombre(registros):
    # Una lista con cero o un elemento ya está ordenada.
    if len(registros) <= 1:
        # Devolvemos una copia para no alterar la lista original.
        return registros[:]
    # Identificamos el punto medio de la lista.
    medio = len(registros) // 2
    # Ordenamos recursivamente la mitad izquierda.
    izquierda = ordenar_por_nombre(registros[:medio])
    # Ordenamos recursivamente la mitad derecha.
    derecha = ordenar_por_nombre(registros[medio:])
    # Creamos la lista para combinar las dos mitades.
    salida = []
    # Empezamos desde el primer registro de cada mitad.
    i, j = 0, 0
    # Comparamos las mitades mientras ambas tengan elementos.
    while i < len(izquierda) and j < len(derecha):
        # Elegimos primero el nombre alfabéticamente menor o igual.
        if menor_igual(izquierda[i], derecha[j]):
            # Añadimos el registro de la mitad izquierda.
            salida.append(izquierda[i])
            # Avanzamos en la mitad izquierda.
            i += 1
        else:
            # Añadimos el registro de la mitad derecha.
            salida.append(derecha[j])
            # Avanzamos en la mitad derecha.
            j += 1
    # Añadimos los registros restantes de la mitad izquierda.
    while i < len(izquierda):
        # Conservamos el registro pendiente.
        salida.append(izquierda[i])
        # Continuamos con el siguiente.
        i += 1
    # Añadimos los registros restantes de la mitad derecha.
    while j < len(derecha):
        # Conservamos el registro pendiente.
        salida.append(derecha[j])
        # Continuamos con el siguiente.
        j += 1
    # Devolvemos los registros organizados por nombre.
    return salida


# Ubicamos la primera posición cuyo nombre sea mayor o igual al buscado.
def limite_inferior(registros, nombre):
    # El comienzo posible está al inicio del arreglo.
    izquierda = 0
    # El final posible está después del último elemento.
    derecha = len(registros)
    # Reducimos el intervalo de búsqueda a la mitad en cada vuelta.
    while izquierda < derecha:
        # Calculamos el índice central.
        medio = (izquierda + derecha) // 2
        # Si el nombre del medio es menor, buscamos a la derecha.
        if registros[medio][0] < nombre:
            # Excluimos los registros hasta el medio inclusive.
            izquierda = medio + 1
        else:
            # Seguimos buscando desde la mitad izquierda.
            derecha = medio
    # Devolvemos dónde comienza el nombre, si existe.
    return izquierda


# Leemos los nombres de estaciones de una carpeta de datos configurable.
def cargar_estaciones(carpeta="Datos"):
    # Almacenamos cada estación en una lista.
    estaciones = []
    # Abrimos el CSV con la codificación usada por el profesor.
    with open(carpeta + "/estaciones.csv", "r", encoding="utf-8-sig", newline="") as archivo:
        # Leemos cada fila del CSV.
        lector = csv.reader(archivo)
        # Omitimos el encabezado.
        next(lector)
        # Procesamos los nombres de estaciones.
        for fila in lector:
            # Evitamos las filas vacías.
            if len(fila) > 0:
                # Guardamos el nombre sin espacios exteriores.
                estaciones.append(fila[0].strip())
    # Devolvemos todos los nombres.
    return estaciones


# Leemos las rutas del CSV, sin depender de un número fijo de servicios.
def cargar_rutas(carpeta="Datos"):
    # Cada ruta se representa como [servicio, [[orden, estación], ...]].
    rutas = []
    # Abrimos el archivo de recorridos.
    with open(carpeta + "/rutas.csv", "r", encoding="utf-8-sig", newline="") as archivo:
        # Creamos el lector de CSV.
        lector = csv.reader(archivo)
        # Omitimos el encabezado.
        next(lector)
        # Examinamos cada fila del archivo.
        for fila in lector:
            # Ignoramos las filas incompletas.
            if len(fila) < 3:
                # Continuamos con la siguiente fila.
                continue
            # Tomamos el nombre del servicio.
            servicio = fila[0].strip()
            # Convertimos la posición a un número entero.
            orden = int(fila[1].strip())
            # Leemos el nombre de la parada.
            estacion = fila[2].strip()
            # Suponemos que la ruta todavía no está registrada.
            encontrada = None
            # Recorremos los servicios ya leídos.
            for ruta in rutas:
                # Comprobamos el identificador del servicio.
                if ruta[0] == servicio:
                    # Guardamos una referencia a su lista.
                    encontrada = ruta
                    # Terminamos la búsqueda de este servicio.
                    break
            # Si no existe, creamos un servicio nuevo.
            if encontrada is None:
                # Creamos la lista de paradas del servicio.
                encontrada = [servicio, []]
                # Registramos el nuevo servicio.
                rutas.append(encontrada)
            # Accedemos a las paradas del servicio encontrado.
            paradas = encontrada[1]
            # Buscamos la posición de inserción sin usar sort().
            posicion = 0
            # Respetamos el orden numérico del CSV incluso si viene mezclado.
            while posicion < len(paradas) and paradas[posicion][0] < orden:
                # Avanzamos hasta la posición correcta.
                posicion += 1
            # Insertamos la parada en su lugar.
            paradas.insert(posicion, [orden, estacion])
    # Devolvemos los recorridos de todos los servicios.
    return rutas


# Creamos un índice para consultar estaciones sin recorrer todas las rutas cada vez.
class IndiceViajes:
    # Construimos el índice una sola vez por cada versión de la red.
    def __init__(self, rutas, estaciones):
        # Guardamos los recorridos originales para consultarlos después.
        self.rutas = rutas
        # Convertimos estaciones en registros de un solo campo para ordenarlas.
        registros_estaciones = []
        # Recorremos los nombres de estaciones.
        for nombre in estaciones:
            # Incorporamos un registro con el nombre.
            registros_estaciones.append([nombre])
        # Ordenamos los nombres usando nuestro propio merge sort.
        self.estaciones_ordenadas = ordenar_por_nombre(registros_estaciones)
        # Creamos un índice global de estaciones donde se puede abordar.
        registros_globales = []
        # Aquí guardaremos los nombres ordenados de cada servicio.
        self.por_ruta = []
        # Construimos la información para cada servicio.
        for numero_ruta in range(len(rutas)):
            # Obtenemos las paradas del servicio actual.
            paradas = rutas[numero_ruta][1]
            # Creamos los registros de búsqueda de este servicio.
            registros_ruta = []
            # Recorremos las paradas en el sentido real del recorrido.
            for posicion in range(len(paradas)):
                # Extraemos el nombre de la estación.
                estacion = paradas[posicion][1]
                # Registramos estación y posición para la búsqueda binaria.
                registros_ruta.append([estacion, posicion])
                # Registramos estación, servicio y posición en el índice global.
                registros_globales.append([estacion, numero_ruta, posicion])
            # Guardamos el índice alfabético de las paradas de esta ruta.
            self.por_ruta.append(ordenar_por_nombre(registros_ruta))
        # Ordenamos todas las apariciones de estación en la red.
        self.ocurrencias = ordenar_por_nombre(registros_globales)

    # Comprobamos rápidamente si la estación existe en el catálogo.
    def existe(self, nombre):
        # Buscamos dónde debería comenzar el nombre.
        inicio = limite_inferior(self.estaciones_ordenadas, nombre)
        # Verificamos que la posición esté dentro de la lista.
        if inicio < len(self.estaciones_ordenadas):
            # Comprobamos si el nombre coincide exactamente.
            return self.estaciones_ordenadas[inicio][0] == nombre
        # Si se sale del catálogo, no existe.
        return False

    # Buscamos únicamente las rutas que pasan por una estación.
    def servicios_de(self, nombre):
        # Calculamos el comienzo del bloque de coincidencias.
        inicio = limite_inferior(self.ocurrencias, nombre)
        # Preparamos la lista de servicios y posiciones encontrados.
        coincidencias = []
        # Recorremos solo los registros del nombre solicitado.
        while inicio < len(self.ocurrencias) and self.ocurrencias[inicio][0] == nombre:
            # Obtenemos índice del servicio y posición de la parada.
            coincidencias.append([self.ocurrencias[inicio][1], self.ocurrencias[inicio][2]])
            # Continuamos con la siguiente aparición de esa estación.
            inicio += 1
        # Devolvemos los servicios candidatos, sin escanear toda la red.
        return coincidencias

    # Buscamos posiciones de una estación dentro de un servicio concreto.
    def posiciones_en_ruta(self, numero_ruta, nombre):
        # Recuperamos el índice alfabético de esa ruta.
        registros = self.por_ruta[numero_ruta]
        # Localizamos el comienzo del nombre mediante búsqueda binaria.
        inicio = limite_inferior(registros, nombre)
        # Preparamos las posiciones coincidentes.
        posiciones = []
        # Recuperamos las coincidencias; tolera estaciones repetidas en un servicio.
        while inicio < len(registros) and registros[inicio][0] == nombre:
            # Añadimos la posición dentro del recorrido dirigido.
            posiciones.append(registros[inicio][1])
            # Avanzamos hacia la siguiente coincidencia.
            inicio += 1
        # Devolvemos las posiciones posibles para ese servicio.
        return posiciones


# Comprobamos una estación frente a la lista de cierres sin usar set ni dict.
def esta_cerrada(cerradas, nombre):
    # Recorremos las estaciones cerradas.
    for cerrada in cerradas:
        # Verificamos si coincide el nombre.
        if cerrada == nombre:
            # Confirmamos el cierre.
            return True
    # Si no aparece en la lista, está abierta.
    return False


# Creamos un prefijo para comprobar tramos completos en tiempo constante.
def preparar_prefijos_cierres(rutas, cerradas):
    # Guardamos una lista de prefijos para cada servicio.
    prefijos = []
    # Recorremos todas las rutas.
    for ruta in rutas:
        # El primer valor es cero estaciones cerradas antes de comenzar.
        prefijo = [0]
        # Recorremos las paradas de la ruta.
        for parada in ruta[1]:
            # Reutilizamos el conteo anterior.
            cantidad = prefijo[len(prefijo) - 1]
            # Si la estación está cerrada, sumamos una unidad.
            if esta_cerrada(cerradas, parada[1]):
                # Aumentamos el acumulado de cierres.
                cantidad += 1
            # Guardamos el total de estaciones cerradas hasta esta parada.
            prefijo.append(cantidad)
        # Incorporamos el índice del servicio.
        prefijos.append(prefijo)
    # Devolvemos el conteo acumulado para cada ruta.
    return prefijos


# Consultamos si un tramo [inicio, fin] está abierto usando los prefijos.
def tramo_disponible(prefijos, numero_ruta, inicio, fin):
    # Obtenemos el acumulado de cierres de la ruta.
    prefijo = prefijos[numero_ruta]
    # Restamos los cierres anteriores al inicio del tramo.
    cierres = prefijo[fin + 1] - prefijo[inicio]
    # El tramo es válido solamente cuando no hay cierres.
    return cierres == 0


# Evaluamos un candidato y lo conservamos si mejora el actual.
def elegir_mejor(actual, candidato, criterio):
    # Si aún no tenemos viaje, aceptamos el primero.
    if actual is None:
        # Conservamos el candidato.
        return candidato
    # Para menos transbordos, un directo siempre vence a uno con cambio.
    if criterio == "transbordos":
        # Calculamos cambios del candidato: directo 0, conexión 1.
        cambios_nuevo = 0 if candidato[0] == "DIRECTO" else 1
        # Calculamos cambios del recorrido actual.
        cambios_actual = 0 if actual[0] == "DIRECTO" else 1
        # Elegimos el candidato si requiere menos cambios de bus.
        if cambios_nuevo < cambios_actual:
            # Devolvemos el candidato mejor.
            return candidato
        # Conservamos el actual si hace menos transbordos.
        if cambios_nuevo > cambios_actual:
            # Evitamos reemplazarlo por un viaje peor.
            return actual
    # Elegimos el candidato si utiliza menos tramos entre estaciones.
    if candidato[4] < actual[4]:
        # Guardamos la alternativa con menos paradas.
        return candidato
    # En empate de paradas, preferimos la opción directa.
    if candidato[4] == actual[4] and candidato[0] == "DIRECTO" and actual[0] == "TRANSBORDO":
        # Devolvemos el directo en el empate.
        return candidato
    # Si todo empata, conservamos el primero para resultados estables.
    return actual


# Planeamos viajes con máximo un transbordo, usando el índice ya construido.
def buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice=None, criterio="paradas"):
    # Si no recibimos un índice, creamos uno para mantener compatibilidad.
    if indice is None:
        # Recomendación: en Streamlit se prepara una sola vez y se reutiliza.
        indice = IndiceViajes(rutas, estaciones)
    # Verificamos que el criterio sea uno de los dos soportados.
    if criterio != "paradas" and criterio != "transbordos":
        # Devolvemos una explicación del criterio incorrecto.
        return ["ERROR", "Criterio de búsqueda desconocido.", None, None, 0]
    # Comprobamos que exista la estación inicial.
    if not indice.existe(origen):
        # Devolvemos un mensaje claro para la web.
        return ["ERROR", "La estación de origen no existe.", None, None, 0]
    # Comprobamos que exista la estación final.
    if not indice.existe(destino):
        # Devolvemos un mensaje claro para la web.
        return ["ERROR", "La estación de destino no existe.", None, None, 0]
    # Rechazamos el origen si está cerrado.
    if esta_cerrada(cerradas, origen):
        # Comunicamos la razón por la que no se puede viajar.
        return ["ERROR", "La estación de origen está cerrada.", None, None, 0]
    # Rechazamos el destino si está cerrado.
    if esta_cerrada(cerradas, destino):
        # Comunicamos la razón por la que no se puede viajar.
        return ["ERROR", "La estación de destino está cerrada.", None, None, 0]
    # Si son la misma estación, el viaje tiene cero paradas.
    if origen == destino:
        # No hace falta abordar un bus.
        return ["MISMO DESTINO", None, None, None, 0]
    # Preparamos los cierres del estado actual (si cambian, se recalculan).
    prefijos = preparar_prefijos_cierres(rutas, cerradas)
    # Obtenemos solamente los servicios que pasan por el origen.
    salidas = indice.servicios_de(origen)
    # Obtenemos solamente los servicios que llegan al destino.
    llegadas = indice.servicios_de(destino)
    # Todavía no conocemos ningún viaje válido.
    mejor = None

    # FASE 1: COMPROBAR CONEXIONES DIRECTAS.
    # Recorremos únicamente los servicios con estación de origen.
    for salida in salidas:
        # Guardamos el identificador interno de servicio.
        ruta_1 = salida[0]
        # Guardamos la posición donde se aborda ese servicio.
        posicion_origen = salida[1]
        # Localizamos las apariciones del destino dentro de ese servicio.
        posiciones_destino = indice.posiciones_en_ruta(ruta_1, destino)
        # Recorremos los destinos posibles respetando el sentido de la ruta.
        for posicion_destino in posiciones_destino:
            # Solo se puede viajar hacia adelante.
            if posicion_origen < posicion_destino:
                # Excluimos el recorrido que atraviese cualquier estación cerrada.
                if tramo_disponible(prefijos, ruta_1, posicion_origen, posicion_destino):
                    # Calculamos la cantidad de tramos.
                    tramos = posicion_destino - posicion_origen
                    # Guardamos nombre del servicio y cantidad de tramos.
                    candidato = ["DIRECTO", rutas[ruta_1][0], None, None, tramos]
                    # Comparamos esta opción con el mejor viaje encontrado.
                    mejor = elegir_mejor(mejor, candidato, criterio)
    # Si queremos menos cambios y ya hay directo, no buscamos transbordos.
    if criterio == "transbordos" and mejor is not None:
        # Ninguna opción con transbordo puede mejorar el número de cambios.
        return mejor
    # Si ya existe un directo de un solo tramo, no hay viaje más corto posible.
    if mejor is not None and mejor[4] == 1:
        # La cantidad mínima positiva de tramos es uno.
        return mejor

    # FASE 2: COMPROBAR CONEXIONES CON UN TRANSBORDO.
    # Recorremos únicamente servicios que pasan por el origen.
    for salida in salidas:
        # Obtenemos el identificador interno del primer servicio.
        ruta_1 = salida[0]
        # Localizamos la posición del origen.
        posicion_origen = salida[1]
        # Recuperamos las paradas del primer servicio.
        paradas_1 = rutas[ruta_1][1]
        # Evaluamos únicamente servicios que llegan al destino.
        for llegada in llegadas:
            # Obtenemos el identificador del segundo servicio.
            ruta_2 = llegada[0]
            # Guardamos la posición donde finaliza el viaje.
            posicion_destino = llegada[1]
            # Descartamos cambiar de servicio hacia el mismo identificador.
            if ruta_1 == ruta_2:
                # Un mismo servicio no necesita un transbordo.
                continue
            # Recorremos puntos de cambio posteriores al origen.
            for i in range(posicion_origen + 1, len(paradas_1)):
                # Un primer tramo cerrado no mejora al alargarlo: podemos parar.
                if not tramo_disponible(prefijos, ruta_1, posicion_origen, i):
                    # Ninguna parada posterior de esta ruta será alcanzable.
                    break
                # Obtenemos el nombre de la estación candidata de cambio.
                cambio = paradas_1[i][1]
                # Buscamos esa estación en el segundo servicio mediante índice.
                posiciones_cambio = indice.posiciones_en_ruta(ruta_2, cambio)
                # Evaluamos todas las apariciones del cambio en el segundo servicio.
                for j in posiciones_cambio:
                    # El segundo bus debe pasar por el cambio antes del destino.
                    if j < posicion_destino:
                        # Verificamos cierres en el segundo tramo.
                        if tramo_disponible(prefijos, ruta_2, j, posicion_destino):
                            # Sumamos tramos del primero y el segundo servicio.
                            tramos = (i - posicion_origen) + (posicion_destino - j)
                            # Guardamos el candidato con un único transbordo.
                            candidato = ["TRANSBORDO", rutas[ruta_1][0], rutas[ruta_2][0], cambio, tramos]
                            # Actualizamos el mejor según el criterio seleccionado.
                            mejor = elegir_mejor(mejor, candidato, criterio)
    # Si ninguna combinación sirvió, devolvemos None.
    return mejor


# Imprimimos un recorrido en la terminal sin afectar la página web.
def mostrar_resultado(resultado, origen, destino):
    # Comprobamos si el motor encontró un error de validación.
    if resultado is not None and resultado[0] == "ERROR":
        # Mostramos solo el mensaje de error concreto.
        print("ERROR:", resultado[1])
    # Si existe una alternativa válida, mostramos sus detalles.
    elif resultado is not None:
        # Identificamos el origen y el destino de la consulta.
        print("\nOrigen:", origen, "\nDestino:", destino)
        # Mostramos el tipo de viaje seleccionado.
        print("Tipo:", resultado[0])
        # Solo mostramos buses si hay que desplazarse.
        if resultado[0] != "MISMO DESTINO":
            # Mostramos el primer servicio.
            print("Primer servicio:", resultado[1])
        # Informamos transbordo y segundo servicio cuando corresponda.
        if resultado[0] == "TRANSBORDO":
            # Mostramos la estación de conexión.
            print("Cambio:", resultado[3])
            # Mostramos el siguiente servicio.
            print("Segundo servicio:", resultado[2])
        # Mostramos los tramos recorridos.
        print("Cantidad de paradas:", resultado[4])
    else:
        # Avisamos si no hay conexión con máximo un cambio de servicio.
        print("No se encontró un viaje con máximo un transbordo.")


# Ejecutamos este ejemplo solo al abrir este archivo directamente.
if __name__ == "__main__":
    # Cargamos las estaciones del proyecto.
    estaciones = cargar_estaciones()
    # Cargamos los servicios de la red.
    rutas = cargar_rutas()
    # Construimos índices reutilizables una sola vez.
    indice = IndiceViajes(rutas, estaciones)
    # Simulamos el cierre de una estación.
    cerradas = ["CALLE 57"]
    # Establecemos el origen del ejemplo.
    origen = "UNIVERSIDADES"
    # Establecemos el destino del ejemplo.
    destino = "PORTAL USME"
    # Buscamos el recorrido con el menor número de paradas (R5 oficial).
    corto = buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice, "paradas")
    # Mostramos la primera búsqueda.
    print("MEJOR POR MENOS PARADAS")
    # Imprimimos la recomendación oficial.
    mostrar_resultado(corto, origen, destino)
    # Buscamos el recorrido con la menor cantidad de cambios de servicio.
    simple = buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice, "transbordos")
    # Presentamos la segunda alternativa.
    print("\nMEJOR POR MENOS TRANSBORDOS")
    # Imprimimos la recomendación adicional.
    mostrar_resultado(simple, origen, destino)

# NUEVA FUNCION DE APOYO: reconstruye las estaciones del viaje elegido.
# La interfaz no calcula el itinerario: recibe las paradas del motor.
def detalle_recorrido(rutas, indice, resultado, origen, destino, cerradas):
    # Solo hay itinerario cuando la búsqueda encontró un viaje real.
    if resultado is None or resultado[0] != "DIRECTO" and resultado[0] != "TRANSBORDO":
        return []
    # Construimos las condiciones de cierre igual que en la búsqueda principal.
    prefijos = preparar_prefijos_cierres(rutas, cerradas)
    # Recorremos las apariciones del origen, sin usar dict ni set.
    for salida in indice.servicios_de(origen):
        # Identificador y posición del primer servicio.
        r1, p1 = salida[0], salida[1]
        # El servicio debe coincidir con el seleccionado por el planeador.
        if rutas[r1][0] != resultado[1]:
            continue
        # Para una ruta directa solo necesitamos encontrar el destino.
        if resultado[0] == "DIRECTO":
            # Revisamos todas las posiciones del destino en ese servicio.
            for pd in indice.posiciones_en_ruta(r1, destino):
                # Comprobamos orden, cierres y número exacto de tramos.
                if pd > p1 and pd - p1 == resultado[4] and tramo_disponible(prefijos, r1, p1, pd):
                    # Construimos la secuencia real de estaciones del primer servicio.
                    tramo = []
                    # Incluimos el origen y la parada de destino.
                    for i in range(p1, pd + 1):
                        tramo.append(rutas[r1][1][i][1])
                    # Devolvemos servicio y paradas, sin metadatos de geolocalización.
                    return [[resultado[1], tramo]]
        # Si existe transbordo, localizamos el punto compartido.
        else:
            # Leemos la estación de transbordo obtenida por R5.
            cambio = resultado[3]
            # Recorremos los lugares donde esta primera ruta pasa por el cambio.
            for pc1 in indice.posiciones_en_ruta(r1, cambio):
                # El transbordo debe ser posterior al origen y estar disponible.
                if pc1 <= p1 or not tramo_disponible(prefijos, r1, p1, pc1):
                    continue
                # Recorremos servicios que pasan por el lugar de cambio.
                for intermedio in indice.servicios_de(cambio):
                    # Identificador y posición de abordaje del segundo servicio.
                    r2, pc2 = intermedio[0], intermedio[1]
                    # Solo sirve el segundo servicio que R5 seleccionó.
                    if rutas[r2][0] != resultado[2]:
                        continue
                    # Buscamos dónde llega ese servicio al destino.
                    for pd in indice.posiciones_en_ruta(r2, destino):
                        # La parada de destino debe venir después del transbordo.
                        if pd <= pc2:
                            continue
                        # Ambos tramos deben sumar las paradas recomendadas.
                        if (pc1 - p1) + (pd - pc2) != resultado[4]:
                            continue
                        # Se descartan los recorridos que pasan por un cierre.
                        if not tramo_disponible(prefijos, r2, pc2, pd):
                            continue
                        # Guardamos todas las estaciones del primer servicio.
                        tramo_1 = []
                        for i in range(p1, pc1 + 1):
                            tramo_1.append(rutas[r1][1][i][1])
                        # Guardamos todas las estaciones del segundo servicio.
                        tramo_2 = []
                        for j in range(pc2, pd + 1):
                            tramo_2.append(rutas[r2][1][j][1])
                        # Devolvemos la información exacta que mostrará la página.
                        return [[resultado[1], tramo_1], [resultado[2], tramo_2]]
    # Si no podemos reconstruir una ruta, avisamos con una lista vacía.
    return []
