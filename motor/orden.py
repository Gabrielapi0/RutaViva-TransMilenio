def ordenar(lista):
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


def busqueda_binaria(lista_ordenada, objetivo):
    izq = 0
    der = len(lista_ordenada) - 1
    while izq <= der:
        mid = (izq + der) // 2
        if lista_ordenada[mid] == objetivo:
            return mid
        elif lista_ordenada[mid] < objetivo:
            izq = mid + 1
        else:
            der = mid - 1
    return -1


def buscar_pertenencia(lista, elemento):
    for item in lista:
        if item == elemento:
            return True
    return False