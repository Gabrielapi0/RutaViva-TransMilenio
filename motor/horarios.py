"""
R4 - Proximo bus.  Integrante 2.

Archivo: motor/horarios.py

Estructura elegida
------------------
Al cargar horarios.csv (~140.000 filas) se agrupan los eventos por la pareja
(ruta, estacion). El resultado son dos listas paralelas:

    self.claves = ["1-1\x1fUNIVERSIDADES", "1-1\x1fRECINTO FERIAL", ...]  (ordenada)
    self.horas  = [[597, 608, 620, ...],    [...],                  ...]  (cada una ordenada)

    - claves[i] es "ruta" + SEP + "estacion".
    - horas[i] son los minutos desde las 00:00 en que pasa un bus de esa ruta
      por esa estacion, de menor a mayor.

Consulta: busqueda binaria sobre claves (O(log G)) y luego busqueda binaria
sobre horas[i] (O(log H)).  G = parejas ruta-estacion, H = buses de esa pareja.

Carga: un merge sort propio sobre E eventos -> O(E log E), se hace una sola vez.

Decisiones de casos borde (documentadas en DOCUMENTACION_P2.md)
---------------------------------------------------------------
1. Si la hora consultada coincide con un bus, ESE bus cuenta (el bus esta en
   la estacion en ese minuto): proximo_bus(..., "09:57") -> "09:57".
2. Si la hora es posterior al ultimo bus del dia, se envuelve al dia siguiente
   y se devuelve el primer bus del dia (el servicio se repite a diario).
   Se controla con ENVOLVER_AL_DIA_SIGUIENTE.
3. Ruta inexistente, estacion inexistente, estacion que no pertenece a la ruta,
   ruta sin horarios, hora mal escrita o estacion cerrada -> None.
   El metodo consultar() devuelve ademas el motivo, para que el front lo muestre.
4. Horas del GTFS >= 24:00 (por ejemplo 25:10) se normalizan con modulo 24
   (25:10 -> 01:10): pertenecen a la madrugada del dia siguiente.

Restricciones del motor respetadas: no se usa dict, set, sorted, .sort, min,
max, bisect, "x in lista", .index ni .count.  Solo list, str, csv.
"""

import csv

SEP = "\x1f"                       # separador invisible, menor que cualquier letra
MINUTOS_DIA = 1440
ENVOLVER_AL_DIA_SIGUIENTE = True   # decision R4: despues del ultimo bus -> primero del dia

# Codigos de motivo que devuelve consultar()
OK = "OK"
HORA_INVALIDA = "HORA_INVALIDA"
ESTACION_CERRADA = "ESTACION_CERRADA"
RUTA_INEXISTENTE = "RUTA_INEXISTENTE"
ESTACION_NO_EN_RUTA = "ESTACION_NO_EN_RUTA"
SIN_HORARIOS = "SIN_HORARIOS"


# ----------------------------------------------------------------------
# Utilidades de hora
# ----------------------------------------------------------------------

def hora_a_minutos(texto):
    """'HH:MM' -> minutos desde 00:00 (0..1439).  Devuelve -1 si es invalida.
    Horas >= 24 se normalizan con modulo 24 (decision GTFS)."""
    if not isinstance(texto, str):
        return -1
    partes = texto.strip().split(":")
    if len(partes) != 2:
        return -1
    h_txt = partes[0].strip()
    m_txt = partes[1].strip()
    if not h_txt.isdigit() or not m_txt.isdigit():
        return -1
    h = int(h_txt)
    m = int(m_txt)
    if m > 59:
        return -1
    return (h % 24) * 60 + m


def minutos_a_hora(minutos):
    """Minutos desde 00:00 -> 'HH:MM'."""
    h = minutos // 60
    m = minutos % 60
    return str(h).zfill(2) + ":" + str(m).zfill(2)


# ----------------------------------------------------------------------
# Ordenamiento y busqueda propios (reemplazan sorted / bisect)
# ----------------------------------------------------------------------

