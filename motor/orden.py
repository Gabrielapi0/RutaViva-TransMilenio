# motor/orden.py

def ordenar(lista):
    """Ordena una lista alfabeticamente usando MergeSort O(n log n)."""
    if len(lista) <= 1:
        return lista

    medio = len(lista) // 2
    izquierda = ordenar(lista[:medio])
    derecha = ordenar(lista[medio:])
    return _mezclar(izquierda, derecha)


def _mezclar(izq, der):
    resultado = []
    i = 0
    j = 0
    while i < len(izq) and j < len(der):
        if izq[i] <= der[j]:
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1

    while i < len(izq):
        resultado.append(izq[i])
        i += 1

    while j < len(der):
        resultado.append(der[j])
        j += 1

    return resultado


def lower_bound(lista_ordenada, objetivo):
    """Busqueda binaria: retorna el primer indice i donde lista_ordenada[i] >= objetivo."""
    izq = 0
    der = len(lista_ordenada)
    while izq < der:
        mid = (izq + der) // 2
        if lista_ordenada[mid] < objetivo:
            izq = mid + 1
        else:
            der = mid
    return izq


def busqueda_binaria(lista_ordenada, objetivo):
    """Retorna la posicion exacta de objetivo en lista_ordenada, o -1 si no existe."""
    pos = lower_bound(lista_ordenada, objetivo)
    if pos < len(lista_ordenada) and lista_ordenada[pos] == objetivo:
        return pos
    return -1


def buscar_pertenencia(lista, elemento):
    """Recorrido lineal explicito sin usar el operador 'in'."""
    for item in lista:
        if item == elemento:
            return True
    return False


class TablaHash:
    """Tabla hash propia con encadenamiento y redimensionamiento dinamico (O(1) promedio)."""

    def __init__(self, capacidad_inicial=257):
        self.capacidad = capacidad_inicial
        self.tamano = 0
        self.cubetas = []
        i = 0
        while i < self.capacidad:
            self.cubetas.append([])
            i += 1

    def _hash(self, clave):
        h = 0
        for ch in clave:
            h = (h * 31 + ord(ch)) % self.capacidad
        return h

    def _redimensionar(self):
        cubetas_viejas = self.cubetas
        self.capacidad = self.capacidad * 2 + 1
        self.cubetas = []
        i = 0
        while i < self.capacidad:
            self.cubetas.append([])
            i += 1
        self.tamano = 0
        for cubeta in cubetas_viejas:
            for par in cubeta:
                self.guardar(par[0], par[1])

    def guardar(self, clave, valor):
        if (self.tamano + 1) * 4 > self.capacidad * 3:
            self._redimensionar()
        idx = self._hash(clave)
        cubeta = self.cubetas[idx]
        for par in cubeta:
            if par[0] == clave:
                par[1] = valor
                return
        cubeta.append([clave, valor])
        self.tamano += 1

    def obtener(self, clave):
        """Retorna el valor asociado a clave, o None si no existe."""
        idx = self._hash(clave)
        cubeta = self.cubetas[idx]
        for par in cubeta:
            if par[0] == clave:
                return par[1]
        return None

def limite_inferior(lista_ordenada, objetivo):
    izq = 0
    der = len(lista_ordenada)
    while izq < der:
        mid = (izq + der) // 2
        if lista_ordenada[mid] < objetivo:
            izq = mid + 1
        else:
            der = mid
    return izq


def ordenar_indices(valores):
    n = len(valores)
    a = []
    b = []
    for i in range(n):
        a.append(i)
        b.append(0)
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
            x = inicio
            y = medio
            k = inicio
            while x < medio and y < fin:
                if valores[a[x]] <= valores[a[y]]:
                    b[k] = a[x]
                    x += 1
                else:
                    b[k] = a[y]
                    y += 1
                k += 1
            while x < medio:
                b[k] = a[x]
                x += 1
                k += 1
            while y < fin:
                b[k] = a[y]
                y += 1
                k += 1
            inicio += 2 * ancho
        a, b = b, a
        ancho *= 2
    return a