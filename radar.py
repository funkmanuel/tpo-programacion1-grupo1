"""Busquedas, sonar y recorridos del cubo (entrega 3)."""


import time

from tablero import leer_celda, escribir_celda, NAVE, IMPACTO, HUNDIDO, DETECTADO, AGUA, AGUA_MARCADA


def buscar_nave_lineal(cubo, estado_buscado=NAVE):
    """recorre todo el cubo"""
    n = len(cubo)
    inicio = time.perf_counter()
    encontrados = []
    comparaciones = 0
    for z in range(1, n + 1):
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                comparaciones = comparaciones + 1
                if leer_celda(cubo, (z, x, y)) == estado_buscado:
                    encontrados.append((z, x, y))
    fin = time.perf_counter()
    metricas = {
        "comparaciones": comparaciones,
        "tiempo_ms": (fin - inicio) * 1000,
        "profundidad_max": 0,
    }
    return encontrados, metricas


def buscar_nave_optimizada(cubo, flota, estado_buscado=NAVE):
    """recorre celdas de la flota"""
    if estado_buscado not in (NAVE, IMPACTO, HUNDIDO, DETECTADO):
        return buscar_nave_lineal(cubo, estado_buscado)

    inicio = time.perf_counter()
    encontrados = []
    comparaciones = 0

    for datos_nave in flota.values():
        for punto in datos_nave["celdas"]:
            comparaciones = comparaciones + 1
            if leer_celda(cubo, punto) == estado_buscado:
                encontrados.append(punto)

    # Mantiene el mismo orden de puntos (z, x, y) que la busqueda lineal.
    encontrados.sort()
    fin = time.perf_counter()
    metricas = {
        "comparaciones": comparaciones,
        "tiempo_ms": (fin - inicio) * 1000,
        "profundidad_max": 0,
    }
    return encontrados, metricas


def puntos_plano_z(n, valor):
    """puntos del plano z"""
    puntos = []

    for x in range(1, n + 1):
        for y in range(1, n + 1):
            puntos.append((valor, x, y))

    return puntos


def puntos_plano_x(n, valor):
    """puntos del plano x"""
    puntos = []

    for z in range(1, n + 1):
        for y in range(1, n + 1):
            puntos.append((z, valor, y))

    return puntos


def puntos_plano_y(n, valor):
    """puntos del plano y"""
    puntos = []

    for z in range(1, n + 1):
        for x in range(1, n + 1):
            puntos.append((z, x, valor))

    return puntos


PLANOS = {
    "z": puntos_plano_z,
    "x": puntos_plano_x,
    "y": puntos_plano_y,
}


def sonar_plano(cubo, eje, valor):
    """detecta naves en un plano"""
    if not isinstance(eje, str):
        raise ValueError("El eje debe ser z, x o y.")

    eje = eje.strip().lower()
    if eje not in PLANOS:
        raise ValueError("El eje debe ser z, x o y.")

    n = len(cubo)
    if type(valor) != int:
        raise ValueError("El valor del plano debe ser un numero entero.")
    if valor < 1 or valor > n:
        raise ValueError(f"El valor del plano debe estar entre 1 y {n}.")

    funcion_plano = PLANOS[eje]
    puntos = funcion_plano(n, valor)
    contactos = []

    for punto in puntos:
        estado = leer_celda(cubo, punto)

        if estado in (NAVE, DETECTADO, IMPACTO, HUNDIDO):
            contactos.append(punto)

        if estado == NAVE:
            escribir_celda(cubo, punto, DETECTADO)

    return cubo, contactos


# Entrega 3: busqueda recursiva

def buscar_nave_recursiva(cubo, estado_buscado=NAVE):
    """Busca un estado recursivamente. Devuelve los puntos y sus metricas."""
    inicio = time.perf_counter()
    encontrados = []
    n = len(cubo)

    def recorrer(z, profundidad):
        if z > n:
            return 0, profundidad - 1

        comparaciones = 0
        for x in range(1, n + 1):
            for y in range(1, n + 1):
                comparaciones = comparaciones + 1
                punto = (z, x, y)
                if leer_celda(cubo, punto) == estado_buscado:
                    encontrados.append(punto)

        siguientes, profundidad_max = recorrer(z + 1, profundidad + 1)
        return comparaciones + siguientes, profundidad_max

    comparaciones, profundidad_max = recorrer(1, 1)
    fin = time.perf_counter()
    metricas = {
        "comparaciones": comparaciones,
        "tiempo_ms": (fin - inicio) * 1000,
        "profundidad_max": profundidad_max,
    }
    return encontrados, metricas