def ordenar_por(lista, menor=None):
    """Merge sort de abajo hacia arriba (iterativo, estable).
    menor(a, b) -> True si a va antes que b.  Si es None se usa a < b.
    Devuelve una lista nueva.  O(n log n) tiempo, O(n) memoria extra."""
    n = len(lista)
    origen = []
    for x in lista:
        origen.append(x)
    if n < 2:
        return origen
    destino = [None] * n
    ancho = 1
    while ancho < n:
        inicio = 0
        while inicio < n:
            medio = inicio + ancho
            if medio > n:
                medio = n
            fin = inicio + 2 * ancho
            if fin > n:
                fin = n
            i = inicio
            j = medio
            k = inicio
            while i < medio and j < fin:
                if menor is None:
                    va_derecha = origen[j] < origen[i]
                else:
                    va_derecha = menor(origen[j], origen[i])
                if va_derecha:          # estrictamente menor -> estable
                    destino[k] = origen[j]
                    j += 1
                else:
                    destino[k] = origen[i]
                    i += 1
                k += 1
            while i < medio:
                destino[k] = origen[i]
                i += 1
                k += 1
            while j < fin:
                destino[k] = origen[j]
                j += 1
                k += 1
            inicio += 2 * ancho
        origen, destino = destino, origen
        ancho *= 2
    return origen


def primera_posicion_mayor_o_igual(lista, x):
    """Busqueda binaria (lower bound) en una lista ordenada.
    Devuelve la primera posicion p con lista[p] >= x, o len(lista). O(log n)."""
    bajo = 0
    alto = len(lista)
    while bajo < alto:
        medio = (bajo + alto) // 2
        if lista[medio] < x:
            bajo = medio + 1
        else:
            alto = medio
    return bajo


def buscar_exacto(lista, x):
    """Posicion de x en la lista ordenada, o -1 si no esta. O(log n)."""
    p = primera_posicion_mayor_o_igual(lista, x)
    if p < len(lista) and lista[p] == x:
        return p
    return -1


def esta_en_lista(lista, x):
    """Recorrido lineal explicito (reemplaza 'x in lista'). O(n).
    Se usa solo para la lista de estaciones cerradas, que es pequena."""
    for elemento in lista:
        if elemento == x:
            return True
    return False


def clave_par(ruta, estacion):
    return str(ruta) + SEP + str(estacion)


# ----------------------------------------------------------------------
# Indice de horarios
# ----------------------------------------------------------------------

