"""Motor provisional R5 (versión resumida): viajes dirigidos con cero o un transbordo.

Solo utiliza listas y el módulo csv, según las restricciones del profesor.
La integración final con Red(carpeta) dependerá del contrato del equipo.
"""

import csv  # Único módulo permitido: lo usamos para leer los archivos CSV.


def ordenar(registros):  # Merge sort propio (sin sorted ni .sort) que ordena por el campo [0].
    if len(registros) <= 1:  # Una lista de 0 o 1 elementos ya está ordenada.
        return registros[:]  # Devolvemos una copia para no alterar la original.
    medio = len(registros) // 2  # Calculamos el punto medio de la lista.
    izq = ordenar(registros[:medio])  # Ordenamos recursivamente la mitad izquierda.
    der = ordenar(registros[medio:])  # Ordenamos recursivamente la mitad derecha.
    salida, i, j = [], 0, 0  # Lista combinada y un puntero para cada mitad.
    while i < len(izq) and j < len(der):  # Mientras ambas mitades tengan elementos...
        if izq[i][0] <= der[j][0]:  # ...elegimos el menor; "<=" conserva el orden de entrada en empates.
            salida.append(izq[i])  # Añadimos el registro de la izquierda.
            i += 1  # Avanzamos en la izquierda.
        else:  # Si el de la derecha es menor...
            salida.append(der[j])  # ...añadimos el registro de la derecha.
            j += 1  # Avanzamos en la derecha.
    return salida + izq[i:] + der[j:]  # Pegamos al final lo que haya sobrado de cualquier mitad.


def bloque(registros, nombre):  # Devuelve los registros (ya ordenados) cuyo campo [0] es igual a nombre.
    izq, der = 0, len(registros)  # Intervalo de búsqueda binaria [izq, der).
    while izq < der:  # Partimos el intervalo a la mitad en cada vuelta.
        medio = (izq + der) // 2  # Índice central del intervalo.
        if registros[medio][0] < nombre:  # Si el central es menor, el nombre está a la derecha...
            izq = medio + 1  # ...descartamos la mitad izquierda.
        else:  # Si no, puede estar en el medio o a la izquierda...
            der = medio  # ...descartamos la mitad derecha.
    coincidencias = []  # Aquí juntamos todas las apariciones del nombre.
    while izq < len(registros) and registros[izq][0] == nombre:  # Recorremos solo el bloque de ese nombre.
        coincidencias.append(registros[izq])  # Guardamos la coincidencia.
        izq += 1  # Pasamos a la siguiente.
    return coincidencias  # Lista vacía si el nombre no existe.


def leer_filas(ruta):  # Lee un CSV y devuelve sus filas sin el encabezado.
    with open(ruta, "r", encoding="utf-8-sig", newline="") as archivo:  # Codificación usada por el profesor.
        filas = list(csv.reader(archivo))  # Convertimos todas las filas en una lista.
    return filas[1:]  # Quitamos la primera fila (encabezado).


def cargar_estaciones(carpeta="Datos"):  # Lee los nombres de estaciones de la carpeta indicada.
    estaciones = []  # Lista de nombres.
    for fila in leer_filas(carpeta + "/estaciones.csv"):  # Recorremos cada fila del archivo.
        if len(fila) > 0:  # Ignoramos filas vacías.
            estaciones.append(fila[0].strip())  # Guardamos el nombre sin espacios exteriores.
    return estaciones  # Devolvemos todos los nombres.


