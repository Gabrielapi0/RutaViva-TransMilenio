# motor/__init__.py
from .cargador import cargar_estaciones, cargar_rutas, cargar_horarios
from .orden import ordenar, lower_bound, busqueda_binaria, buscar_pertenencia, TablaHash
from .fila import simular_fila
from .horarios import IndiceHorarios
from .ranking import IndiceRanking
from .operar import OperarRed


class Red(OperarRed):
    def __init__(self, carpeta):
        super().__init__()
        self.estaciones = cargar_estaciones(carpeta)
        self.rutas = cargar_rutas(carpeta)
        self.horarios = cargar_horarios(carpeta)
        self.cerradas = []

        # Estructuras rapidas de Integrante 1 (R1, R2, R3)
        self._estaciones_ordenadas = ordenar(self.estaciones)
        self._indice_estaciones = TablaHash(len(self.estaciones) * 2 + 1)
        self._rutas_p1_sucias = False
        self._construir_indice_estaciones()

        # Estructuras de Integrante 2 (R4, R6)
        base = carpeta.rstrip("/\\")
        self._horarios = IndiceHorarios(base + "/horarios.csv")
        self._ranking = IndiceRanking(self._horarios)

    def _construir_indice_estaciones(self):
        """Precalcula en tabla hash las rutas asociadas a cada estacion."""
        tabla = TablaHash(len(self.estaciones) * 2 + 1)
        for est in self.estaciones:
            tabla.guardar(est, [])

        for r in self.rutas:
            id_ruta = r[0]
            paradas = r[1]
            for p in paradas:
                est = p[1]
                rutas_est = tabla.obtener(est)
                if rutas_est is not None:
                    if not buscar_pertenencia(rutas_est, id_ruta):
                        rutas_est.append(id_ruta)

        self._indice_estaciones = tabla
        self._rutas_p1_sucias = False

    # --- REQUISITOS INTEGRANTE 1 (P1: R1, R2, R3) ---

    def estado(self, nombre):
        """R1: Consulta en O(1) promedio mediante tabla hash propia."""
        if self._rutas_p1_sucias:
            self._construir_indice_estaciones()

        nombre_norm = nombre.strip().upper()
        rutas_asociadas = self._indice_estaciones.obtener(nombre_norm)
        if rutas_asociadas is None:
            return "NO EXISTE", []

        est_cerrada = buscar_pertenencia(self.cerradas, nombre_norm)
        estado_str = "CERRADA" if est_cerrada else "OPERATIVA"
        return estado_str, rutas_asociadas[:]

    def autocompletar(self, prefijo, k):
        """R2: Consulta en O(log n + k) mediante busqueda binaria en arreglo preordenado."""
        if k <= 0:
            return []
        prefijo_norm = prefijo.strip().upper()
        len_pref = len(prefijo_norm)
        resultados = []

        idx = lower_bound(self._estaciones_ordenadas, prefijo_norm)
        total = len(self._estaciones_ordenadas)

        while idx < total and len(resultados) < k:
            est = self._estaciones_ordenadas[idx]
            if est[:len_pref] != prefijo_norm:
                break
            if not buscar_pertenencia(self.cerradas, est):
                resultados.append(est)
            idx += 1

        return resultados

    def rango(self, desde, hasta):
        """R3: Consulta en O(log n + m) mediante busqueda binaria en arreglo preordenado."""
        desde_norm = desde.strip().upper()
        hasta_norm = hasta.strip().upper()
        if desde_norm > hasta_norm:
            return []

        resultados = []
        idx = lower_bound(self._estaciones_ordenadas, desde_norm)
        total = len(self._estaciones_ordenadas)

        while idx < total:
            est = self._estaciones_ordenadas[idx]
            if est > hasta_norm:
                break
            if not buscar_pertenencia(self.cerradas, est):
                resultados.append(est)
            idx += 1

        return resultados

    # --- REQUISITOS INTEGRANTE 2 (P2: R4, R6) ---

    def proximo_bus(self, estacion, ruta, hora):
        return self._horarios.proximo(estacion, ruta, hora, self.rutas, self.cerradas)

    def ranking(self, k):
        return self._ranking.top(k, self.estaciones, self.rutas, self.cerradas)

    def _invalidar_p2(self, rutas_cambiaron=True):
        """Llamado por OperarRed (R7-R9) tras cambios en rutas o cierres."""
        if rutas_cambiaron:
            self._rutas_p1_sucias = True
            self._horarios.invalidar()
            self._ranking.invalidar()
        else:
            self._ranking.invalidar_cierres()

    

    def viaje(self, origen, destino):
        try:
            from .integracion_r5 import ejecutar_r5
            return ejecutar_r5(self.rutas, self.estaciones, self.cerradas, origen, destino)
        except ImportError:
            return None


__all__ = ["Red", "simular_fila"]