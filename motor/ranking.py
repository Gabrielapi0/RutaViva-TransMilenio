"""
R6 - Ranking de estaciones.  Integrante 2.

Archivo: motor/ranking.py

Que mide
--------
"Buses al dia" de una estacion = suma, sobre todas las rutas que HOY paran
en ella (segun self.rutas), del numero de buses diarios de esa ruta en esa
estacion (eventos de horarios.csv).  Ej.: RICAURTE = 4446 con los datos reales.

Estructura elegida: cache en dos niveles
----------------------------------------
    nivel 1  self._orden_total   todas las estaciones [nombre, buses], ordenadas
                                 por buses desc. y nombre asc.  Depende de rutas.
    nivel 2  self._abiertas      lo mismo pero sin las cerradas.  Depende de cerradas.

    ranking(k) con cache valida  -> copia los k primeros:        O(k)
    tras cerrar / reabrir         -> se rehace solo el nivel 2:   O(S log c)
    tras agregar / quitar parada  -> se rehacen ambos niveles:    O(P log P + S log S)

    S = estaciones, P = paradas de todas las rutas, c = estaciones cerradas.

La recomputacion es perezosa: invalidar() solo marca; el trabajo se hace en
la siguiente llamada a ranking().  Se consulta mucho y cambia poco.

Decisiones (documentadas en DOCUMENTACION_P2.md)
------------------------------------------------
- Empates: mismo numero de buses -> orden alfabetico por nombre.
- k <= 0 o no entero -> [].   k mayor que las abiertas -> todas las abiertas.
- Estaciones abiertas sin buses aparecen al final con 0.
- Parada agregada por R7 sin horarios propios: hereda los buses de la parada
  anterior de esa ruta (el bus que pasa por "despues_de" sigue a la nueva).
  Si es la primera de la ruta, hereda de la siguiente con datos.
- Si una estacion aparece dos veces en la misma ruta se cuenta una sola vez
  (los eventos de horarios ya incluyen ambas pasadas).
"""

from .horarios import ordenar_por, buscar_exacto


def _menor_por_nombre(a, b):
    return a[0] < b[0]


def _menor_ranking(a, b):
    """a va antes que b si tiene mas buses; en empate, nombre alfabetico."""
    if a[1] != b[1]:
        return a[1] > b[1]
    return a[0] < b[0]


class IndiceRanking:
    """Indice privado de Integrante 2.  Red lo guarda en self._ranking."""

    def __init__(self, horarios):
        self._h = horarios          # IndiceHorarios compartido (no se copia)
        self._orden_total = None    # nivel 1
        self._abiertas = None       # nivel 2

    # --- invalidacion ----------------------------------------------------

    def invalidar(self):
        """Tras agregar_parada, quitar_parada, deshacer o rehacer."""
        self._orden_total = None
        self._abiertas = None

    def invalidar_cierres(self):
        """Tras cerrar o reabrir (las rutas no cambiaron)."""
        self._abiertas = None

    # --- calculo ---------------------------------------------------------

    def _buses_de_ruta(self, ruta):
        """[[estacion, buses], ...] de una ruta, una vez por estacion,
        rellenando paradas sin horarios con la vecina. O(L log L + L log G)."""
        id_ruta = ruta[0]
        paradas = ruta[1]
        valores = []
        for parada in paradas:
            valores.append(self._h.cantidad(id_ruta, parada[1]))

        # Relleno hacia adelante: hereda de la parada anterior.
        anterior = 0
        i = 0
        while i < len(valores):
            if valores[i] == 0:
                valores[i] = anterior
            else:
                anterior = valores[i]
            i += 1
        # Relleno hacia atras: paradas iniciales sin datos.
        siguiente = 0
        i = len(valores) - 1
        while i >= 0:
            if valores[i] == 0:
                valores[i] = siguiente
            else:
                siguiente = valores[i]
            i -= 1

        pares = []
        i = 0
        while i < len(paradas):
            pares.append([paradas[i][1], valores[i]])
            i += 1
        # Una sola vez por estacion dentro de la ruta.
        pares = ordenar_por(pares, _menor_por_nombre)
        unicos = []
        for par in pares:
            if len(unicos) == 0 or unicos[len(unicos) - 1][0] != par[0]:
                unicos.append(par)
        return unicos

    def _calcular_orden_total(self, estaciones, rutas):
        # 1. Juntar [estacion, buses] de todas las rutas y sumar por estacion.
        todos = []
        for ruta in rutas:
            for par in self._buses_de_ruta(ruta):
                todos.append(par)
        todos = ordenar_por(todos, _menor_por_nombre)
        nombres = []
        totales = []
        for par in todos:
            if len(nombres) > 0 and nombres[len(nombres) - 1] == par[0]:
                totales[len(totales) - 1] += par[1]
            else:
                nombres.append(par[0])
                totales.append(par[1])

        # 2. Cada estacion de la red con su total (0 si ninguna ruta para ahi).
        lista = []
        for nombre in estaciones:
            p = buscar_exacto(nombres, nombre)
            lista.append([nombre, totales[p] if p >= 0 else 0])

        # 3. Orden del ranking: buses desc., nombre asc.
        self._orden_total = ordenar_por(lista, _menor_ranking)

    def _calcular_abiertas(self, cerradas):
        cerradas_ord = ordenar_por(cerradas)
        abiertas = []
        for par in self._orden_total:
            if buscar_exacto(cerradas_ord, par[0]) < 0:
                abiertas.append(par)
        self._abiertas = abiertas

    # --- consultas -------------------------------------------------------

    def top_con_conteo(self, k, estaciones, rutas, cerradas):
        """[[nombre, buses], ...] de las k estaciones abiertas con mas buses."""
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            return []
        if self._orden_total is None:
            self._calcular_orden_total(estaciones, rutas)
            self._abiertas = None
        if self._abiertas is None:
            self._calcular_abiertas(cerradas)
        resultado = []
        i = 0
        while i < k and i < len(self._abiertas):
            par = self._abiertas[i]
            resultado.append([par[0], par[1]])
            i += 1
        return resultado

    def top(self, k, estaciones, rutas, cerradas):
        """Lo que devuelve red.ranking(k): lista de nombres."""
        nombres = []
        for par in self.top_con_conteo(k, estaciones, rutas, cerradas):
            nombres.append(par[0])
        return nombres
