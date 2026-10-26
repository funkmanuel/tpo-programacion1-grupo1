"""Busquedas y sonar (entrega 2)."""


import time

from tablero import leer_celda, escribir_celda, NAVE, IMPACTO, HUNDIDO, DETECTADO


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
