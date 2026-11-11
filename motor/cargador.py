import csv
import os

def _limpiar(texto):
    if not texto:
        return ""
    return texto.strip().replace('\r', '').replace('\n', '')


def cargar_estaciones(carpeta):
    ruta_csv = os.path.join(carpeta, "estaciones.csv")
    estaciones = []
    if not os.path.exists(ruta_csv):
        return estaciones

    with open(ruta_csv, mode='r', encoding='utf-8') as f:
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
    ruta_csv = os.path.join(carpeta, "rutas.csv")
    rutas_raw = []
    if not os.path.exists(ruta_csv):
        return []

    with open(ruta_csv, mode='r', encoding='utf-8') as f:
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

    rutas_resultado = []
    for id_ruta, orden, nombre_est in rutas_raw:
        encontrada = None
        for r in rutas_resultado:
            if r[0] == id_ruta:
                encontrada = r
                break

        if encontrada is None:
            rutas_resultado.append([id_ruta, [[orden, nombre_est]]])
        else:
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
    ruta_csv = os.path.join(carpeta, "horarios.csv")
    horarios = []
    if not os.path.exists(ruta_csv):
        return horarios

    with open(ruta_csv, mode='r', encoding='utf-8') as f:
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