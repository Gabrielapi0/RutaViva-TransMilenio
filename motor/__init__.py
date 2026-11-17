# motor/__init__.py
from .cargador import cargar_estaciones, cargar_rutas, cargar_horarios
from .orden import ordenar, busqueda_binaria, buscar_pertenencia, limite_inferior
from .tabla_hash import TablaHash
from .fila import simular_fila
from .operar import OperarRed  # R7, R8, R9 (Integrante 4)

# 1. Imports del Integrante 2 (R4 y R6)
from .horarios import IndiceHorarios
from .ranking import IndiceRanking


class Red(OperarRed):
    def __init__(self, carpeta):
        # Estructuras base compartidas
        self.estaciones = cargar_estaciones(carpeta)
        self.rutas = cargar_rutas(carpeta)
        self.horarios = cargar_horarios(carpeta)
        self.cerradas = []  # Estado de cierres (Integrante 4 / R8)

        # 2. Inicialización de los índices de Integrante 2
        ruta_horarios_csv = carpeta + "/horarios.csv"
        self._horarios = IndiceHorarios(ruta_horarios_csv)
        self._ranking = IndiceRanking(self._horarios)

        # Índices de Integrante 1 (R1–R3)
        self._orden_est = ordenar(self.estaciones)   # alfabético, UNA vez (R2, R3)
        self._n_orden = len(self.estaciones)
        self._tabla_est = None                       # tabla hash nombre -> rutas (R1)
        self._version_est = -1

    # --- REQUISITOS INTEGRANTE 1 (P1) ---

    def _indice_estaciones(self):
        """Tabla hash propia: nombre de estación -> lista de ids de rutas que
        pasan por ella. Se arma en O(S + P) y se rearma, de forma perezosa,
        solo si R7/R9 cambiaron las rutas (_version) o cambió la lista de
        estaciones. Comparar dos enteros es O(1)."""
        version = getattr(self, "_version", 0)
        if (self._tabla_est is None or version != self._version_est
                or len(self.estaciones) != self._n_orden):
            tabla = TablaHash(2 * len(self.estaciones) + 16)
            for nombre in self.estaciones:
                if tabla.obtener(nombre) is None:
                    tabla.poner(nombre, [])
            for r in self.rutas:
                id_ruta = r[0]
                for p in r[1]:
                    ids = tabla.obtener(p[1])
                    if ids is not None and (len(ids) == 0 or ids[len(ids) - 1] != id_ruta):
                        ids.append(id_ruta)       # una sola vez por ruta
            self._tabla_est = tabla
            self._version_est = version
        return self._tabla_est

    def _orden_alfabetico(self):
        """Estaciones ordenadas; se reordena solo si cambió la lista."""
        if len(self.estaciones) != self._n_orden:
            self._orden_est = ordenar(self.estaciones)
            self._n_orden = len(self.estaciones)
        return self._orden_est

    def estado(self, nombre):
        """R1: Estado de la estación ('OPERATIVA', 'CERRADA', 'NO EXISTE') y sus rutas.
        O(1) esperado (tabla hash) + O(c) por revisar las cerradas."""
        nombre_norm = nombre.strip().upper()
        rutas_est = self._indice_estaciones().obtener(nombre_norm)
        if rutas_est is None:
            return "NO EXISTE", []
        est_cerrada = buscar_pertenencia(self.cerradas, nombre_norm)
        estado_str = "CERRADA" if est_cerrada else "OPERATIVA"
        return estado_str, list(rutas_est)

    def autocompletar(self, prefijo, k):
        """R2: Devuelve hasta k estaciones ABIERTAS que inician por prefijo en orden alfabético.
        Búsqueda binaria del primer candidato y avance mientras coincida el prefijo."""
        prefijo_norm = prefijo.strip().upper()
        orden = self._orden_alfabetico()
        len_pref = len(prefijo_norm)
        resultados = []
        i = limite_inferior(orden, prefijo_norm)          # O(log S)
        while i < len(orden) and len(resultados) < k:
            est = orden[i]
            if est[:len_pref] != prefijo_norm:
                break                                     # ya no hay más con ese prefijo
            if not buscar_pertenencia(self.cerradas, est):
                resultados.append(est)
            i += 1
        return resultados

    def rango(self, desde, hasta):
        """R3: Devuelve las estaciones ABIERTAS dentro del rango alfabético [desde, hasta].
        Búsqueda binaria de `desde` y avance hasta pasar `hasta`: O(log S + m)."""
        desde_norm = desde.strip().upper()
        hasta_norm = hasta.strip().upper()
        orden = self._orden_alfabetico()
        resultados = []
        i = limite_inferior(orden, desde_norm)            # O(log S)
        while i < len(orden) and orden[i] <= hasta_norm:
            if not buscar_pertenencia(self.cerradas, orden[i]):
                resultados.append(orden[i])
            i += 1
        return resultados

    # --- REQUISITOS INTEGRANTE 2 (P2: R4, R6) ---

    def proximo_bus(self, estacion, ruta, hora):
        """R4: hora HH:MM del siguiente bus de esa ruta en esa estación, o None."""
        self._sincronizar_p2()
        return self._horarios.proximo(estacion, ruta, hora, self.rutas, self.cerradas)

    def ranking(self, k):
        """R6: lista de (nombre, buses_por_dia) de las k estaciones abiertas con más buses."""
        self._sincronizar_p2()
        return self._ranking.top(k, self.estaciones, self.rutas, self.cerradas)

    def _sincronizar_p2(self):
        """Si R7/R8/R9 cambiaron la red (OperarRed sube self._version en cada
        cambio, incluidos deshacer y rehacer), se invalidan los cachés de P2.
        Comparar dos enteros es O(1); el recálculo solo ocurre tras un cambio."""
        version = getattr(self, "_version", 0)
        if version != getattr(self, "_version_p2", 0):
            self._invalidar_p2()
            self._version_p2 = version

    def _invalidar_p2(self, rutas_cambiaron=True):
        """Invalida los cachés de P2 cuando ocurre alguna modificación o cierre en la red."""
        if rutas_cambiaron:
            self._horarios.invalidar()
            self._ranking.invalidar()
        else:
            self._ranking.invalidar_cierres()

    # --- REQUISITO INTEGRANTE 3 (P3: R5) ---

    def viaje(self, origen, destino):
        try:
            from .integracion_r5 import ejecutar_r5
            return ejecutar_r5(self.rutas, self.estaciones, self.cerradas, origen, destino)
        except ImportError:
            return None

    # --- R7, R8, R9 (Integrante 4): agregar_parada, quitar_parada, recorrido,
    #     cerrar, reabrir, deshacer y rehacer se heredan de OperarRed (motor/operar.py).


__all__ = ["Red", "simular_fila"]