# Recorridos: los tres devuelven una lista de puntos del cubo.

def recorrido_capas(cubo):
    """Recorre el cubo de manera tradicional, capa por capa."""
    n = len(cubo)
    puntos = []
    for z in range(1, n + 1):
        puntos.extend(puntos_plano_z(n, z))
    return puntos


def recorrido_capas_recursivo(cubo):
    """Recorre todas las capas usando recursion."""
    n = len(cubo)
    puntos = []

    def recorrer(z):
        if z > n:
            return
        puntos.extend(puntos_plano_z(n, z))
        recorrer(z + 1)

    recorrer(1)
    return puntos


def recorrido_octantes(cubo):
    """Divide el cubo en partes y las recorre recursivamente."""
    n = len(cubo)
    puntos = []

    def recorrer(z1, z2, x1, x2, y1, y2):
        if z1 > z2 or x1 > x2 or y1 > y2:
            return

        if z1 == z2 and x1 == x2 and y1 == y2:
            puntos.append((z1, x1, y1))
            return

        mitad_z = (z1 + z2) // 2
        mitad_x = (x1 + x2) // 2
        mitad_y = (y1 + y2) // 2

        for desde_z, hasta_z in ((z1, mitad_z), (mitad_z + 1, z2)):
            for desde_x, hasta_x in ((x1, mitad_x), (mitad_x + 1, x2)):
                for desde_y, hasta_y in ((y1, mitad_y), (mitad_y + 1, y2)):
                    recorrer(desde_z, hasta_z, desde_x, hasta_x, desde_y, hasta_y)

    recorrer(1, n, 1, n, 1, n)
    return puntos


RECORRIDOS = {
    "capas": recorrido_capas,
    "capas_recursivo": recorrido_capas_recursivo,
    "octantes": recorrido_octantes,
}


def recorrer_cubo(cubo, recorrido="capas"):
    """Devuelve los puntos en el orden elegido, o lanza ValueError."""
    if recorrido not in RECORRIDOS:
        raise ValueError("Recorrido no valido.")
    return RECORRIDOS[recorrido](cubo)


# Mapa de probabilidad

def mapa_probabilidad(cubo):
    """Devuelve una matriz 3D de puntajes a partir de celdas conocidas.

    AGUA representa una celda sin explorar. Se puntuan los posibles
    tramos rectos de 2 a 5 celdas que no contienen agua marcada,
    celdas hundidas ni posiciones descartadas. Los impactos conocidos
    favorecen los tramos compatibles. No se lee una flota oculta.
    """
    n = len(cubo)
    mapa = []
    for z in range(n):
        capa = []
        for x in range(n):
            capa.append([0] * n)
        mapa.append(capa)

    direcciones = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    for largo in range(2, min(5, n) + 1):
        for dz, dx, dy in direcciones:
            for z in range(1, n + 1):
                for x in range(1, n + 1):
                    for y in range(1, n + 1):
                        final = (z + dz * (largo - 1),
                                 x + dx * (largo - 1),
                                 y + dy * (largo - 1))
                        if max(final) > n:
                            continue

                        tramo = []
                        valido = True
                        impactos = 0
                        for i in range(largo):
                            punto = (z + dz * i, x + dx * i, y + dy * i)
                            estado = leer_celda(cubo, punto)
                            # NAVE representa informacion oculta: no se usa.
                            if estado == AGUA_MARCADA or estado == HUNDIDO:
                                valido = False
                                break
                            if estado == IMPACTO or estado == DETECTADO:
                                impactos = impactos + 1
                            tramo.append(punto)

                        if valido:
                            for punto in tramo:
                                estado = leer_celda(cubo, punto)
                                if estado == AGUA or estado == NAVE:
                                    z1, x1, y1 = punto
                                    mapa[z1 - 1][x1 - 1][y1 - 1] += 1 + impactos

    return mapa


def mejores_puntos(mapa, cantidad=1):
    """Devuelve los puntos con mayor puntaje, sin incluir ceros."""
    if type(cantidad) != int or cantidad < 1:
        raise ValueError("La cantidad debe ser un entero positivo.")

    opciones = []
    n = len(mapa)
    for z in range(n):
        for x in range(n):
            for y in range(n):
                valor = mapa[z][x][y]
                if valor > 0:
                    opciones.append(((z + 1, x + 1, y + 1), valor))

    opciones.sort(key=lambda elemento: (-elemento[1], elemento[0]))
    return opciones[:cantidad]
