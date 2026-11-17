def _hash_texto(texto):
    h = 5381
    for caracter in texto:
        h = (h * 33 + ord(caracter)) % 2147483647
    return h


class TablaHash:
    def __init__(self, capacidad=64):
        self._cubetas = []
        for _ in range(capacidad):
            self._cubetas.append([])
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def _crecer(self):
        viejas = self._cubetas
        self._cubetas = []
        for _ in range(len(viejas) * 2):
            self._cubetas.append([])
        for cubeta in viejas:
            for par in cubeta:
                self._cubetas[_hash_texto(par[0]) % len(self._cubetas)].append(par)

    def poner(self, clave, valor):
        cubeta = self._cubetas[_hash_texto(clave) % len(self._cubetas)]
        for par in cubeta:
            if par[0] == clave:
                par[1] = valor
                return
        cubeta.append([clave, valor])
        self._tamano += 1
        if self._tamano > len(self._cubetas):
            self._crecer()

    def obtener(self, clave):
        cubeta = self._cubetas[_hash_texto(clave) % len(self._cubetas)]
        for par in cubeta:
            if par[0] == clave:
                return par[1]
        return None