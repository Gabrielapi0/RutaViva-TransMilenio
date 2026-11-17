import csv

from .tabla_hash import TablaHash

def _limpiar(texto):
    if not texto:
        return ""
    return texto.strip().replace('\r', '').replace('\n', '')


def cargar_estaciones(carpeta):
    ruta_csv = carpeta + "/estaciones.csv"
    estaciones = []
    try:
        f = open(ruta_csv, mode='r', encoding='utf-8')
    except FileNotFoundError:
        return estaciones

    with f:
        lector = csv.reader(f)
        encabezado = True
        for fila in lector:
            if encabezado:
                encabezado = False
                continue
            if fila and len(fila) > 0:
                nombre = _limpiar(fila[0]).upper()
                if nombre:
                    estaciones.append(nombre)
    return estaciones


def cargar_rutas(carpeta):
    ruta_csv = carpeta + "/rutas.csv"
    rutas_raw = []
    try:
        f = open(ruta_csv, mode='r', encoding='utf-8')
    except FileNotFoundError:
        return []

    with f:
        lector = csv.reader(f)
        encabezado = True
        for fila in lector:
            if encabezado:
                encabezado = False
                continue
            if len(fila) >= 3:
                id_ruta = _limpiar(fila[0]).upper()
                orden = int(_limpiar(fila[1]))
                nombre_est = _limpiar(fila[2]).upper()
                rutas_raw.append((id_ruta, orden, nombre_est))

    # Agrupamos las filas por ruta. La ruta se ubica con la tabla hash propia
    # (id -> [id, paradas]) en O(1) esperado, así que agrupar cuesta O(P) en total.
    # (Antes se recorría la lista de rutas por cada fila: O(P * R), cuadrático).
    rutas_resultado = []
    indice_rutas = TablaHash()
    for id_ruta, orden, nombre_est in rutas_raw:
        encontrada = indice_rutas.obtener(id_ruta)
        if encontrada is None:
            encontrada = [id_ruta, []]
            rutas_resultado.append(encontrada)
            indice_rutas.poner(id_ruta, encontrada)
        encontrada[1].append([orden, nombre_est])

    for r in rutas_resultado:
        paradas = r[1]
        for i in range(1, len(paradas)):
            clave = paradas[i]
            j = i - 1
            while j >= 0 and paradas[j][0] > clave[0]:
                paradas[j + 1] = paradas[j]
                j -= 1
            paradas[j + 1] = clave

    return rutas_resultado


def cargar_horarios(carpeta):
    ruta_csv = carpeta + "/horarios.csv"
    horarios = []
    try:
        f = open(ruta_csv, mode='r', encoding='utf-8')
    except FileNotFoundError:
        return horarios

    with f:
        lector = csv.reader(f)
        encabezado = True
        for fila in lector:
            if encabezado:
                encabezado = False
                continue
            if len(fila) >= 3:
                ruta = _limpiar(fila[0]).upper()
                estacion = _limpiar(fila[1]).upper()
                hora = _limpiar(fila[2])
                horarios.append((ruta, estacion, hora))
    return horarios