def cargar_rutas(carpeta="Datos"):  # Lee las rutas como [servicio, [[orden, estación], ...]].
    rutas = []  # Lista de servicios.
    for fila in leer_filas(carpeta + "/rutas.csv"):  # Recorremos cada fila del archivo.
        if len(fila) < 3:  # Ignoramos filas incompletas.
            continue  # Pasamos a la siguiente fila.
        servicio, orden, estacion = fila[0].strip(), int(fila[1].strip()), fila[2].strip()  # Datos de la fila.
        ruta = None  # Suponemos que el servicio aún no está registrado.
        for r in rutas:  # Buscamos el servicio entre los ya leídos.
            if r[0] == servicio:  # Si coincide el identificador...
                ruta = r  # ...guardamos la referencia...
                break  # ...y dejamos de buscar.
        if ruta is None:  # Si no existía...
            ruta = [servicio, []]  # ...creamos el servicio con su lista de paradas...
            rutas.append(ruta)  # ...y lo registramos.
        pos = 0  # Posición de inserción, calculada sin usar sort().
        while pos < len(ruta[1]) and ruta[1][pos][0] < orden:  # Avanzamos mientras el orden sea menor.
            pos += 1  # Así respetamos el orden numérico aunque el CSV venga mezclado.
        ruta[1].insert(pos, [orden, estacion])  # Insertamos la parada en su lugar.
    return rutas  # Devolvemos todos los servicios.


class IndiceViajes:  # Índice para consultar estaciones sin recorrer toda la red cada vez.
    def __init__(self, rutas, estaciones):  # Se construye una sola vez por cada versión de la red.
        self.rutas = rutas  # Guardamos los recorridos originales.
        self.estaciones_ordenadas = ordenar([[n] for n in estaciones])  # Catálogo ordenado de nombres.
        globales, self.por_ruta = [], []  # Apariciones en toda la red y por cada servicio.
        for r in range(len(rutas)):  # Recorremos cada servicio por su índice.
            locales = []  # Registros [estación, posición] de este servicio.
            for p in range(len(rutas[r][1])):  # Recorremos sus paradas en el sentido real.
                nombre = rutas[r][1][p][1]  # Nombre de la estación en esa posición.
                locales.append([nombre, p])  # Registro para buscar dentro del servicio.
                globales.append([nombre, r, p])  # Registro para buscar en toda la red.
            self.por_ruta.append(ordenar(locales))  # Índice alfabético de este servicio.
        self.ocurrencias = ordenar(globales)  # Índice alfabético de toda la red.

    def existe(self, nombre):  # ¿La estación está en el catálogo?
        return len(bloque(self.estaciones_ordenadas, nombre)) > 0  # Sí, si la búsqueda binaria la encuentra.

    def servicios_de(self, nombre):  # Servicios que pasan por una estación: [[ruta, posición], ...].
        return [[reg[1], reg[2]] for reg in bloque(self.ocurrencias, nombre)]  # Solo el bloque de ese nombre.

    def posiciones_en_ruta(self, numero_ruta, nombre):  # Posiciones de una estación dentro de un servicio.
        return [reg[1] for reg in bloque(self.por_ruta[numero_ruta], nombre)]  # Tolera estaciones repetidas.


def esta_cerrada(cerradas, nombre):  # Revisa la lista de cierres sin usar "in", dict ni set (prohibidos).
    for cerrada in cerradas:  # Recorremos las estaciones cerradas una por una.
        if cerrada == nombre:  # Si coincide con la buscada...
            return True  # ...está cerrada.
    return False  # Si no apareció, está abierta.


def preparar_prefijos_cierres(rutas, cerradas):  # Conteo acumulado de estaciones cerradas por servicio.
    prefijos = []  # Una lista de acumulados para cada servicio.
    for ruta in rutas:  # Recorremos cada servicio.
        prefijo = [0]  # Antes de la primera parada hay cero cierres.
        for parada in ruta[1]:  # Recorremos sus paradas.
            prefijo.append(prefijo[-1] + (1 if esta_cerrada(cerradas, parada[1]) else 0))  # Sumamos 1 si está cerrada.
        prefijos.append(prefijo)  # Guardamos los acumulados del servicio.
    return prefijos  # Devolvemos todos los acumulados.


def tramo_disponible(prefijos, r, inicio, fin):  # ¿El tramo [inicio, fin] del servicio r está abierto?
    return prefijos[r][fin + 1] - prefijos[r][inicio] == 0  # Sí, si no tiene cierres (tiempo constante).


