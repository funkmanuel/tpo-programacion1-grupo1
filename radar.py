
import time

from tablero import leer_celda, NAVE


def buscar_nave_lineal(cubo, estado_buscado=NAVE):
    """Recibe un cubo y el estado a buscar (NAVE por defecto).

    Devuelve una lista de puntos (z, x, y) y un diccionario de métricas
    con comparaciones, tiempo_ms y profundidad_max. No modifica el cubo.
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
        "profundidad_max": 3,
    }
    return encontrados, metricas
