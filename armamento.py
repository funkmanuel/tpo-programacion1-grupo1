"""Catalogo de armas y torpedo para la entrega 1."""

import tablero


# None indica que la municion del torpedo es ilimitada.
CATALOGO_ARMAS = {
    "T": {"nombre": "torpedo", "municion": None},
    "R": {"nombre": "misil de racimo", "municion": 3},
    "C": {"nombre": "carga de profundidad", "municion": 2},
    "S": {"nombre": "sonar", "municion": 4},
    "L": {"nombre": "barrido laser", "municion": 2},
    "O": {"nombre": "onda expansiva", "municion": 1},
    "G": {"nombre": "torpedo guiado", "municion": 1},
}


def torpedo(cubo, punto):
    """Recibe un cubo y un punto (z, x, y) y modifica la celda apuntada.

    Devuelve el cubo y el resultado: agua, impacto o repetido.
    Si el punto o el estado de la celda es invalido, devuelve None.
    """
    if not isinstance(punto, (tuple, list)):
        return None

    if len(punto) != 3:
        return None

    for coordenada in punto:
        if type(coordenada) != int:
            return None

    n = tablero.tamanio(cubo)
    if not tablero.punto_valido(punto, n):
        return None

    estado = tablero.leer_celda(cubo, punto)

    if estado == tablero.AGUA:
        tablero.escribir_celda(cubo, punto, tablero.AGUA_MARCADA)
        resultado = "agua"
    elif estado == tablero.NAVE or estado == tablero.DETECTADO:
        tablero.escribir_celda(cubo, punto, tablero.IMPACTO)
        resultado = "impacto"
    elif estado in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
        resultado = "repetido"
    else:
        return None

    return cubo, resultado


ARMAS_DISPONIBLES = {"T": torpedo}


def disparar(cubo, arma, punto):
    """Recibe un cubo, la letra del arma y el punto al que se dispara.

    Devuelve el cubo y el resultado del disparo, o None si el arma
    no esta disponible o el punto es invalido.
    """
    if not isinstance(arma, str):
        return None

    arma = arma.strip().upper()
    if arma not in ARMAS_DISPONIBLES:
        return None

    funcion_arma = ARMAS_DISPONIBLES[arma]
    return funcion_arma(cubo, punto)
