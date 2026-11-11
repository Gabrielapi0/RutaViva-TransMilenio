# motor/__init__.py
import os
from .cargador import cargar_estaciones, cargar_rutas, cargar_horarios
from .orden import ordenar, busqueda_binaria, buscar_pertenencia
from .fila import simular_fila

# 1. Imports del Integrante 2 (R4 y R6)
from .horarios import IndiceHorarios
from .ranking import IndiceRanking


class Red:
    def __init__(self, carpeta):
        # Estructuras base compartidas
        self.estaciones = cargar_estaciones(carpeta)
        self.rutas = cargar_rutas(carpeta)
        self.horarios = cargar_horarios(carpeta)
        self.cerradas = []  # Estado de cierres (Integrante 4 / R8)

        # 2. Inicialización de los índices de Integrante 2
        ruta_horarios_csv = os.path.join(carpeta, "horarios.csv")
        self._horarios = IndiceHorarios(ruta_horarios_csv)
        self._ranking = IndiceRanking(self._horarios)

    # --- REQUISITOS INTEGRANTE 1 (P1) ---

    def estado(self, nombre):
        """R1: Estado de la estación ('OPERATIVA', 'CERRADA', 'NO EXISTE') y sus rutas."""
        nombre_norm = nombre.strip().upper()
        existe = buscar_pertenencia(self.estaciones, nombre_norm)
        if not existe:
            return "NO EXISTE", []

        est_cerrada = buscar_pertenencia(self.cerradas, nombre_norm)
        estado_str = "CERRADA" if est_cerrada else "OPERATIVA"

        rutas_asociadas = []
        for r in self.rutas:
            id_ruta = r[0]
            paradas = r[1]
            for p in paradas:
                if p[1] == nombre_norm:
                    if not buscar_pertenencia(rutas_asociadas, id_ruta):
                        rutas_asociadas.append(id_ruta)
                    break

        return estado_str, rutas_asociadas

    def autocompletar(self, prefijo, k):
        """R2: Devuelve hasta k estaciones ABIERTAS que inician por prefijo en orden alfabético."""
        prefijo_norm = prefijo.strip().upper()
        estaciones_ordenadas = ordenar(self.estaciones)
        resultados = []
        len_pref = len(prefijo_norm)

        for est in estaciones_ordenadas:
            if len(resultados) >= k:
                break
            if buscar_pertenencia(self.cerradas, est):
                continue
            if est[:len_pref] == prefijo_norm:
                resultados.append(est)

        return resultados

    def rango(self, desde, hasta):
        """R3: Devuelve las estaciones ABIERTAS dentro del rango alfabético [desde, hasta]."""
        desde_norm = desde.strip().upper()
        hasta_norm = hasta.strip().upper()
        estaciones_ordenadas = ordenar(self.estaciones)
        resultados = []

        for est in estaciones_ordenadas:
            if buscar_pertenencia(self.cerradas, est):
                continue
            if desde_norm <= est <= hasta_norm:
                resultados.append(est)

        return resultados

    # --- REQUISITOS INTEGRANTE 2 (P2: R4, R6) ---

    def proximo_bus(self, estacion, ruta, hora):
        """R4: Consulta del próximo bus para una ruta y estación dada una hora HH:MM."""
        return self._horarios.proximo(estacion, ruta, hora, self.rutas, self.cerradas)

    def ranking(self, k):
        """R6: Top k estaciones abiertas por donde pasan más buses al día."""
        return self._ranking.top(k, self.estaciones, self.rutas, self.cerradas)

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

    # --- STUBS INTEGRANTE 4 (P4: R7, R8, R9) ---

    def agregar_parada(self, ruta, nueva, despues_de):
        pass

    def quitar_parada(self, ruta, estacion):
        pass

    def recorrido(self, ruta, al_reves=False):
        pass

    def cerrar(self, nombre):
        """R8: Cerrar estación temporalmente."""
        nombre_norm = nombre.strip().upper()
        if buscar_pertenencia(self.estaciones, nombre_norm) and not buscar_pertenencia(self.cerradas, nombre_norm):
            self.cerradas.append(nombre_norm)
            self._invalidar_p2(rutas_cambiaron=False)

    def reabrir(self, nombre):
        """R8: Reabrir estación."""
        nombre_norm = nombre.strip().upper()
        if buscar_pertenencia(self.cerradas, nombre_norm):
            nueva_lista = []
            for e in self.cerradas:
                if e != nombre_norm:
                    nueva_lista.append(e)
            self.cerradas = nueva_lista
            self._invalidar_p2(rutas_cambiaron=False)

    def deshacer(self):
        pass

    def rehacer(self):
        pass


__all__ = ["Red", "simular_fila"]