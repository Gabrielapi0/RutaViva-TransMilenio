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
    cola = Cola()
    pasajeros_atendidos = 0
    espera_total = 0

    for minuto in range(len(llegadas)):
        personas = llegadas[minuto]
        for _ in range(personas):
            cola.encolar(minuto)

        if (minuto + 1) % frecuencia == 0:
            subieron = 0
            while not cola.esta_vacia() and subieron < capacidad:
                minuto_llegada = cola.desencolar()
                espera_total += (minuto - minuto_llegada)
                pasajeros_atendidos += 1
                subieron += 1

    espera_promedio = (espera_total / pasajeros_atendidos) if pasajeros_atendidos > 0 else 0

    return {
        "atendidos": pasajeros_atendidos,
        "en_espera": cola.tamano,
        "espera_promedio": espera_promedio
    }