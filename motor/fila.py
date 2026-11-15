# motor/fila.py

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.siguiente = None


class Cola:
   
    def __init__(self):
        self.frente = None
        self.final = None
        self.tamano = 0

    def encolar(self, valor):
        nuevo = Nodo(valor)
        if self.final is None:
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.siguiente = nuevo
            self.final = nuevo
        self.tamano += 1

    def desencolar(self):
        if self.frente is None:
            return None
        valor = self.frente.valor
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self.tamano -= 1
        return valor

    def esta_vacia(self):
        return self.tamano == 0


def simular_fila(llegadas, frecuencia, capacidad):
    """
    R10: Simula la fila de abordaje en O(n) con cola lineal propia.
    Retorna lista: [pasajeros_atendidos, pasajeros_en_espera, espera_promedio].
    """
    cola = Cola()
    pasajeros_atendidos = 0
    espera_total = 0

    minuto = 0
    total_minutos = len(llegadas)
    while minuto < total_minutos:
        personas = llegadas[minuto]
        p = 0
        while p < personas:
            cola.encolar(minuto)
            p += 1

        if frecuencia > 0 and (minuto + 1) % frecuencia == 0:
            subieron = 0
            while not cola.esta_vacia() and subieron < capacidad:
                minuto_llegada = cola.desencolar()
                espera_total += (minuto - minuto_llegada)
                pasajeros_atendidos += 1
                subieron += 1
        minuto += 1

    espera_promedio = (espera_total / pasajeros_atendidos) if pasajeros_atendidos > 0 else 0.0
    return [pasajeros_atendidos, cola.tamano, espera_promedio]