class IndiceHorarios:
    """Indice privado de Integrante 2.  La clase Red lo guarda en
    self._horarios y lo consulta desde proximo_bus() y ranking()."""

    def __init__(self, ruta_csv=None, filas=None):
        """ruta_csv: camino a horarios.csv.  filas: alternativa para pruebas,
        lista de [ruta, estacion, 'HH:MM']."""
        self.claves = []          # "ruta SEP estacion", ordenada
        self.horas = []           # listas de minutos, cada una ordenada
        self.total_eventos = 0

        # Estado sincronizado con self.rutas de Red (para R7).
        self._pares_activos = []  # claves "ruta SEP estacion" presentes hoy en rutas, ordenada
        self._ids_ruta = []       # identificadores de ruta presentes hoy en rutas, ordenada
        self._sucio = True        # True -> hay que re-sincronizar con rutas

        if filas is None:
            filas = self._leer_csv(ruta_csv)
        self._construir(filas)

    # --- carga -----------------------------------------------------------

    @staticmethod
    def _leer_csv(ruta_csv):
        filas = []
        if ruta_csv is None:
            return filas
        try:
            archivo = open(ruta_csv, newline="", encoding="utf-8")
        except OSError:
            return filas            # sin archivo -> red sin horarios (no se cae)
        with archivo:
            lector = csv.reader(archivo)
            primera = True
            for fila in lector:
                if primera:         # encabezado: ruta,estacion,hora
                    primera = False
                    continue
                if len(fila) < 3:
                    continue
                filas.append([fila[0].strip(), fila[1].strip(), fila[2].strip()])
        return filas

    def _construir(self, filas):
        """Ordena los eventos y los agrupa por (ruta, estacion). O(E log E)."""
        # Cada evento se codifica como un solo texto ordenable:
        #   ruta SEP estacion SEP HH:MM
        # Las horas ya normalizadas tienen 5 caracteres con ceros a la izquierda,
        # por lo que el orden de texto coincide con el orden cronologico.
        eventos = []
        for fila in filas:
            m = hora_a_minutos(fila[2])
            if m < 0:
                continue            # hora corrupta en el CSV: se descarta
            eventos.append(clave_par(fila[0], fila[1]) + SEP + minutos_a_hora(m))
        eventos = ordenar_por(eventos)
        self.total_eventos = len(eventos)

        clave_actual = None
        for texto in eventos:
            clave = texto[:-6]                  # quita SEP + "HH:MM"
            minutos = hora_a_minutos(texto[-5:])
            if clave != clave_actual:
                self.claves.append(clave)
                self.horas.append([])
                clave_actual = clave
            # Se conservan horas repetidas: en el GTFS son buses distintos que
            # pasan en el mismo minuto, y R6 debe contarlos a todos.
            self.horas[len(self.horas) - 1].append(minutos)

    # --- sincronizacion con R7 -------------------------------------------

    def invalidar(self):
        """Red debe llamarlo despues de agregar_parada, quitar_parada,
        deshacer y rehacer (y puede hacerlo en cerrar/reabrir sin costo)."""
        self._sucio = True

    def _sincronizar(self, rutas):
        """Reconstruye las parejas (ruta, estacion) vigentes a partir de la
        estructura compartida rutas = [[id, [[orden, estacion], ...]], ...].
        O(P log P), P = total de paradas.  Solo corre si hubo cambios."""
        pares = []
        ids = []
        for ruta in rutas:
            ids.append(str(ruta[0]))
            for parada in ruta[1]:
                pares.append(clave_par(ruta[0], parada[1]))
        self._pares_activos = ordenar_por(pares)
        self._ids_ruta = ordenar_por(ids)
        self._sucio = False

    # --- consultas -------------------------------------------------------

    def cantidad(self, ruta, estacion):
        """Numero de buses al dia de esa ruta en esa estacion (0 si no hay). O(log G)."""
        p = buscar_exacto(self.claves, clave_par(ruta, estacion))
        if p < 0:
            return 0
        return len(self.horas[p])

    def consultar(self, estacion, ruta, hora, rutas=None, cerradas=None):
        """Version detallada para el front.
        Devuelve [motivo, 'HH:MM' o None, es_dia_siguiente]."""
        t = hora_a_minutos(hora)
        if t < 0:
            return [HORA_INVALIDA, None, False]

        if cerradas is not None and esta_en_lista(cerradas, estacion):
            return [ESTACION_CERRADA, None, False]

        clave = clave_par(ruta, estacion)

        # Si Red entrega las rutas actuales, se valida contra ellas (R7).
        if rutas is not None:
            if self._sucio:
                self._sincronizar(rutas)
            if buscar_exacto(self._pares_activos, clave) < 0:
                if buscar_exacto(self._ids_ruta, str(ruta)) < 0:
                    return [RUTA_INEXISTENTE, None, False]
                return [ESTACION_NO_EN_RUTA, None, False]

        p = buscar_exacto(self.claves, clave)
        if p < 0 or len(self.horas[p]) == 0:
            return [SIN_HORARIOS, None, False]

        lista = self.horas[p]
        q = primera_posicion_mayor_o_igual(lista, t)
        if q < len(lista):
            return [OK, minutos_a_hora(lista[q]), False]
        if ENVOLVER_AL_DIA_SIGUIENTE:
            return [OK, minutos_a_hora(lista[0]), True]
        return [SIN_HORARIOS, None, False]

    def proximo(self, estacion, ruta, hora, rutas=None, cerradas=None):
        """Lo que devuelve red.proximo_bus: 'HH:MM' o None."""
        return self.consultar(estacion, ruta, hora, rutas, cerradas)[1]
