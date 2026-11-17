from .orden import ordenar_indices


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
    n = len(llegadas)
    resultado = []
    for _ in range(n):
        resultado.append(0)
    if n == 0 or frecuencia <= 0 or capacidad <= 0:
        return resultado

    orden = ordenar_indices(llegadas)      # merge sort propio, estable
    fila = Cola()
    for indice in orden:
        fila.encolar(indice)

    bus = 0
    abordo = 0
    while not fila.esta_vacia():
        indice = fila.desencolar()
        instante = llegadas[indice]
        if bus > 0 and instante <= bus and abordo < capacidad:
            abordo += 1
        else:
            siguiente = -(-instante // frecuencia) * frecuencia   # techo
            if siguiente < frecuencia:
                siguiente = frecuencia                            # primer bus
            if siguiente <= bus:
                siguiente = bus + frecuencia                      # bus lleno
            bus = siguiente
            abordo = 1
        resultado[indice] = bus
    return resultado