def clave(viaje, criterio):  # Convierte un viaje en una lista comparable según el criterio.
    cambios = 0 if viaje[0] == "DIRECTO" else 1  # Directo = 0 cambios; transbordo = 1.
    if criterio == "transbordos":  # Primero menos cambios, después menos paradas.
        return [cambios, viaje[4]]  # Clave para el criterio de transbordos.
    return [viaje[4], cambios]  # Primero menos paradas; en empate, gana el directo.


def elegir_mejor(actual, candidato, criterio):  # Conserva el mejor de dos viajes.
    if actual is None or clave(candidato, criterio) < clave(actual, criterio):  # Si no hay o el nuevo es mejor...
        return candidato  # ...nos quedamos con el candidato.
    return actual  # En empate conservamos el primero (resultados estables).


def _buscar(rutas, estaciones, cerradas, origen, destino, indice, criterio):
    # Búsqueda interna: devuelve [resultado, tramos]; tramos = [[ruta, desde, hasta], ...] para el detalle.
    if indice is None:  # Si no recibimos índice...
        indice = IndiceViajes(rutas, estaciones)  # ...lo creamos (en Streamlit conviene crearlo una vez).
    if criterio != "paradas" and criterio != "transbordos":  # Solo hay dos criterios válidos.
        return [["ERROR", "Criterio de búsqueda desconocido.", None, None, 0], []]  # Mensaje para la web.
    for nombre, texto in [[origen, "origen"], [destino, "destino"]]:  # Validamos que ambas existan.
        if not indice.existe(nombre):  # Si la estación no está en el catálogo...
            return [["ERROR", "La estación de " + texto + " no existe.", None, None, 0], []]  # ...avisamos.
    for nombre, texto in [[origen, "origen"], [destino, "destino"]]:  # Validamos que ambas estén abiertas.
        if esta_cerrada(cerradas, nombre):  # Si la estación está cerrada...
            return [["ERROR", "La estación de " + texto + " está cerrada.", None, None, 0], []]  # ...avisamos.
    if origen == destino:  # Si son la misma estación...
        return [["MISMO DESTINO", None, None, None, 0], []]  # ...no hace falta tomar bus.
    prefijos = preparar_prefijos_cierres(rutas, cerradas)  # Cierres del estado actual de la red.
    salidas = indice.servicios_de(origen)  # Servicios que pasan por el origen.
    llegadas = indice.servicios_de(destino)  # Servicios que pasan por el destino.
    mejor, tramos = None, []  # Aún no hay viaje válido ni tramos.

    # FASE 1: viajes directos.
    for r1, p1 in salidas:  # Cada servicio (y posición) donde se puede abordar en el origen.
        for pd in indice.posiciones_en_ruta(r1, destino):  # Cada posición del destino en ese servicio.
            if p1 < pd and tramo_disponible(prefijos, r1, p1, pd):  # Hacia adelante y sin cierres.
                candidato = ["DIRECTO", rutas[r1][0], None, None, pd - p1]  # Viaje directo.
                if elegir_mejor(mejor, candidato, criterio) is candidato:  # Si mejora al actual...
                    mejor, tramos = candidato, [[r1, p1, pd]]  # ...lo guardamos con su tramo.
    if mejor is not None and (criterio == "transbordos" or mejor[4] == 1):  # Ningún transbordo puede mejorarlo.
        return [mejor, tramos]  # Terminamos antes para ahorrar trabajo.

    # FASE 2: viajes con un transbordo.
    for r1, p1 in salidas:  # Primer servicio, abordado en el origen.
        for r2, pd in llegadas:  # Segundo servicio, que llega al destino.
            if r1 == r2:  # Cambiar al mismo servicio no es un transbordo.
                continue  # Saltamos esta combinación.
            for i in range(p1 + 1, len(rutas[r1][1])):  # Posibles puntos de cambio después del origen.
                if not tramo_disponible(prefijos, r1, p1, i):  # Si ya hay un cierre en el primer tramo...
                    break  # ...ninguna parada posterior será alcanzable.
                cambio = rutas[r1][1][i][1]  # Estación candidata para el cambio.
                for j in indice.posiciones_en_ruta(r2, cambio):  # Dónde pasa el segundo servicio por ella.
                    if j < pd and tramo_disponible(prefijos, r2, j, pd):  # Antes del destino y sin cierres.
                        paradas = (i - p1) + (pd - j)  # Tramos del primer servicio más los del segundo.
                        candidato = ["TRANSBORDO", rutas[r1][0], rutas[r2][0], cambio, paradas]  # Viaje con transbordo.
                        if elegir_mejor(mejor, candidato, criterio) is candidato:  # Si mejora al actual...
                            mejor, tramos = candidato, [[r1, p1, i], [r2, j, pd]]  # ...lo guardamos con sus tramos.
    return [mejor, tramos]  # mejor es None si no hay viaje con máximo un transbordo.


def buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice=None, criterio="paradas"):
    # Planea viajes con máximo un transbordo; devuelve [tipo, servicio1, servicio2, cambio, paradas] o None.
    return _buscar(rutas, estaciones, cerradas, origen, destino, indice, criterio)[0]  # Solo el resultado.


def detalle_recorrido(rutas, indice, resultado, origen, destino, cerradas):
    # Devuelve [[servicio, [estaciones...]], ...] del viaje que entregó buscar_mejor_viaje.
    if resultado is None or (resultado[0] != "DIRECTO" and resultado[0] != "TRANSBORDO"):  # Sin viaje real...
        return []  # ...no hay itinerario que mostrar.
    for criterio in ["paradas", "transbordos"]:  # El resultado vino de uno de los dos criterios.
        encontrado, tramos = _buscar(rutas, None, cerradas, origen, destino, indice, criterio)  # Repetimos la búsqueda.
        if encontrado == resultado:  # Si coincide con el viaje recibido, sus tramos son los correctos.
            detalle = []  # Lista de tramos para la página.
            for r, desde, hasta in tramos:  # Cada tramo: servicio y posiciones de subida y bajada.
                detalle.append([rutas[r][0], [rutas[r][1][k][1] for k in range(desde, hasta + 1)]])  # Servicio y estaciones.
            return detalle  # La interfaz solo muestra esto; no recalcula nada.
    return []  # Si no coincide (p. ej. la red cambió), avisamos con una lista vacía.


def mostrar_resultado(resultado, origen, destino):  # Imprime un resultado en la terminal.
    if resultado is None:  # Si no se encontró viaje...
        print("No se encontró un viaje con máximo un transbordo.")  # ...lo avisamos.
    elif resultado[0] == "ERROR":  # Si hubo un error de validación...
        print("ERROR:", resultado[1])  # ...mostramos solo el mensaje.
    else:  # Si hay un resultado válido...
        print("\nOrigen:", origen, "\nDestino:", destino)  # ...mostramos la consulta...
        print("Tipo:", resultado[0])  # ...y el tipo de viaje.
        if resultado[0] != "MISMO DESTINO":  # Solo si hay que tomar bus...
            print("Primer servicio:", resultado[1])  # ...mostramos el primer servicio.
        if resultado[0] == "TRANSBORDO":  # Si hay transbordo...
            print("Cambio:", resultado[3])  # ...mostramos la estación de cambio...
            print("Segundo servicio:", resultado[2])  # ...y el segundo servicio.
        print("Cantidad de paradas:", resultado[4])  # Tramos recorridos en total.


if __name__ == "__main__":  # Este ejemplo solo corre al ejecutar el archivo directamente.
    estaciones, rutas = cargar_estaciones(), cargar_rutas()  # Cargamos la red desde la carpeta Datos.
    indice = IndiceViajes(rutas, estaciones)  # Construimos el índice una sola vez.
    cerradas, origen, destino = ["CALLE 57"], "UNIVERSIDADES", "PORTAL USME"  # Datos del ejemplo.
    for titulo, criterio in [["MEJOR POR MENOS PARADAS", "paradas"], ["\nMEJOR POR MENOS TRANSBORDOS", "transbordos"]]:
        print(titulo)  # Título de cada búsqueda.
        resultado = buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice, criterio)  # Buscamos.
        mostrar_resultado(resultado, origen, destino)  # Mostramos el resultado.