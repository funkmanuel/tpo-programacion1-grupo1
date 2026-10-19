"""Busquedas de naves y sonar por planos para la entrega 2."""

import time

from tablero import leer_celda, escribir_celda, NAVE, IMPACTO, HUNDIDO, DETECTADO


def buscar_nave_lineal(cubo, estado_buscado=NAVE):
    """Recibe un cubo y el estado a buscar (NAVE por defecto).

    Devuelve una lista de puntos (z, x, y) y un diccionario de metricas
    con comparaciones, tiempo_ms y profundidad_max. No modifica el cubo.
    La profundidad es 0 porque la busqueda no es recursiva.
    """
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
    """Recibe el cubo y su flota completa, con las celdas de cada nave.

    Devuelve los puntos encontrados y las mismas metricas que la busqueda lineal.
    No modifica los datos. La flota debe corresponder al cubo recibido.

    Revisa solo las celdas de las naves: con la flota completa son 35,
    mientras que un cubo de 8 tiene 512 celdas. Usa el estado actual del cubo
    para distinguir naves ocultas, detectadas, impactos y hundimientos.
    Para buscar agua u otros estados utiliza la busqueda lineal.
    """
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
    """Recibe N y un valor de z validos; devuelve los puntos de ese plano."""
    puntos = []

    for x in range(1, n + 1):
        for y in range(1, n + 1):
            puntos.append((valor, x, y))

    return puntos


def puntos_plano_x(n, valor):
    """Recibe N y un valor de x validos; devuelve los puntos de ese plano."""
    puntos = []

    for z in range(1, n + 1):
        for y in range(1, n + 1):
            puntos.append((z, valor, y))

    return puntos


def puntos_plano_y(n, valor):
    """Recibe N y un valor de y validos; devuelve los puntos de ese plano."""
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
    """Recibe un cubo, un eje (z/x/y) y el valor entero del plano entre 1 y N.

    Devuelve el mismo cubo y una lista de las celdas ocupadas de ese plano.
    Marca las naves ocultas como DETECTADO, sin causar impactos. Las celdas
    ya detectadas, impactadas o hundidas tambien son contactos y conservan
    su estado. El agua y las celdas fuera del plano no se modifican.

    Lanza ValueError si el eje o el valor del plano son invalidos.
    """
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
