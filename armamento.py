"""Catalogo de armas y disparos para la Entrega 2."""

import tablero

class ArmamentoError(Exception):
    """Clase base para errores de armamento."""
    pass

class PuntoInvalidoError(ArmamentoError):
    """Excepcion para puntos con formato incorrecto."""
    pass

class ArmaInvalidaError(ArmamentoError):
    """Excepcion para armas que no existen en el catálogo."""
    pass

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


def inventario_inicial():
    """Devuelve un diccionario con la munición inicial de cada arma."""
    inventario = {}
    for letra, datos in CATALOGO_ARMAS.items():
        inventario[letra] = datos["municion"]
    return inventario


def validar_formato_punto(punto):
    """Recibe un punto y levanta una excepcion si no es una tupla o lista de 3 enteros."""
    if not isinstance(punto, (tuple, list)):
        raise PuntoInvalidoError("El punto debe ser una tupla o lista.")
    if len(punto) != 3:
        raise PuntoInvalidoError("El punto debe tener exactamente 3 coordenadas.")
    for coordenada in punto:
        if type(coordenada) != int:
            raise PuntoInvalidoError("Las coordenadas deben ser numeros enteros.")


def afectar_celda(cubo, punto):
    """Recibe un cubo y un punto. Modifica la celda y devuelve el resultado."""
    n = tablero.tamanio(cubo)
    if not tablero.punto_valido(punto, n):
        return "fuera_de_rango"
    
    estado = tablero.leer_celda(cubo, punto)

    if estado == tablero.AGUA:
        tablero.escribir_celda(cubo, punto, tablero.AGUA_MARCADA)
        return "agua"
    elif estado == tablero.NAVE or estado == tablero.DETECTADO:
        tablero.escribir_celda(cubo, punto, tablero.IMPACTO)
        return "impacto"
    elif estado in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
        return "repetido"
    
    return "error"


def torpedo(cubo, punto, eje=None):
    """Afecta unicamente la celda apuntada. Devuelve el cubo y un diccionario de resultados."""
    validar_formato_punto(punto)
    resultado = afectar_celda(cubo, punto)
    return cubo, {punto: resultado}


def misil_racimo(cubo, punto, eje=None):
    """Afecta la celda apuntada y sus seis vecinas. Devuelve el cubo y los resultados."""
    validar_formato_punto(punto)
    z, x, y = punto
    
    puntos_objetivo = [
        punto,
        (z + 1, x, y), (z - 1, x, y),
        (z, x + 1, y), (z, x - 1, y),
        (z, x, y + 1), (z, x, y - 1)
    ]
    
    resultados = {}
    for p in puntos_objetivo:
        res = afectar_celda(cubo, p)
        if res != "fuera_de_rango":
            resultados[p] = res
            
    return cubo, resultados


def carga_profundidad(cubo, punto, eje=None):
    """Afecta toda la recta sobre el eje z. Devuelve el cubo y los resultados."""
    validar_formato_punto(punto)
    _, x, y = punto
    n = tablero.tamanio(cubo)
    
    resultados = {}
    for z_actual in range(1, n + 1):
        p = (z_actual, x, y)
        resultados[p] = afectar_celda(cubo, p)
        
    return cubo, resultados


def barrido_laser(cubo, punto, eje='x'):
    """Afecta una recta completa sobre x o y. Devuelve el cubo y los resultados."""
    validar_formato_punto(punto)
    z, x, y = punto
    n = tablero.tamanio(cubo)
    
    resultados = {}
    if eje == 'x':
        for x_actual in range(1, n + 1):
            p = (z, x_actual, y)
            resultados[p] = afectar_celda(cubo, p)
    elif eje == 'y':
        for y_actual in range(1, n + 1):
            p = (z, x, y_actual)
            resultados[p] = afectar_celda(cubo, p)
    else:
        raise ArmamentoError("El eje del barrido laser debe ser 'x' o 'y'.")
        
    return cubo, resultados


ARMAS_DISPONIBLES = {
    "T": torpedo,
    "R": misil_racimo,
    "C": carga_profundidad,
    "L": barrido_laser
}


def disparar(cubo, arma, punto, eje='x'):
    """Recibe cubo, arma, punto y eje. Despacha la función del arma y devuelve los resultados."""
    if not isinstance(arma, str):
        raise ArmaInvalidaError("El codigo del arma debe ser texto.")

    arma = arma.strip().upper()
    if arma not in ARMAS_DISPONIBLES:
        raise ArmaInvalidaError(f"El arma '{arma}' no esta disponible o no existe.")

    funcion_arma = ARMAS_DISPONIBLES[arma]
    return funcion_arma(cubo, punto, eje=eje)